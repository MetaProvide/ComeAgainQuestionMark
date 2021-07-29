import sys, os
import wave, math, contextlib
import speech_recognition as sr
from alive_progress import alive_bar
from moviepy.editor import AudioFileClip

VIDEO_FILE_DIR = "VideoInput"
TEXT_FILE_DIR = "TextOutput"
AUDIO_FILE_DIR = "ConvertedAudio"
CHUNK_SIZE = 60
TEXT_SEPERATOR = "\n"


def convert_video_to_audio(input_file, output_file):
    audioclip = AudioFileClip(input_file)
    audioclip.write_audiofile(output_file)


def convert_audio_to_text(input_file_name, output_file, separator=TEXT_SEPERATOR):
    with contextlib.closing(wave.open(input_file_name, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames/float(rate)

    total_duration = math.ceil(duration / CHUNK_SIZE)

    recognizer = sr.Recognizer()
    
    with alive_bar(total_duration) as bar:
        for i in range(total_duration):
            with sr.AudioFile(input_file_name) as source:
                audio = recognizer.record(source, offset=i*CHUNK_SIZE, duration=CHUNK_SIZE)
            f = open(output_file, "a")
            f.write(recognizer.recognize_google(audio))
            f.write(separator)
            bar()
        f.close()


def app(args):
    try:
        input_video_file_name = os.path.join(VIDEO_FILE_DIR, args[1])
        base, ext = os.path.splitext(args[1])
        audio_file_name = os.path.join(AUDIO_FILE_DIR, base + '.wav')
        output_text_file_name = os.path.join(TEXT_FILE_DIR, args[2])
        print('Paths for processing:')
        print('Input video file: {}'.format(input_video_file_name))
        print('Converted audio file: {}'.format(audio_file_name))
        print('Transcribed text file: {}'.format(output_text_file_name))
        print('-----------------------------------\n')

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

if __name__ == "__main__":
    app(sys.argv)
    
