#!/bin/bash
sudo apt-get install python3-venv
python3 -m venv venv
. venv/bin/activate
pip install -r ./requirements.txt 
export FLASK_APP=app.py 
flask run
