#!/bin/bash

#First Time Setup for Raspberry Pi

if [ "$(uname)" != "Linux" ]; then
    echo "Linux is Expected OS exit code 1"
    exit 1 #OS is not Linux based
fi

if [[ "$(uname -a)" != *"aarch64"* ]]; then
  echo "It's there."
  exit 1 #OS is not ARM64 based
fi

echo "hi"


# Install Network Tables
pip3 install pynetworktables
#Install OpenCV2
pip3 install opencv-python
