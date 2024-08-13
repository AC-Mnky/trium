import cv2
from os.path import isfile

from src.vision2.find_red import find_red

if __name__ == "__main__":

    for image_index in range(50):
        version = '0'
        filename = '../../assets/openCV_pic/version' + version + '/' + str(image_index) + '.jpg'
        if not isfile(filename):
            continue
        image = cv2.imread(filename)

        points = find_red(image)

        for p in points:
            cv2.circle(image, p, 10, (255, 255, 255, 255), 2)
        cv2.imshow('image', image)
        cv2.waitKey()
