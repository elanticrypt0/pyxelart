#!/bin/bash

uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
uv pip install opencv-python
uv pip install imageio
uv pip install tqdm
sudo apt install ffmpeg