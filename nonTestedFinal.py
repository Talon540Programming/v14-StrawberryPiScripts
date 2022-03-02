# import the necessary packages
import threading
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
NetworkTables.startClientTeam(540)
NetworkTables.initialize(server='10.5.40.2')
NetworkTables.addConnectionListener(connectionListener, immediateNotify=True)

# Check if we have initialized a connection to the RoboRio
# If we have, procced, if not then wait till we do
# This is also good because it doesnt allow us to send data to the Rio untill we have a connection (send a packet to Ayush's brain (nothing))

with serverCondition:
    print("Waiting for Server Connection")
    if not rio_notified[0]:
        serverCondition.wait()


# The Server has been Connected to so we can Procced with the Code

# What needs to be tested:

talonpi = NetworkTables.getTable('TalonPi')
allianceColor = talonpi.getAutoUpdateValue('Alliance Color','PIREADY').value

# Get Local ip
def local_ip():
    for ifaceName in interfaces():
        addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'No IP addr'}] )]
        if(' '.join(addresses) != 'No IP addr' ):
            if not(' '.join(addresses).startswith("127.")): # Local looping Subnet
                talonpi.putString('pi_local_ip',str(' '.join(addresses)))
                return(str(' '.join(addresses)))


app = Flask(__name__)

# define HoughCircles constants
ROUNDNESS_THRESH = 10
CENTER_DETECT_THRESH = 60
MIN_RADIUS = 20
# construct the argument parse and parse the arguments
vs = cv2.VideoCapture(0)
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

def mask_gen():
    while True:
        # Capture frame-by-frame
        success, frame = vs.read()  # read the camera frame
        if not success:
            break
        else:
            # grab the current frame
            _, frame = vs.read()
            # resize the frame, blur it, and convert it to the HSV

            blurred = cv2.GaussianBlur(frame, (101, 101), 0)
            hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
            # construct a mask for red or blue, then perform a series of dilations and erosions to remove any small blobs
            # left in the mask
            if(allianceColor == "blue"): # Blue Mask
                mask = cv2.inRange(hsv, blueLower, blueUpper)
            elif(allianceColor == "red"): # Red Mask
                mask = cv2.inRange(hsv, red1Lower, red1Upper) + cv2.inRange(hsv, red2Lower, red2Upper)
            else: # Default if they didn't post
                mask = cv2.inRange(hsv, red1Lower, red1Upper) + cv2.inRange(hsv, red2Lower, red2Upper)
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)
            # use Hough Circle Transform to find the roundest object on the screen and trace its perimeter
            circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, 2, 50, param1=ROUNDNESS_THRESH,
                                    param2=CENTER_DETECT_THRESH, minRadius=MIN_RADIUS, maxRadius=0)
            if circles is not None:
                circles = np.uint16(np.around(circles))
                biggest_circle = circles[[i[0][2] for i in circles].index(max([i[0][2] for i in circles]))]
                center = (biggest_circle[0][0], biggest_circle[0][1])
                # circle center
                cv2.circle(mask, center, 1, (255, 0, 255), 3)
                # circle outline
                radius = biggest_circle[0][2]
                talonpi.putNumber('Motor Value',(center[0] - 640) / 8000)

                cv2.circle(mask, center, radius, (255, 0, 255), 3)
                cv2.circle(frame, center, 1, (255, 0, 0), 3)
                cv2.circle(frame, center, radius, (0, 0, 255), 3)
            else:
                talonpi.putNumber('Motor Value', 0)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def raw_gen():  # Raw Video Feed
    while True:
        # Capture frame-by-frame
        success, frame = vs.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/mask') 
def mask_feed():
    return Response(mask_gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/raw')
def raw_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(raw_gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/') #Base root
def index():
    """Video streaming home page."""
    return render_template('root.html')
    
if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host=local_ip(), debug=True,port="5800",use_reloader=False)