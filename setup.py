# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['comeagainquestionmark']

package_data = \
{'': ['*']}

install_requires = \
['Pillow==8.3.1',
 'SpeechRecognition==3.8.1',
 'Wave==0.0.2',
 'alive-progress==1.6.2',
 'autopep8>=1.5.7,<2.0.0',
 'black>=21.7b0,<22.0',
 'certifi==2021.5.30',
 'charset-normalizer==2.0.3',
 'decorator==4.4.2',
 'idna==3.2',
 'imageio-ffmpeg==0.4.4',
 'imageio==2.9.0',
 'moviepy==1.0.3',
 'numpy==1.21.1',
 'proglog==0.1.9',
 'progress==1.6',
 'requests==2.26.0',
 'tqdm==4.61.2',
 'urllib3==1.26.6']

setup_kwargs = {
    'name': 'comeagainquestionmark',
    'version': '0.1.0',
    'description': 'Transcription tool for video to text',
    'long_description': None,
    'author': 'Henry Bergström',
    'author_email': 'henrybergstrom@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
