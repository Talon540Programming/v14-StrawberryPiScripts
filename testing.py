# import the necessary packages
from netifaces import interfaces, ifaddresses, AF_INET
import imutils
import threading
import imutils
from networktables import NetworkTables
import numpy as np
import cv2
import time
from netifaces import interfaces, ifaddresses, AF_INET
from CameraStream import WebCamVideoStream

# # region
# serverCondition = threading.Condition() #Establish a Condition
# rio_notified = [False]

# # Wait for the Pi to establish a connect with the RoboRio so it doesnt pull null
# # Do this by establishing a listener that will activate when the server is initialized

# # Get Local ip
# def getLocalIp():
#     for ifaceName in interfaces():
#         addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'No IP addr'}] )]
#         if(' '.join(addresses) != 'No IP addr' ):
#             if not(' '.join(addresses).startswith("127.")): # Local looping Subnet
#                 if (' '.join(addresses).startswith("10.5.40")):
#                     return str(' '.join(addresses))

# def connectionListener(connected, info):
#     print(info, '; Connected=%s' % connected, " local ip: "+ getLocalIp())
#     with serverCondition:
#         rio_notified[0] = True
#         serverCondition.notify()

# # Initalise client connection to the RoboRio server
# NetworkTables.startClientTeam(540) # Establish user as a Client connection to the RoboRio's server
# NetworkTables.initialize(server='10.5.40.2') # RoboRio ip
# NetworkTables.addConnectionListener(connectionListener, immediateNotify=True)

# # Check if we have initialized a connection to the RoboRio
# # If we have, procced, if not then wait till we do
# # This is also good because it doesnt allow us to send data to the Rio untill we have a connection (send a packet to Ayush's brain (nothing))

# with serverCondition:
#     print("Waiting for Server Connection")
#     if not rio_notified[0]:
#         serverCondition.wait()


# # The Server has been Connected to so we can Procced with the Code !! REST OF THE CODE !!
# # endregion


frame_width = 640

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
alliance = "blue"
# Get raw frames and run ball Detection code
print("Running ball Detection code")
print("Hopefully pushing data to NetworkTables")

while True:
    # Raw feed code -->
    # print(allianceColor.value)
    frame = stream.read()
    frame = imutils.resize(frame, width=frame_width)

    # <-- Ball Detection code -->

    # resize the frame, blur it, and convert it to the HSV
    blurred = cv2.GaussianBlur(frame, (101, 101), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    # construct a mask for red or blue, then perform a series of dilations and erosions to remove any small blobs
    # left in the mask
    mask = cv2.inRange(hsv, blueLower, blueUpper)
    # Define the currently used color to be checked later and error checked
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    # use Hough Circle Transform to find the roundest object on the screen and trace its perimeter
    circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, 2, 50, param1=ROUNDNESS_THRESH,param2=CENTER_DETECT_THRESH, minRadius=MIN_RADIUS, maxRadius=0)
    if circles is not None:
        circles = np.uint16(np.around(circles))
        biggest_circle = circles[[i[0][2] for i in circles].index(max([i[0][2] for i in circles]))]
        center = (biggest_circle[0][0], biggest_circle[0][1])
        print(((frame_width/2)-center[0]))
    else:
        print("none")
    # show the frames to our screen (debugging)
    # cv2.imshow("Frame", frame)
    # cv2.imshow('Mask', mask)
    # key = cv2.waitKey(1) & 0xFF