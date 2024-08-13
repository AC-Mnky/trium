import cv2, os, time
import numpy as np
import Algo
from picamera2 import Picamera2
from Settings import Settings


class Cam(object):
    def __init__(self):
        self.cap = Picamera2()
        self.settings = Settings()

    def get_image_info(self, image):
        print(type(image))
        print(image.shape)
        print(image.size)
        print(image.dtype)

    def iden_color(self):
        self.cap.start()
        i = 0
        frame_rgb = None
        while True:
            frame_rgb = self.cap.capture_array(
                "main"
            )  # let the picture captured by the cam to be the current frame

            frame_bgr, _, _ = self.color_detection(
                frame_rgb
            )  # convert the difference between the color-encoding method of arrays

            cv2.imwrite(r'./pic/' + str(i) + '.jpg', frame_bgr)  # save the current frame
            i = i + 1
            cv2.imshow("capture", frame_bgr)  # show the current frame

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            time.sleep(0.5)
        self.cap.stop()

    def color_mask(self):
        self.cap.start()
        i = 0
        frame_rgb = None
        while True:
            frame_rgb = self.cap.capture_array(
                "main"
            )  # let the picture captured by the cam to be the current frame

            _, mask, _ = self.color_detection(
                frame_rgb
            )  # convert the difference between the color-encoding method of arrays

            i = i + 1
            cv2.imshow("capture", mask)  # show the current frame

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            time.sleep(0.1)
        self.cap.stop()

    def color_detection(self, frame_rgb):
        lower_red = self.settings.lower_red
        upper_red = self.settings.upper_red
        lower_blue = self.settings.lower_blue
        upper_blue = self.settings.upper_blue
        lower_green = self.settings.lower_green
        upper_green = self.settings.upper_green

        coords_list = []

        frame_hsv = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2HSV)

        red_mask = cv2.inRange(frame_hsv, lower_red, upper_red)
        blue_mask = cv2.inRange(frame_hsv, lower_blue, upper_blue)
        green_mask = cv2.inRange(frame_hsv, lower_green, upper_green)

        # filt the picture
        kernel = np.ones((5, 5), np.uint8)
        red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
        blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_OPEN, kernel)
        green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(
            red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        for contour in contours:
            if cv2.contourArea(contour) > 20:
                x, y, w, h = cv2.boundingRect(contour)
                coords_list.append((x, y))
        if len(coords_list) >= 4:
            coords_center, _ = Algo.k_means(coords_list)
        else:
            coords_center = coords_list

        for i in range(0, len(coords_center)):
            cv2.putText(frame_hsv, "RED", (int(coords_center[i][0]), int(coords_center[i][1] - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        return cv2.cvtColor(frame_hsv, cv2.COLOR_HSV2BGR), red_mask, coords_list
