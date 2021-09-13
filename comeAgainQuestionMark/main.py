#! /usr/bin/env python3
import os
import wave
import math
import contextlib
import subprocess
import argparse
import json
import speech_recognition as sr
from vosk import Model, KaldiRecognizer, SetLogLevel
from pathlib import Path
from alive_progress import alive_bar
from moviepy.editor import AudioFileClip

PROJ_ROOT_DIR = Path(__file__).parent.parent
CHUNK_SIZE = 10
TEXT_SEPERATOR = "\n"
SAMPLE_RATE = 16000


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


def generate_timestamp(seconds):
    hour = seconds // 3600
    minute = (seconds - hour * 3600) // 60
    sec = seconds - hour * 3600 - minute * 60
    return "[{:02d}:{:02d}:{:02d}]".format(hour, minute, sec)


def transcribe(input_file_name, output_file, model_path, separator=TEXT_SEPERATOR):
    process = get_data_from(input_file_name)

    model = Model(model_path)
    recognizer = KaldiRecognizer(model, SAMPLE_RATE)
    of = open(output_file, "a")

    old_partial = ""
    while True:
        data = process.stdout.read(4000)
        if len(data) == 0:
            break
        if recognizer.AcceptWaveform(data):
            text_chunk = json.loads(recognizer.Result())["text"]
            of.write(text_chunk + "\n")
        else:
            current_partial = json.loads(recognizer.PartialResult())["partial"]
            print(current_partial[len(old_partial) :], end="")
            old_partial = current_partial

    text_chunk = json.loads(recognizer.Result())["text"]
    of.write(text_chunk + "\n")
    of.close()


def app():
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

    args = parser.parse_args()

    if not os.path.exists(args.model_path):
        print(
            "Please download the model from https://alphacephei.com/vosk/models, unzip and specify it [-m | --model path/to/model ]"
        )
        exit(1)

    print(
        "model: {}, input: {}, output: {}".format(
            args.model_path, args.input_path, args.output_path
        )
    )

    try:
        input_file_name = os.path.abspath(args.input_path)
        base, _ = os.path.splitext(os.path.basename(args.input_path))
        model_file_name = os.path.abspath(args.model_path)
        output_text_file_name = os.path.join(args.output_path)
        print("Paths for processing:")
        print("Input file: {}".format(input_file_name))
        # print("Converted audio file: {}".format(audio_file_name))
        print("Transcribed text file: {}".format(output_text_file_name))
        print("-----------------------------------\n")
        print("START: transcribe input to text")
        transcribe(input_file_name, output_text_file_name, model_file_name)
        print("DONE: Output file is located at: {}".format(output_text_file_name))

    except (IndexError, RuntimeError, TypeError, NameError) as err:
        print("ERROR: ", err)
        # TODO make better error handling
