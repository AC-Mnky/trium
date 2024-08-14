from picamera2 import Picamera2
import cv2
import time

cap = Picamera2()
cap.start()

while True:
	frame = cap.capture_array("main")
	cv2.imshow("test", frame)
	if cv2.waitKey(1) & 0xFF == ord("q"):
		break
	time.sleep(0.1)
