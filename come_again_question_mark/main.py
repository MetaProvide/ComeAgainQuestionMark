#! /usr/bin/env python3
import os
import datetime
import subprocess
import argparse
import json
import srt
from vosk import Model, KaldiRecognizer, SetLogLevel
from pathlib import Path
import progressbar

PROJ_ROOT_DIR = Path(__file__).parent.parent
CHUNK_SIZE = 10
TEXT_SEPERATOR = "\n"
SAMPLE_RATE = 16000
WORDS_PER_LINE = 7

SetLogLevel(-1)


def get_data_from(input_file_name):
    if input_file_name.lower().endswith((".mp4", ".mov")):
        process = subprocess.Popen(
            [
                "ffmpeg",
                "-loglevel",
                "quiet",
                "-i",
                input_file_name,
                "-ar",
                str(SAMPLE_RATE),
                "-ac",
                "1",
                "-f",
                "s16le",
                "-",
            ],
            stdout=subprocess.PIPE,
        )
    elif input_file_name.lower().endswith((".mp3", ".wav")):
        process = subprocess.Popen(
            [
                "ffmpeg",
                "-loglevel",
                "quiet",
                "-i",
                input_file_name,
                "-ar",
                str(SAMPLE_RATE),
                "-ac",
                "1",
                "-f",
                "wav",
                "-",
            ],
            stdout=subprocess.PIPE,
        )
    else:
        print("Format for {} not supported".format(input_file_name))
        exit(1)
    return process


def transcribe(
    input_file_name,
    output_file,
    model_path,
    enable_timestamp,
    num_words,
    timestamp_format,
):
    process = get_data_from(input_file_name)
    model = Model(model_path)
    recognizer = KaldiRecognizer(model, SAMPLE_RATE)
    recognizer.SetWords(True)  # Not sure why it is needed

    print("Recognizing audio...")
    progress_count = 0
    progress_total = 200  # TODO Find better total
    progress_widgets = [progressbar.Percentage(), progressbar.Bar(marker="■")]
    with progressbar.ProgressBar(widgets=progress_widgets, max_value=10) as bar:
        results = []
        subs = []
        while True:
            data = process.stdout.read(4000)
            progress_count += 1
            bar.update(progress_count / progress_total)
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                results.append(recognizer.Result())
        results.append(recognizer.FinalResult())

    print("Format transcription...", end="")
    progress_count = 0
    progress_total = len(results)
    for i, res in enumerate(results):
        jres = json.loads(res)
        if "result" not in jres:
            continue
        words = jres["result"]
        for j in range(0, len(words), num_words):
            line = words[j : j + num_words]
            s = srt.Subtitle(
                index=len(subs),
                content=" ".join([ln["word"] for ln in line]),
                start=datetime.timedelta(seconds=line[0]["start"]),
                end=datetime.timedelta(seconds=line[-1]["end"]),
            )
            subs.append(s)
    print("Done.")

    transcription = parse_subs(subs, enable_timestamp, timestamp_format) + "\n"
    if output_file:
        print("Saving file...", end="")
        of = open(output_file, "a")
        of.write(transcription)
        of.close()
        print("Done.")
    else:
        return transcription


def generate_timestamp(seconds):
    hour = seconds // 3600
    minute = (seconds - hour * 3600) // 60
    sec = seconds - hour * 3600 - minute * 60
    return "[{:02d}:{:02d}:{:02d}]".format(hour, minute, sec)


def parse_subs(subs, enable_timestamp, timestamp_format):
    if timestamp_format == "srt":
        return srt.compose(subs)
    elif enable_timestamp and timestamp_format == "txt":
        return "".join(
            [
                "{}: {}\n".format(generate_timestamp(ln.start.seconds), ln.content)
                for ln in subs
            ]
        )
    else:
        return "".join(["{}\n".format(ln.content) for ln in subs])


def setup_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-m",
        "--model",
        dest="model_path",
        help="Specify model Path for Vosk. Get model from https://alphacephei.com/vosk.models and specify path",
    )
    parser.add_argument(
        "-i", "--input", dest="input_path", help="Specify input video/audio path"
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output_path",
        default="",
        help="Specify output text path",
    )
    parser.add_argument(
        "-t",
        "--timestamped",
        dest="enable_timestamp",
        default="yes",
        help="Enable timetamping ['true'|'false'] (default: 'true')",
    )
    parser.add_argument(
        "-n",
        "--nwords",
        dest="num_words",
        default=7,
        help="Specify number of words per line in output file",
    )
    parser.add_argument(
        "-f",
        "--format",
        dest="output_format",
        default="txt",
        help="Timetamp format: [txt|srt] (default: txt)",
    )

    return parser


def validate_paths(args):
    isValid = True
    if not os.path.exists(args.input_path):
        print("Please specify valid input file path")
        isValid = False

        print("Please specify valid output file path")
        isValid = False

    if not os.path.exists(args.model_path):
        print(
            "Please download the model from https://alphacephei.com/vosk/models, unzip and specify it [-m | --model path/to/model ]"
        )
        isValid = False

    if int(args.num_words) < 0 or int(args.num_words) > 30:
        print("Please specify valid num_words [-n|--nwords] range (1-30)")
        isValid = False

    return isValid


def app():
    parser = setup_arguments()
    args = parser.parse_args()
    if not validate_paths(args):
        exit(1)

    print(
        "Model: {}\nInput: {}\nOutput: {}\nEnable Timestamp: {}\nNumber of words: {}\nFormat: {}".format(
            args.model_path,
            args.input_path,
            args.output_path,
            args.enable_timestamp,
            args.num_words,
            args.output_format,
        )
    )

    try:
        input_file_name = os.path.abspath(args.input_path)
        base, _ = os.path.splitext(os.path.basename(args.input_path))
        model_file_name = os.path.abspath(args.model_path)
        output_text_file_name = os.path.join(args.output_path)
        if not args.output_path == "":
            output_text_file_name = os.path.join(args.output_path)
        else:
            output_text_file_name = None
        num_words = int(args.num_words)
        enable_timestamp = args.enable_timestamp.lower() in [
            "true",
            "1",
            "t",
            "y",
            "yes",
            "yeah",
        ]
        print("Transcribing input to text")
        print(
            transcribe(
                input_file_name,
                output_text_file_name,
                model_file_name,
                enable_timestamp,
                num_words,
                args.output_format,
            )
        )
        if output_text_file_name:
            print(
                "\nDone - Output file is located at: {}".format(output_text_file_name)
            )

    except (IndexError, RuntimeError, TypeError, NameError) as err:
        print("ERROR: ", err)
        # TODO make better error handling
