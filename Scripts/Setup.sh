#!/bin/bash

#Make sure to configure all settings in sudo raspi-config first

echo checking OS
if [ "$(uname)" != "Linux" ]; then
    echo "Linux is Expected OS exit code 1"
    exit 1 #OS is not Linux based
fi

if [[ "$(uname -a)" != *"aarch64"* ]]; then
  echo "aarch64 based OS is Expected OS exit code 1"
  exit 1 #OS is not aarch64 based
fi

echo checking Network
ping -c 1 1.1.1.1
status=$?
if [ $status != 0 ]; then
    echo "No Network Connection; Check wifi or Ethernet connection"
    echo "Also make sure you are not on the RobotNetwork"
    exit 1 #no network
fi

echo Updating Packages
sudo apt update && sudo apt upgrade
echo Installing required packages
sudo apt install python3-pip git curl dpkg debian-archive-keyring
echo Installing required pip modules
#Install NetworkTables, OpenCV2 and its dependencies
/usr/bin/pip3 install opencv-python numpy pynetworktables flask netifaces



