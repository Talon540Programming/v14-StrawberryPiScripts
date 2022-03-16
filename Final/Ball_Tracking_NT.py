# import the necessary packages
import threading

import cv2
import imutils
import numpy as np
from netifaces import AF_INET, ifaddresses, interfaces
from networktables import NetworkTables

from CameraStream import WebCamVideoStream
from tracking import Ball_Tracking

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

frame_width = int(talonpi.getAutoUpdateValue('frame_width',640,True).value)
frame_height = int(talonpi.getAutoUpdateValue('frame_height',360,True).value)
gamemode = talonpi.getAutoUpdateValue('Gamemode','PIREADY',True).value
debuggingMode = talonpi.getAutoUpdateValue('Debugging Mode?',False,True).value
allianceColor = talonpi.getAutoUpdateValue('Alliance Color',"blue",True).value



talonpi.getEntry('local_ip').setString(getLocalIp())


# Call camera from thread
stream = WebCamVideoStream(src=0).start()

while True:
    # Raw feed code -->
    # print(allianceColor.value)
    frame = stream.read()
    frame = imutils.resize(frame, width=frame_width,height=frame_height)

    # <-- Ball Detection code -->
    Ball_Tracking(frame=frame,frame_width=frame_width,alliance=allianceColor).start()