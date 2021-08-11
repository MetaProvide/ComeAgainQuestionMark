#! /usr/bin/env python3
import os
import wave
import math
import contextlib
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
                        results.append(recognizer.Result())
                    bar()

                results.append(recognizer.FinalResult())

                print(results)
                
                for i, res in enumerate(results):
                    words = json.loads(res).get('text')
                    if not words:
                        continue
                    timestamp = generate_timestamp(words[0]['start'])
                    content = ' '.join([w['word'] for w in words])
                    print(
                      timestamp + ": " + content
                      )

                    f.write(
                      timestamp + ": " + content
                    )

        f.close()


def app(args):
    try:
        input_video_file_name = os.path.join(args[1])
        base, _ = os.path.splitext(os.path.basename(args[1]))
        audio_file_name = os.path.join(AUDIO_PATH, base + ".wav")
        output_text_file_name = os.path.join(args[2])
        print("Paths for processing:")
        print("Input video file: {}".format(input_video_file_name))
        print("Converted audio file: {}".format(audio_file_name))
        print("Transcribed text file: {}".format(output_text_file_name))
        print("-----------------------------------\n")

        print("START: convert video to audio")
        convert_video_to_audio(input_video_file_name, audio_file_name)
        print("DONE: convert video to audio\n")

        print("START: convert audio to text")
        convert_audio_to_text(audio_file_name, output_text_file_name)
        print("DONE: convert audio to text.")
        print("Output file is located at: {}".format(output_text_file_name))

    except (IndexError, RuntimeError, TypeError, NameError) as err:
        print("ERROR: ", err)
        # TODO make better error handling
