#!/bin/sh

sudo apt update;
sudo apt upgrade -y;

sudo apt install python3 python3-pip;
sudo apt install chromium-chromedriver;

rm -rf ./data.json

python3 -m venv ./.venv;
source .venv/bin/activate;

pip3 install .;
python3 main.py;

deactivate;

crontab -l | { cat; echo "*/10 * * * * source ~/code/Grade-Checker/.venv/bin/activate && $(which python3) ~/code/Grade-Checker/main.py && deactivate"; } | crontab -