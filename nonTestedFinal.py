# import the necessary packages
from netifaces import interfaces, ifaddresses, AF_INET
import imutils
import threading
import imutils
from networktables import NetworkTables
import numpy as np
import cv2
import time
from flask import Flask, render_template, Response
from netifaces import interfaces, ifaddresses, AF_INET


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


# The Server has been Connected to so we can Procced with the Code !! REST OF THE CODE !!

talonpi = NetworkTables.getTable('TalonPi')
allianceColor = talonpi.getAutoUpdateValue('Alliance Color','PIREADY').value
gamemode = talonpi.getAutoUpdateValue('Gamemode','PIREADY').value
motorValue = talonpi.getAutoUpdateValue('Motor Value','PIREADY').value

# Get Local ip
local_ip = False # Returns False if no local ip is found. Due to pi issues
for ifaceName in interfaces():
    addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'No IP addr'}] )]
    if(' '.join(addresses) != 'No IP addr' ):
        if not(' '.join(addresses).startswith("127.")): # Local looping Subnet
            if (' '.join(addresses).startswith("10.5.40")):
                local_ip = str(' '.join(addresses))

# Initalise flask app
app = Flask(__name__) 

# Use multithreaded Camera server instead of single threaded
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

# Call camera from thread
stream = WebCamVideoStream(src=0).start()

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

# Mask and ballDetection function
def ballDetection(frame):
    # resize the frame, blur it, and convert it to the HSV
    blurred = cv2.GaussianBlur(frame, (101, 101), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    # construct a mask for red or blue, then perform a series of dilations and erosions to remove any small blobs
    # left in the mask
    if allianceColor == "blue":
        mask = cv2.inRange(hsv, blueLower, blueUpper)
    elif allianceColor == "red":
        mask = cv2.inRange(hsv, red1Lower, red1Upper) + cv2.inRange(hsv, red2Lower, red2Upper)
    else:
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

# Get raw frames and run ball Detection code
def gen():
    while True:
        # Raw feed code -->
        frame = stream.read()
        # frame = imutils.resize(frame, width=960) # resize frame like this # Does height automatically
        # Make the frame viewable and easy to send
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
    # Web Server main screen. Rendered as an HTML page
    """Video streaming home page."""
    return render_template('root.html')
    
if __name__ == '__main__':
    # Run the app with Special Attributes: host: pi ip (allows for cross network connection); debug: debug; port: Port to run web server; use_reloader: reload app on wait (False to not overwrite and overload frame capture)
    #app.run(debug=True)
    app.run(host=local_ip, debug=True,port="5800",use_reloader=False)