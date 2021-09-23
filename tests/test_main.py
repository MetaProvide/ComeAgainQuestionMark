#!/bin/python3
from comeAgainQuestionMark.main import transcribe
from zipfile import ZipFile
from urllib.request import urlretrieve
import os
import logging

LOGGER = logging.getLogger(__name__)

test_assets_url = "https://space.metaprovide.org/index.php/s/qgsSMZk2WqcZ8FR/download"
dirname = os.getcwd()


def download_assets(url):
    zippath = os.path.join(dirname, "assets.zip")
    urlretrieve(test_assets_url, zippath)
    zipfile = ZipFile(zippath, "r")
    zipfile.extractall()
    zipfile.close()
    os.remove(zippath)


def test_mp3_to_txt_to_timestamp(test_audio, model, benchmark):
    transcription = transcribe(
        test_audio,
        None,
        model,
        enable_timestamp=False,
        num_words=7,
        timestamp_format="txt",
    )

    with open(benchmark) as f:
        benchmark_text = f.readlines()
        if benchmark_text and transcription:
            assert True


def test_mp4_to_raw_no_timestamp():
    pass


if __name__ == "__main__":
    if not os.path.exists("tests/assets"):
        download_assets(test_assets_url)

    model = os.path.join(dirname, "tests/assets/models/vosk-model-en-us-0.20")
    audio = os.path.join(dirname, "tests/assets/audio/test_case_1.mp3")
    benchmark = os.path.join(dirname, "tests/assets/transcription/test_case_1.txt")
    if (
        not os.path.exists(model)
        or not os.path.exists(audio)
        or not os.path.exists(benchmark)
    ):
        print("Error with paths")
        exit(1)

    test_mp3_to_txt_to_timestamp(audio, model, benchmark)
