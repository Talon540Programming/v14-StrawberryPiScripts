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
# from BallTracking import ballTracking

from tracking import Ball_Tracking
from tracking import Ball_Tracking_NT


frame_width = 640
alliance = "blue"
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


while True:
    # Raw feed code -->
    # print(allianceColor.value)
    frame = stream.read()
    frame = imutils.resize(frame, width=frame_width)

    # <-- Ball Detection code -->
    # ballTracking(frame,frame_width)
    Ball_Tracking(frame=frame,frame_width=frame_width).start()