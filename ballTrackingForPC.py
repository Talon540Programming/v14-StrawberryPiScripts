# import the necessary packages
import numpy as np
import cv2
import time
import threading
# define HoughCircles constants
ROUNDNESS_THRESH = 10
CENTER_DETECT_THRESH = 60
MIN_RADIUS = 20
# construct the argument parse and parse the arguments]

class WebCamVideoStream:
    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        threading.Thread(target=self.update, args=()).start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return
            # otherwise read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True


vs = WebCamVideoStream(src=0).start()
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
time.sleep(2.0)
blue = False
# keep looping
last_value = 0.8
while True:
    # grab the current frame
    frame = vs.read()
    # resize the frame, blur it, and convert it to the HSV

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
        print((center[0] - 640) / 8000)

        cv2.circle(mask, center, radius, (255, 0, 255), 3)
        cv2.circle(frame, center, 1, (255, 0, 0), 3)
        cv2.circle(frame, center, radius, (0, 0, 255), 3)
    else:
        print(None)
    # show the frames to our screen
    cv2.imshow("Frame", frame)
    cv2.imshow('Mask', mask)
    key = cv2.waitKey(1) & 0xFF
    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break
# stop camera
vs.release()
# close all windows
cv2.destroyAllWindows()
