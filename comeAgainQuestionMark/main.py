#! /usr/bin/env python3
import os
import wave
import math
import contextlib
import argparse
import json
import speech_recognition as sr
from vosk import Model, KaldiRecognizer, SetLogLevel
from pathlib import Path
from alive_progress import alive_bar
from moviepy.editor import AudioFileClip

PROJ_ROOT_DIR = Path(__file__).parent.parent
ASSETS_PATH = os.path.join(PROJ_ROOT_DIR, "assets")
AUDIO_PATH = os.path.join(ASSETS_PATH, "audio")
CHUNK_SIZE = 10
TEXT_SEPERATOR = "\n"
SAMPLE_RATE = 160000
MODEL_PATH = os.path.join(ASSETS_PATH, "models")


if not os.path.exists(MODEL_PATH):
    print ("Please download the model from https://alphacephei.com/vosk/models and unpack in 'models' in {}.".format(MODEL_PATH))
    exit (1)


def generate_timestamp(seconds):
    hour = seconds // 3600
    minute = (seconds - hour * 3600) // 60
    sec = seconds - hour * 3600 - minute * 60
    return "[{:02d}:{:02d}:{:02d}]".format(hour, minute, sec)


def convert_video_to_audio(input_file, output_file):
    audioclip = AudioFileClip(input_file)
    audioclip.write_audiofile(output_file)


def convert_audio_to_text(input_file_name, output_file, separator=TEXT_SEPERATOR):
    with contextlib.closing(wave.open(input_file_name, "r")) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames // rate

        # TODO fix bars()
        total_duration = math.ceil(duration / CHUNK_SIZE)
        model = Model(os.path.join(MODEL_PATH, "vosk-model-en-us-daanzu-20200905-lgraph"))
        recognizer = KaldiRecognizer(model, SAMPLE_RATE)

        with alive_bar(total_duration) as bar:
            with wave.open(input_file_name, "rb") as source:
                results = []
                while True:
                    data = source.readframes(4000)
                    if len(data) == 0:
                        break
                    if recognizer.AcceptWaveform(data):
                        json_data = recognizer.Result()
                        text = json.loads(json_data)['text']
                        results.append(text)
                        print(results)
                    bar()

                # results.append(recognizer.FinalResult())

                of = open(output_file, "a")
                for i, line in enumerate(results):
                    of.write(str(i) + " " + line + '\n') 
                of.close();
        f.close()


def app():
    parser = argparse.ArgumentParser()

    parser.add_argument("-m", "--model", dest = "model_path", default = "model", help="Specify model Path for Vosk. Get model from https://alphacephei.com/vosk.models and specify path")
    parser.add_argument("-i", "--input", dest = "input_path", help="Specify input video path")
    parser.add_argument("-o", "--output",dest = "output_path", help="Specify output text path")

    args = parser.parse_args()
    print("model: {}, input: {}, output: {}".format(args.model_path, args.input_path, args.output_path))
    
    try:
        input_video_file_name = os.path.abspath(args.input_path)
        base, _ = os.path.splitext(os.path.basename(args.input_path))
        audio_file_name = os.path.join(AUDIO_PATH, base + ".wav")
        model_file_name = os.path.abspath(args.model_path)
        output_text_file_name = os.path.join(args.output_path)
        print("Paths for processing:")
        print("Input video file: {}".format(input_video_file_name))
        print("Converted audio file: {}".format(audio_file_name))
        print("Transcribed text file: {}".format(output_text_file_name))
        print("-----------------------------------\n")

        print("START: convert video to audio")
        convert_video_to_audio(input_video_file_name, audio_file_name)
        print("DONE: convert video to audio\n")

        print("START: convert audio to text")
        convert_audio_to_text(audio_file_name, output_text_file_name, model_file_name)
        print("DONE: convert audio to text.")
        print("Output file is located at: {}".format(output_text_file_name))

    except (IndexError, RuntimeError, TypeError, NameError) as err:
        print("ERROR: ", err)
        # TODO make better error handling
