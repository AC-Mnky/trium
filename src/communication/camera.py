import time

import cv2

START_WAIT_TIME = 2


class Camera:
    def __init__(self):
        # self.cam = Picamera2()
        self.cam = cv2.VideoCapture(0)  # 0|1
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 320)  # 640)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)  # 480)
        # self.cam.start()
        self.start_time = time.time()

    def get_image_bgr(self) -> cv2.UMat | None:
        if time.time() - self.start_time < START_WAIT_TIME:
            return None
        # return cv2.cvtColor(self.cam.capture_array("main"), cv2.COLOR_RGB2BGR)
        _, frame = self.cam.read()
        # frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        return frame


if __name__ == "__main__":
    # Test codes
    print(-2)
    camera = Camera()
    print(-1)
    time.sleep(3)
    print(0)
    img = camera.get_image_bgr()
    print(1)
    cv2.imshow("img", img)
    print(2)
    cv2.waitKey()
