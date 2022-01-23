import cv2
import numpy as np
from datetime import datetime
from threading import Thread

print("[Imported OpenCV] Current Version: "+cv2.__version__)
print("[Imported numpy] Current Version: "+np.__version__)

now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("Sysclock: "+current_time)
