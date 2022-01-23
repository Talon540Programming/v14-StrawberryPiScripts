"""imports: computer vision, datetime, and threading"""

from threading import Thread
import cv2
import datetime
import numpy as np
import time

#declare class for Frames Per Sec - inherits nothing, but object properties
class FPS: 
    #constructor, declares/initializes instance variable
    def __init__(self):
        self._start = None
        self._end = None
        self._numFrames = 0

    #getter methods (including return self) 
        
    #start method - grants a start time, for the frames
    def start(self):
        self._start = datetime.datetime.now()
        return self #returns reference to the instance object it was called from
    
    #simple method that calculates the elapsed time
    def elapsed(self):
        return (self._end - self._start).total_seconds()

    #just calculates the fps, number of frames divided by elapsed time
    def fps(self):
        return self._numFrames / self.elapsed()
    
    #setter methods without return values
    
    #stops the frame recording, and resets the time
    def stop(self):
        self._end = datetime.datetime.now()

    #increases the frame count by 1 each time it is called
    def update(self):
        self._numFrames += 1

#webcam streaming class - inherits nothing except the object properties
class WebcamVideoStream:
    
    #initializiation/constructor for the instance variables
    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src) #creates variable of object type for the entire cv2 video capture
        (self.grabbed, self.frame) = self.stream.read() #initializes 2 objects within a tuple 
        self.stopped = False #assumes that the stream starts out by boolean value

    
    def start(self):
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        while True:
            if self.stopped:
                return
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True


fps = FPS().start()
vs = WebcamVideoStream(src=0).start()
time.sleep(2)
lower_blue, upper_blue = np.array([100, 35, 140]), np.array([180, 255, 255])
lower_red, upper_red = np.array([0, 50, 50]), np.array([10, 255, 255])


def detectBalls():
    global fps, lower_blue, upper_blue, lower_red, upper_red
    start, stop = time.perf_counter(), time.perf_counter()
    while True:
        frame = vs.read()
        centerOfScreen = frame.shape[1] / 2
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask_blue, mask_red = cv2.inRange(hsv, lower_blue, upper_blue), cv2.inRange(hsv, lower_red, upper_red)
        result = cv2.bitwise_and(frame, frame, mask=mask_blue + mask_red)

        blurred = cv2.GaussianBlur(frame, (15, 15), 0)
        width, height = result.shape[:2]

        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        mask_blue, mask_red = cv2.erode(mask_blue, None, iterations=2), cv2.erode(mask_red, None, iterations=2)
        mask_blue, mask_red = cv2.dilate(mask_blue, None, iterations=2), cv2.dilate(mask_red, None, iterations=2)
        cnts_blue, _ = cv2.findContours(mask_blue.copy(), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_TC89_L1)
        cnts_red, _ = cv2.findContours(mask_red.copy(), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_TC89_L1)
        centers_blue, centers_red, distances_from_center_blue = list(), list(), list()
        if len(cnts_blue) > 0:
            for c in range(len(cnts_blue) - 1):
                (x, y), radius = cv2.minEnclosingCircle(cnts_blue[c])
                M = cv2.moments(cnts_blue[c])
                try:
                    centers_blue.append((int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])))
                except ZeroDivisionError:
                    pass
                if radius > 100:
                    cv2.circle(result, (centers_blue[-1]), int(radius), (255, 0, 0), 5)
                    cv2.circle(result, centers_blue[-1], 5, (0, 255, 255), -1)
                    distances_from_center_blue.append(centers_blue[-1][0] - centerOfScreen)
            if len(distances_from_center_blue) > 0:
                try:
                    min_distance = min(distances_from_center_blue)
                except TypeError:
                    pass
                if min_distance < 0:
                    print('turn left {}'.format(abs(min_distance)))
                else:
                    print('turn right {}'.format(min_distance))
            else:
                pass
        if len(cnts_red) > 0:
            for c in range(len(cnts_red) - 1):
                ((x, y), radius) = cv2.minEnclosingCircle(cnts_red[c])
                M = cv2.moments(cnts_red[c])
                try:
                    centers_red.append((int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])))
                except ZeroDivisionError:
                    pass
                if radius > 100:
                    cv2.circle(result, (centers_red[-1]), int(radius), (0, 0, 255), 5)
                    cv2.circle(result, centers_red[-1], 5, (0, 255, 255), -1)
        cv2.imshow("Result", result)
        if cv2.waitKey(1) & 0xFF == ord('c'):
            break
        stop = time.perf_counter()
        fps.update()
    fps.stop()
    vs.stop()
    cv2.destroyAllWindows()
    print("[LOG]: Test Durration Complete")  # REMOVE


detectBalls()  # REMOVE
