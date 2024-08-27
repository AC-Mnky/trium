# noinspection PyUnresolvedReferences
from picamera2 import Picamera2
import time
import cv2

START_WAIT_TIME = 2


class Camera:
    def __init__(self):
        self.cam = Picamera2()
        self.cam.start()
        self.start_time = time.time()

    def get_image_bgr(self) -> cv2.UMat | None:
        if time.time() - self.start_time < START_WAIT_TIME:
            return None
        return cv2.cvtColor(self.cam.capture_array("main"), cv2.COLOR_RGB2BGR)
