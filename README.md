# ComeAgainQuestionMark
Video-To-Text tool for MetaProvide

## Requirements
- Python3
- Poetry
- FFMPEG

## How to use
1. Clone repo `git clone https://github.com/MetaProvide/ComeAgainQuestionMark.git` or download zip
2. Run command `cd ComeAgainQuestionMark && poetry install` to install dependencies
4. Run command `poetry run python3 comeAgainQuestionMark -m [PATH-TO-MODEL] -i [PATH-TO-VIDEO-INPUT] -o [PATH-TO-TEXT-OUTPUT]`
5. Open file `[PATH-TO-OUTPUT-TEXT]` to see your results

## Quick *old* Demo 
![](assets/demo.gif)

## Note
This script is using Google Speech Recognition Engine in the background.

## License

This program is licensed under the GPLv3 or later.
