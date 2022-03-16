# import the necessary packages
import threading

import cv2
import imutils
import numpy as np
from netifaces import AF_INET, ifaddresses, interfaces
from networktables import NetworkTables

from CameraStream import WebCamVideoStream
from tracking import Ball_Tracking_NT

# region
serverCondition = threading.Condition() #Establish a Condition
rio_notified = [False]

# Wait for the Pi to establish a connect with the RoboRio so it doesnt pull null
# Do this by establishing a listener that will activate when the server is initialized

# Get Local ip
def getLocalIp():
    for ifaceName in interfaces():
        addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'No IP addr'}] )]
        if(' '.join(addresses) != 'No IP addr' ):
            if not(' '.join(addresses).startswith("127.")): # Local looping Subnet
                return str(' '.join(addresses))

def connectionListener(connected, info):
    print(info, '; Connected=%s' % connected, " local ip: "+ getLocalIp())
    with serverCondition:
        rio_notified[0] = True
        serverCondition.notify()

# Initalise client connection to the RoboRio server
NetworkTables.startClientTeam(540) # Establish user as a Client connection to the RoboRio's server
NetworkTables.initialize(server='10.5.40.2') # RoboRio ip
NetworkTables.addConnectionListener(connectionListener, immediateNotify=True)

# Check if we have initialized a connection to the RoboRio
# If we have, procced, if not then wait till we do
# This is also good because it doesnt allow us to send data to the Rio untill we have a connection (send a packet to Ayush's brain (nothing))

with serverCondition:
    print("Waiting for Server Connection")
    if not rio_notified[0]:
        serverCondition.wait()


# The Server has been Connected to so we can Procced with the Code !! REST OF THE CODE !!
# endregion

# Initalise Pi Values with network tables
talonpi = NetworkTables.getTable('TalonPi')

frame_width = talonpi.getAutoUpdateValue('frame_width',640,True)
frame_width = int(frame_width.value)
allianceColor = talonpi.getAutoUpdateValue('Alliance Color','PIREADY')
allianceColor = allianceColor.value
gamemode = talonpi.getAutoUpdateValue('Gamemode','PIREADY')
gamemode = gamemode.value
debuggingMode = talonpi.getAutoUpdateValue('Debugging',False)

talonpi.getEntry('local_ip').setString(getLocalIp())

# Call camera from thread
stream = WebCamVideoStream(src=0).start()
# stream = cv2.VideoCapture(1)

# Define ball and masking variables
blueLower = (95, 90, 20)
blueUpper = (135, 255, 255)
red1Lower = (165, 90, 20)
red1Upper = (180, 255, 255)
red2Lower = (0, 90, 20)
red2Upper = (15, 255, 255)
ROUNDNESS_THRESH = 10
CENTER_DETECT_THRESH = 60
MIN_RADIUS = 20

# Get raw frames and run ball Detection code
print("Running ball Detection code")
print("Hopefully pushing data to NetworkTables")

while (gamemode.value == "auto") or (debuggingMode.value == True) or (not getLocalIp().startswith('10.5.40.')):
    # Raw feed code -->
    # print(allianceColor.value)
    frame = stream.read()
    frame = imutils.resize(frame, width=frame_width)

    # <-- Ball Detection code -->
    Ball_Tracking_NT(frame=frame, frame_width=frame_width, alliance=allianceColor, table='TalonPi').start()
