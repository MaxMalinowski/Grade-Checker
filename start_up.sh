#!/bin/sh

sudo apt update;
sudo apt upgrade -y;

sudo apt install python3 -y;
sudo apt install python3-pip -y;
sudo apt install chromium-browser -y;
sudo apt install chromium-chromedriver -y;

rm -rf ./data.json
mkdir logs
touch logs/stdout.log
touch logs/stderr.log

pip3 install setuptools;
pip3 install .;
python3 main.py;

crontab -l | { cat; echo "*/10 * * * * cd $PWD && $(which python3) ~/code/Grade-Checker/main.py >$PWD/logs/stdout.log 2>$PWD/logs/stderr.log"; } | crontab -