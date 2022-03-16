from threading import Thread

import cv2
import numpy as np
from networktables import NetworkTables

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

# The Ball_Tracking class is used to track the ball's location and return the distance from the center of the screen
class Ball_Tracking: # no network tables
    """ The Ball_Tracking class is used to track the ball's location and return the distance from the center of the screen
        This doesnt use network tables so it should be used for local testing and debugging (say on your computer)
    """
    def __init__(self,frame,frame_width=0,alliance="blue",):
        self.frame_width = frame_width
        self.frame = frame
        self.allianceColor = alliance
        self.table = NetworkTables.getTable('TalonPi')
        self.lastValue = 0
        
    def start(self):
        Thread(target=self.ballTracking, args=()).start()
        return self
    
    def ballTracking(self):
        # region
        # resize the frame, blur it, and convert it to the HSV
        blurred = cv2.GaussianBlur(self.frame, (101, 101), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        # construct a mask for red or blue, then perform a series of dilations and erosions to remove any small blobs
        # left in the mask
        if(self.allianceColor == "blue"):
            mask = cv2.inRange(hsv, blueLower, blueUpper)
        else:
            mask = cv2.inRange(hsv, red1Lower, red1Upper) + cv2.inRange(hsv, red2Lower, red2Upper)
        # Define the currently used color to be checked later and error checked
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        # use Hough Circle Transform to find the roundest object on the screen and trace its perimeter
        circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, 2, 50, param1=ROUNDNESS_THRESH,param2=CENTER_DETECT_THRESH, minRadius=MIN_RADIUS, maxRadius=0)
        # endregion
        if circles is not None:
            circles = np.uint16(np.around(circles))
            biggest_circle = circles[[i[0][2] for i in circles].index(max([i[0][2] for i in circles]))]
            center = (biggest_circle[0][0], biggest_circle[0][1])
            if not self.lastValue == ((self.frame_width/2)-center[0]):
                print(((self.frame_width/2)-center[0]))
                self.table.getEntry('Motor Value').setDouble(((self.frame_width/2)-center[0]))
                self.lastValue = (((self.frame_width/2)-center[0]))
        else:
            if not self.lastValue == 0:
                print("none")
                self.table.getEntry('Motor Value').setDouble(0)


# !!!!! DEPRECEATED !!!!!
class Ball_Tracking_NT: # with network tables
    """ The Ball_Tracking class is used to track the ball's location and return the distance from the center of the screen by posting it to Network Tables 
        This works specifically by connecting to the TalonPi network table, it should not be called unless you are connected to the RoboRio network and a 
        connection listener is established to ensure no calls are blocked. This function works by using multi_threading to mask and form frames and then deriving
        ball data from them. It then posts this to network tables. This is done to increase the FPS of the primary thread (where it is called) so it doesn't need 
        to wait up for the frame to be analyzed.
    """
    
    def __init__(self, frame, frame_width=640, postZeros=False, alliance="blue"):
        self.frame_width = frame_width
        self.frame = frame
        self.table = NetworkTables.getTable('TalonPi')
        self.zeros = postZeros
        self.alliance = alliance
        
        
    def start(self):
        Thread(target=self.ballTracking, args=()).start()
        return self
    
    def ballTracking(self): # might need to be in a While loop (see CameraSteam.py)
        # resize the frame, blur it, and convert it to the HSV
        blurred = cv2.GaussianBlur(self.frame, (101, 101), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        # construct a mask for red or blue, then perform a series of dilations and erosions to remove any small blobs
        # left in the mask
        if self.alliance == "blue":
            mask = cv2.inRange(hsv, blueLower, blueUpper)
        else:
            mask = cv2.inRange(hsv, red1Lower, red1Upper) + cv2.inRange(hsv, red2Lower, red2Upper)
            
        # Define the currently used color to be checked later and error checked
        self.table.getEntry('Working Color').setString(self.alliance)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        # use Hough Circle Transform to find the roundest object on the screen and trace its perimeter
        circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, 2, 50, param1=ROUNDNESS_THRESH,param2=CENTER_DETECT_THRESH, minRadius=MIN_RADIUS, maxRadius=0)
        if circles is not None:
            circles = np.uint16(np.around(circles))
            biggest_circle = circles[[i[0][2] for i in circles].index(max([i[0][2] for i in circles]))]
            center = (biggest_circle[0][0], biggest_circle[0][1])
            self.table.getEntry('Motor Value').setDouble(((self.frame_width/2)-center[0]))
            print(((self.frame_width/2)-center[0]))
        else:
            if(self.zeros):
                self.table.getEntry('Motor Value').setDouble(0)
