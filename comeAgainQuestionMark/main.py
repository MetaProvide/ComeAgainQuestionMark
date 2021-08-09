#! /usr/bin/env python3
import os
import wave
import math
import contextlib
import speech_recognition as sr
from pathlib import Path
from alive_progress import alive_bar
from moviepy.editor import AudioFileClip

PROJ_ROOT_DIR = Path(__file__).parent.parent
ASSETS_PATH = os.path.join(PROJ_ROOT_DIR, "assets")
AUDIO_PATH = os.path.join(ASSETS_PATH, "audio")
CHUNK_SIZE = 10
TEXT_SEPERATOR = "\n"


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
        duration = frames / float(rate)

    total_duration = math.ceil(duration / CHUNK_SIZE)

    recognizer = sr.Recognizer()

    with alive_bar(total_duration) as bar:
        for i in range(0, total_duration):
            with sr.AudioFile(input_file_name) as source:
                try:
                    seconds_passed = i * CHUNK_SIZE
                    audio = recognizer.record(
                        source, offset=seconds_passed, duration=CHUNK_SIZE
                    )
                    f = open(output_file, "a")
                    transcribed_chunk = recognizer.recognize_google(audio)
                    f.write(
                        generate_timestamp(seconds_passed) + ": " + transcribed_chunk
                    )
                    f.write(separator)
                except sr.UnknownValueError:
                    print(
                        "[{0}] Google Speech Recognition could not understand audio chunk".format(
                            i
                        )
                    )
                    f.write("------ ")
                except sr.RequestError as e:
                    print(
                        "[{0}] Could not request results from Google Speech Recognition service; {1}".format(
                            i, e
                        )
                    )
            bar()
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
