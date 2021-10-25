#!/bin/python3
from come_again_question_mark.main import transcribe
from zipfile import ZipFile
from urllib.request import urlretrieve
import os
import logging
import difflib as dl

LOGGER = logging.getLogger(__name__)

test_assets_url = "https://space.metaprovide.org/index.php/s/qgsSMZk2WqcZ8FR/download"
dirname = os.getcwd()
test_folder_path = os.path.join(dirname, "tests")
test_assets_folder_path = os.path.join(test_folder_path, "assets")


def setup_module(module):
    if not os.path.exists(test_assets_folder_path):
        print("----- Setup Assets ------")
        download_assets(test_assets_url)
        print(os.system(f"tree {test_assets_folder_path}"))


def teardown_module(module):
    print("------ Teardown Done -------")


def download_assets(url):
    zip_path = os.path.join(f"{test_assets_folder_path}.zip")
    print(f"Zipping to {zip_path}")
    urlretrieve(url, zip_path)
    zipfile = ZipFile(zip_path, "r")
    zipfile.extractall(test_folder_path)
    print(f"Extracting zip file to {test_assets_folder_path}")
    zipfile.close()
    os.remove(zip_path)
    print(f"Removing zip file {zip_path}")


def test_mp4_to_txt_no_timestamp():
    model = os.path.join(dirname, "tests/assets/models/vosk-model-en-us-0.20")
    video = os.path.join(dirname, "tests/assets/video/test_case_1.mp4")
    benchmark_transcription = os.path.join(
        dirname, "tests/assets/transcription/test_case_1.txt"
    )
    if not os.path.exists(model):
        print(f"Error with path {model}")
        assert False

    if not os.path.exists(video):
        print(f"Error with path {video}")
        assert False

    if not os.path.exists(benchmark_transcription):
        print(f"Error with path {benchmark_transcription}")
        assert False

    transcription = transcribe(
        video,
        None,
        model,
        enable_timestamp=False,
        num_words=7,
        timestamp_format="txt",
    )

    with open(benchmark_transcription) as f:
        benchmark_text = "".join(f.readlines())
        assert get_similarity_ratio(benchmark_text, transcription) > 0.85


def test_mp3_to_txt_no_timestamp():
    model = os.path.join(dirname, "tests/assets/models/vosk-model-en-us-0.20")
    audio = os.path.join(dirname, "tests/assets/audio/test_case_1.mp3")
    benchmark = os.path.join(dirname, "tests/assets/transcription/test_case_1.txt")
    if not os.path.exists(model):
        print(f"Error with path {model}")
        assert False

    if not os.path.exists(audio):
        print(f"Error with path {audio}")
        assert False

    if not os.path.exists(benchmark):
        print(f"Error with path {benchmark}")
        assert False

    transcription = transcribe(
        audio,
        None,
        model,
        enable_timestamp=False,
        num_words=7,
        timestamp_format="txt",
    )

    with open(benchmark) as f:
        benchmark_text = "".join(f.readlines())
        assert get_similarity_ratio(benchmark_text, transcription) > 0.85


def get_similarity_ratio(benchmark_text, transcription_text):
    compare1 = [word for word in benchmark_text.lower().split(" ") if word]
    compare2 = [
        word
        for word in transcription_text.lower().replace("\n", " ").split(" ")
        if word
    ]

    sequence_matcher = dl.SequenceMatcher()
    sequence_matcher.set_seqs(compare1, compare2)

    simularity_ratio = sequence_matcher.ratio()
    print("Similarity Ratio: ", simularity_ratio)

    for diff in dl.context_diff(compare1, compare2):
        print(diff)

    return simularity_ratio


if __name__ == "__main__":
    if not os.path.exists("tests/assets"):
        download_assets(test_assets_url)

    test_mp4_to_txt_no_timestamp()
    test_mp3_to_txt_no_timestamp()
