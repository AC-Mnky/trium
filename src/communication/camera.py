import time

import cv2

START_WAIT_TIME = 2


class Camera:
    def __init__(self):
        # self.cam = Picamera2()
        self.cam = cv2.VideoCapture(0)  # 0|1
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        # self.cam.start()
        self.start_time = time.time()

    def get_image_bgr(self) -> cv2.UMat | None:
        if time.time() - self.start_time < START_WAIT_TIME:
            return None


if __name__ == "__main__":
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
