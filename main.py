import wave, math, contextlib
import speech_recognition as sr
from moviepy.editor import AudioFileClip

input_video_file_name = "VideoInput/my_video_file.mp4"
output_text_file_name = "TextOutput/my_transcription_file.txt"

converted_audio_file_name = "ConvertedAudio/transcribed_speech.wav"
text_chunk_seperator = "\n"

# Convert video to audio
audioclip = AudioFileClip(input_video_file_name)
audioclip.write_audiofile(converted_audio_file_name)


# Convert audio into text
with contextlib.closing(wave.open(converted_audio_file_name, 'r')) as f:
    frames = f.getnframes()
    rate = f.getframerate()
    duration = frames/float(rate)


total_duration = math.ceil(duration / 60)

recognizer = sr.Recognizer()

for i in range(total_duration):
    with sr.AudioFile(converted_audio_file_name) as source:
        audio = recognizer.record(source, offset=i*60, duration=60)
    f = open(output_text_file_name, "a")
    f.write(recognizer.recognize_google(audio))
    f.write(text_chunk_seperator)
f.close()

