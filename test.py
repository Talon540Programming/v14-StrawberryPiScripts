# import the necessary packages
import threading
import time

import cv2
import imutils
import numpy as np
from flask import Flask, Response, render_template
from netifaces import AF_INET, ifaddresses, interfaces
from networktables import NetworkTables

i = 0


serverCondition = threading.Condition() #Establish a Condition
rio_notified = [False]

# Wait for the Pi to establish a connect with the RoboRio so it doesnt pull null
# Do this by establishing a listener that will activate when the server is initialized

def connectionListener(connected, info):
    print(info, '; Connected=%s' % connected)
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


# <-- HERE -->

print("hello world")

talonpi = NetworkTables.getTable('TalonPi')

i=0
while True:
    i = i+1
    talonpi.getEntry('test').setDouble(i)

# class WebCamVideoStream:
#     def __init__(self, src=0):
#         # initialize the video camera stream and read the first frame 
#         # from the stream
#         self.stream = cv2.VideoCapture(src)
#         (self.grabbed, self.frame) = self.stream.read()

#         # initialize the variable used to inidicate if the thread 
#         # should be stopped
#         self.stopped = False

#     def start(self):
#         # start the thread to read frames from the video stream
#         threading.Thread(target=self.update, args=()).start()
#         return self

#     def update(self):
#         # keep looping infinitely until the thread is stopped
#         while True:
#             # if the thread indicator variable is set, stop the thread
#             if self.stopped:
#                 return
#             # otherwise read the next frame from the stream
#             (self.grabbed, self.frame) = self.stream.read()

#     def read(self):
#         # return the frame most recently read
#         return self.frame

#     def stop(self):
#         # indicate that the thread should be stopped
#         self.stopped = True


# blueLower = (95, 90, 20)
# blueUpper = (135, 255, 255)
# red1Lower = (165, 90, 20)
# red1Upper = (180, 255, 255)
# red2Lower = (0, 90, 20)
# red2Upper = (15, 255, 255)
# ROUNDNESS_THRESH = 10
# CENTER_DETECT_THRESH = 60
# MIN_RADIUS = 20

# frame_width = 1280

# stream = WebCamVideoStream(src=0).start()
# i=0

# while True:
#     i += 1
#     print(i)
#     frame = stream.read()
#     frame = imutils.resize(frame, width=frame_width) # resize frame like this # Does height automatically
#     blurred = cv2.GaussianBlur(frame, (101, 101), 0)
#     hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
#     # construct a mask for red or blue, then perform a series of dilations and erosions to remove any small blobs
#     # left in the mask
#     mask = cv2.inRange(hsv, red1Lower, red1Upper) + cv2.inRange(hsv, red2Lower, red2Upper)
#     mask = cv2.erode(mask, None, iterations=2)
#     mask = cv2.dilate(mask, None, iterations=2)
#     # use Hough Circle Transform to find the roundest object on the screen and trace its perimeter
#     circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, 2, 50, param1=ROUNDNESS_THRESH,param2=CENTER_DETECT_THRESH, minRadius=MIN_RADIUS, maxRadius=0)
#     if circles is not None:
#         circles = np.uint16(np.around(circles))
#         biggest_circle = circles[[i[0][2] for i in circles].index(max([i[0][2] for i in circles]))]
#         center = (biggest_circle[0][0], biggest_circle[0][1])
#         talonpi.getEntry('Motor Value').setDouble((frame_width/2)-center[0])
#     # cv2.imshow('frame',frame)
#     # key = cv2.waitKey(1) & 0xFF
#     # # if the 'q' key is pressed, stop the loop
#     # if key == ord("q"):
#     #     break

