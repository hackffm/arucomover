#!/bin/bash

echo check existing folders
if [ ! -d ~/arucodetection ]; then
  echo "create aruco_detection folders"
	mkdir ~/arucodetection
	mkdir ~/arucodetection/data
	mkdir ~/arucodetection/log
	mkdir ~/arucodetection/recording
	echo "prepare config"
  cp config.json ~/arucodetection
  sed -i -e 's/pi/'"${USER}"'/g' ~/arucodetection/config.json
fi

if [ ! -d ~/arucodetection/venv ]; then
  mkdir ~/arucodetection/venv
  echo create python venv
  python3 -m venv ~/arucodetection/venv
  
  echo install python packages
  source ~/arucodetection/venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
fi

if [ ! -d ~/nodered ]; then
  echo create noderedfolder
  mkdir ~/nodered
  cp package.json ~/nodered
  cd ~/nodered
  npm install
fi
