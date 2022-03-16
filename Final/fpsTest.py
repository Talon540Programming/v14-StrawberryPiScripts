import time
from threading import Thread

import cv2
import imutils
import numpy as np

from CameraStream import WebCamVideoStream

# creating the videocapture object
# and reading from the input file
# Change it to 0 if reading from webcam
frame_width = 640

stream = WebCamVideoStream(src=0).start()
prev_frame_time = 0
new_frame_time = 0

while True:
	frame = stream.read()
	frame = imutils.resize(frame, width=frame_width)
	new_frame_time = time.time()
	fps = 1/(new_frame_time-prev_frame_time)
	prev_frame_time = new_frame_time
	fps = int(fps)
	print(fps)
 
	# displaying the frame with fps
	cv2.imshow('frame', frame)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

# When everything done, release the capture
stream.release()
# Destroy the all windows now
cv2.destroyAllWindows()
