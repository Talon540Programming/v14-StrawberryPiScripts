from cscore import CameraServer
from networktables import NetworkTables, NetworkTable
import cv2
import numpy as np
from time import sleep

last_value = 0.8


def main():
    global last_value
    cs = CameraServer.getInstance(_nextPort = 5802)
    # cs._nextPort = 5802
    cs.enableLogging()
    camera = cs.startAutomaticCapture()
    camera.setResolution(320, 240)
    cvSink = cs.getVideo()
    outputStream = cs.putVideo("Name", 320, 240)
    img = np.zeros(shape=(240, 320, 3), dtype=np.uint8)
    # define HoughCircles constants
    ROUNDNESS_THRESH = 30
    CENTER_DETECT_THRESH = 60
    MIN_RADIUS = 20
    # construct the argument parse and parse the arguments
    # define the lower and upper boundaries of the blue or red
    # ball in the HSV color space, then initialize the
    # list of tracked points
    blueLower = (95, 90, 20)
    blueUpper = (135, 255, 255)
    red1Lower = (165, 90, 20)
    red1Upper = (180, 255, 255)
    red2Lower = (0, 90, 20)
    red2Upper = (15, 255, 255)
    # allow the camera or video file to warm up
    sleep(2.0)
    blue = False
    while True:
        time, frame = cvSink.grabFrame(img)
        if time == 0:
            outputStream.notifyError(cvSink.getError())
            continue
        frame = cv2.resize(frame, (1280, 960))
        blurred = cv2.GaussianBlur(frame, (101, 101), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        # construct a mask for red or blue, then perform a series of dilations and erosions to remove any small blobs
        # left in the mask
        if blue:
            mask = cv2.inRange(hsv, blueLower, blueUpper)
        else:
            mask = cv2.inRange(hsv, red1Lower, red1Upper) + cv2.inRange(hsv, red2Lower, red2Upper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        # use Hough Circle Transform to find the roundest object on the screen and trace its perimeter
        circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, 2, 50, param1=ROUNDNESS_THRESH,
                                   param2=CENTER_DETECT_THRESH, minRadius=MIN_RADIUS, maxRadius=0)

        if circles is not None:
            circles = np.uint16(np.around(circles))
            print(circles)
            biggest_circle = circles[[i[0][2] for i in circles].index(max([i[0][2] for i in circles]))]
            center = (biggest_circle[0][0], biggest_circle[0][1])
            # circle center
            cv2.circle(mask, center, 1, (255, 0, 255), 3)
            # circle outline
            radius = biggest_circle[0][2]
            print((center[0] - 640) / 1000)
            turn_percentage = (center[0] - 640) / 1000
            last_value = turn_percentage
            # put turn_percentage to table
            cv2.circle(mask, center, radius, (255, 0, 255), 3)
            cv2.circle(frame, center, 1, (255, 0, 0), 3)
            cv2.circle(frame, center, radius, (0, 0, 255), 3)
        else:
            print(None)
            # put none in table
        # show the frame to our screen
        outputStream.putFrame(mask)


main()
