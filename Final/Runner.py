# import the necessary packages
import threading
import time

import cv2
import imutils
import numpy as np
from netifaces import AF_INET, ifaddresses, interfaces
from networktables import NetworkTables

from CameraStream import WebCamVideoStream
from tracking import Ball_Tracking, Ball_Tracking_NT

# from BallTracking import ballTracking



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
