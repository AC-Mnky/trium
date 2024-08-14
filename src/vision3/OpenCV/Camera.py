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

            frame_bgr, _ = self.color_detection(
                frame_rgb
            )  # convert the difference between the color-encoding method of arrays

            #cv2.imwrite(r'./pic/'+str(i)+'.jpg',frame_bgr)#save the current frame
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

            _, mask = self.color_detection(
                frame_rgb
            )  # convert the difference between the color-encoding method of arrays

            i = i + 1
            cv2.imshow("capture", mask)  # show the current frame

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            time.sleep(0.5)
        self.cap.stop()

    def color_detection(self, frame_rgb):
        lower_red = self.settings.lower_red
        upper_red = self.settings.upper_red
        lower_yellow = self.settings.lower_yellow
        upper_yellow = self.settings.upper_yellow

        frame_hsv = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2HSV)

        red_mask = cv2.inRange(frame_hsv, lower_red, upper_red)
        yellow_mask = cv2.inRange(frame_hsv, lower_yellow, upper_yellow)

        # filt the picture
        kernel = np.ones((5, 5), np.uint8)
        red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
        yellow_mask = cv2.morphologyEx(yellow_mask, cv2.MORPH_OPEN, kernel)

        # find red stuff
        red_contours, _ = cv2.findContours(
            red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        coords_list_red = []
        coords_center_red = []
        for contour in red_contours:
            if cv2.contourArea(contour) > 20:
                x, y, w, h = cv2.boundingRect(contour)
                coords_list_red.append((x, y))

        if len(coords_list_red) != 0:
            coords_center_red = Algo.loop_check(coords_list_red)
        else:
            coords_center_red = coords_list_red

        
        for i in range(0,len(coords_center_red)):
            cv2.putText(frame_hsv,"RED",(int(coords_center_red[i][0]), int(coords_center_red[i][1] - 10)),cv2.FONT_HERSHEY_SIMPLEX,0.9,(0, 255, 0),2)
        
        #find yellow stuff
        yellow_contours, _ = cv2.findContours(
            yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        coords_list_yellow = []
        coords_center_yellow = []
        for contour in yellow_contours:
            if cv2.contourArea(contour) > 20:
                x, y, w, h = cv2.boundingRect(contour)
                coords_list_yellow.append((x, y))
        if len(coords_list_yellow) != 0:
            coords_center_yellow = Algo.loop_check(coords_list_yellow)
        else:
            coords_center_yellow = coords_list_yellow
        
        for i in range(0,len(coords_center_yellow)):
            cv2.putText(frame_hsv,"YELLOW",(int(coords_center_yellow[i][0]), int(coords_center_yellow[i][1] - 10)),cv2.FONT_HERSHEY_SIMPLEX,0.9,(0, 255, 0),2)
        
        
        return cv2.cvtColor(frame_hsv, cv2.COLOR_HSV2BGR), red_mask
