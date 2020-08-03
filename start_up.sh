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

echo -n "Enter time scheme of grade-checker cronjob (minute hour day month weakday): "
read timescheme

crontab -l | { cat; echo "$timescheme cd $PWD && $(which python3) $PWD/main.py"; } | crontab -