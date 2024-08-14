# noinspection PyUnresolvedReferences
from picamera2 import Picamera2
from time import sleep
import cv2


class Camera:
    def __init__(self):
        self.cam = Picamera2()
        self.cam.start()
        sleep(2)

    def capture(self):
        return cv2.cvtColor(self.cam.capture_array("main"), cv2.COLOR_RGB2BGR)
    