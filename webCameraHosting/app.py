# import the necessary packages
import numpy as np
import cv2
import time
import imutils
from flask import Flask, render_template, Response
from netifaces import interfaces, ifaddresses, AF_INET
from threading import Thread

# Get the local IP address for the Device
# Might throw BS if on a mac. Dont cry

for ifaceName in interfaces():
    addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'No IP addr'}] )]
    if(' '.join(addresses) != 'No IP addr' ):
        if not(' '.join(addresses).startswith("127.")):
            local_ip = ' '.join(addresses)

app = Flask(__name__)

import argparse
parser = argparse.ArgumentParser(description='Choose Color')
parser.add_argument("-c", help="Pick Ball Color") #For testing
args = parser.parse_args()

# define HoughCircles constants
ROUNDNESS_THRESH = 10
CENTER_DETECT_THRESH = 60
MIN_RADIUS = 20
# construct the argument parse and parse the arguments

class WebCamVideoStream:
    def __init__(self, src=0):
        # initialize the video camera stream and read the first frame 
        # from the stream
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()

        # initialize the variable used to inidicate if the thread 
        # should be stopped
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        Thread(target=self.update, args=()).start()
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


stream = WebCamVideoStream(src=0).start()
# stream = cv2.VideoCapture(1)

blueLower = (95, 90, 20)
blueUpper = (135, 255, 255)
red1Lower = (165, 90, 20)
red1Upper = (180, 255, 255)
red2Lower = (0, 90, 20)
red2Upper = (15, 255, 255)
ROUNDNESS_THRESH = 10
CENTER_DETECT_THRESH = 60
MIN_RADIUS = 20

def ballDetection(frame):
    # resize the frame, blur it, and convert it to the HSV
    blurred = cv2.GaussianBlur(frame, (101, 101), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    # construct a mask for red or blue, then perform a series of dilations and erosions to remove any small blobs
    # left in the mask
    mask = cv2.inRange(hsv, red1Lower, red1Upper) + cv2.inRange(hsv, red2Lower, red2Upper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    # use Hough Circle Transform to find the roundest object on the screen and trace its perimeter
    circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, 2, 50, param1=ROUNDNESS_THRESH,param2=CENTER_DETECT_THRESH, minRadius=MIN_RADIUS, maxRadius=0)
    if circles is not None:
        circles = np.uint16(np.around(circles))
        biggest_circle = circles[[i[0][2] for i in circles].index(max([i[0][2] for i in circles]))]
        center = (biggest_circle[0][0], biggest_circle[0][1])
        print((center[0] - 640) / 8000)
    else:
        print(None)

# loop over some frames
def gen():
    while True:
        # Raw feed code -->
        frame = stream.read()
        frame = imutils.resize(frame, width=640) # resize frame like this
        ret, buffer = cv2.imencode('.jpg', frame)
        biteBuffer = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + biteBuffer + b'\r\n')

        # Ball detection Code -->
        ballDetection(frame)

@app.route('/raw')
def raw_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/') #Base root
def index():
    """Video streaming home page."""
    return render_template('root.html')
    
if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host=local_ip, debug=True,port="5800",use_reloader=False)