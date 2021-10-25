# Come Again?
Video-To-Text tool for MetaProvide. Useful when you want to read what was said in a video (or audio clip)

## Requirements
- Python3
- Poetry
- FFMPEG

## How to use
1. Clone repo `git clone https://github.com/MetaProvide/ComeAgainQuestionMark.git` or download zip
2. Run command `cd ComeAgainQuestionMark && poetry install` to install dependencies
3. Download a model from [here](https://alphacephei.com/vosk/models) and unzip
4. Run command `poetry run python3 comeAgainQuestionMark -m [PATH-TO-MODEL-FOLDER] -i [PATH-TO-VIDEO-INPUT] -o [PATH-TO-TEXT-OUTPUT]`
5. Open file `[PATH-TO-TEXT-OUTPUT]` to see your results

## Note
Different model yields different transcritions.

## License
This program is licensed under the GPLv3 or later.
