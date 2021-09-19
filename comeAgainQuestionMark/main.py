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
    input_file_name, output_file, model_path, enable_timestamp, timestamp_format
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

    print("Format transcription...")
    progress_count = 0
    progress_total = len(results)
    with progressbar.ProgressBar(widgets=progress_widgets, max_value=10) as bar:
        for i, res in enumerate(results):
            progress_count += 1
            bar.update(progress_count / progress_total)
            jres = json.loads(res)
            if "result" not in jres:
                continue
            words = jres["result"]
            for j in range(0, len(words), WORDS_PER_LINE):
                line = words[j : j + WORDS_PER_LINE]
                s = srt.Subtitle(
                    index=len(subs),
                    content=" ".join([ln["word"] for ln in line]),
                    start=datetime.timedelta(seconds=line[0]["start"]),
                    end=datetime.timedelta(seconds=line[-1]["end"]),
                )
                subs.append(s)

    print("Saving file...")
    of = open(output_file, "a")
    of.write(parse_subs(subs, enable_timestamp, timestamp_format) + "\n")
    of.close()


def generate_timestamp(seconds):
    hour = seconds // 3600
    minute = (seconds - hour * 3600) // 60
    sec = seconds - hour * 3600 - minute * 60
    return "[{:02d}:{:02d}:{:02d}]".format(hour, minute, sec)


def parse_subs(subs, enable_timestamp, timestamp_format):
    if timestamp_format == "srt":
        return srt.compose(subs)
    elif enable_timestamp and timestamp_format == "raw":
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
        "-i", "--input", dest="input_path", help="Specify input video path"
    )
    parser.add_argument(
        "-o", "--output", dest="output_path", help="Specify output text path"
    )
    parser.add_argument(
        "-t",
        "--timestamped",
        dest="enable_timestamp",
        default=True,
        help="Enable timetamping [True|False] (default: True)",
    )
    parser.add_argument(
        "-f",
        "--format",
        dest="output_format",
        default="raw",
        help="Timetamp format: [raw|srt] (default: raw)",
    )

    return parser


def validate_paths(args):
    isValid = True
    if not os.path.exists(args.input_path):
        print("Please specify valid input file path")
        isValid = False

    if not os.path.exists(args.output_path):
        print("Please specify valid output file path")
        isValid = False

    if not os.path.exists(args.model_path):
        print(
            "Please download the model from https://alphacephei.com/vosk/models, unzip and specify it [-m | --model path/to/model ]"
        )
        isValid = False

    return isValid


def app():
    parser = setup_arguments()
    args = parser.parse_args()
    if not validate_paths(args):
        exit(1)

    print(
        "Model: {}\nInput: {}\nOutput: {}\nEnable Timestamp: {}\nFormat: {}".format(
            args.model_path,
            args.input_path,
            args.output_path,
            args.enable_timestamp,
            args.output_format,
        )
    )

    try:
        input_file_name = os.path.abspath(args.input_path)
        base, _ = os.path.splitext(os.path.basename(args.input_path))
        model_file_name = os.path.abspath(args.model_path)
        output_text_file_name = os.path.join(args.output_path)
        print("Transcribing input to text")
        transcribe(
            input_file_name,
            output_text_file_name,
            model_file_name,
            args.enable_timestamp,
            args.output_format,
        )
        print("\nDone - Output file is located at: {}".format(output_text_file_name))

    except (IndexError, RuntimeError, TypeError, NameError) as err:
        print("ERROR: ", err)
        # TODO make better error handling
