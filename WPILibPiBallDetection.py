from cscore import CameraServer
import cv2
import numpy as np
def main():
    cs = CameraServer.getInstance()
    cs.enableLogging()
    camera = cs.startAutomaticCapture()
    camera.setResolution(320, 240)
    cvSink = cs.getVideo()
    outputStream = cs.putVideo("Name", 320, 240)
    img = np.zeros(shape=(240, 320, 3), dtype=np.uint8)
    lower_blue, upper_blue = np.array([100, 35, 140]), np.array([180, 255, 255])
    lower_red, upper_red = np.array([0, 50, 50]), np.array([10, 255, 255])
    while True:
        time, frame = cvSink.grabFrame(img)
        if time == 0:
            outputStream.notifyError(cvSink.getError())
            continue
        centerOfScreen = frame.shape[1] / 2
        blurred = cv2.GaussianBlur(frame, (15, 15), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        mask_blue, mask_red = cv2.inRange(hsv, lower_blue, upper_blue), cv2.inRange(hsv, lower_red, upper_red)
        mask_blue, mask_red = cv2.erode(mask_blue, None, iterations=2), cv2.erode(mask_red, None, iterations=2)
        mask_blue, mask_red = cv2.dilate(mask_blue, None, iterations=2), cv2.dilate(mask_red, None, iterations=2)
        result = cv2.bitwise_and(frame, frame, mask=mask_blue + mask_red)
        width, height = result.shape[:2]
        _, cnts_blue, _ = cv2.findContours(mask_blue.copy(), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_TC89_L1)
        _, cnts_red, _ = cv2.findContours(mask_red.copy(), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_TC89_L1)
        centers_blue, centers_red, distances_from_center_blue = list(), list(), list()
        if len(cnts_blue) > 0:
            for c in range(len(cnts_blue) - 1):
                (x, y), radius = cv2.minEnclosingCircle(cnts_blue[c])
                M = cv2.moments(cnts_blue[c])
                try:
                    centers_blue.append(
                        (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])))
                except ZeroDivisionError:
                    pass
                if radius > 100:
                    cv2.circle(
                        result, (centers_blue[-1]), int(radius), (255, 0, 0), 5)
                    cv2.circle(result, centers_blue[-1], 5, (0, 255, 255), -1)
                    distances_from_center_blue.append(
                        centers_blue[-1][0] - centerOfScreen)
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
                    centers_red.append(
                        (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])))
                except ZeroDivisionError:
                    pass
                if radius > 100:
                    cv2.circle(
                        result, (centers_red[-1]), int(radius), (0, 0, 255), 5)
                    cv2.circle(result, centers_red[-1], 5, (0, 255, 255), -1)
        outputStream.putFrame(result)
main()
