#!/bin/sh

sudo apt update;
sudo apt upgrade -y;

sudo apt install python3 -y;
sudo apt install python3-pip -y;
sudo apt install chromium-browser -y;

rm -rf ./data.json

pip3 install setuptools;
pip3 install .;
python3 main.py;

crontab -l | { cat; echo "*/10 * * * * $(which python3) ~/code/Grade-Checker/main.py"; } | crontab -