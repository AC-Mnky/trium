import cv2 as cv
import numpy as np

image = np.astype(cv.imread('../assets/big_image.png'), np.int16)

# print(image)
# print(image.shape)
redness = image[:, :, 2]-image[:, :, 1]
redness = np.maximum(redness, np.zeros(redness.shape))
redness = np.astype(redness, np.uint8)

yellowness = image[:, :, 1]-image[:, :, 0]
yellowness = np.maximum(yellowness, np.zeros(yellowness.shape))
yellowness = np.astype(yellowness, np.uint8)
# print(redness.shape)
# print(np.sum(redness)/255)
# print(np.sum(yellowness)/255)
# hsv_image = cv.cvtColor(image, cv.COLOR_RGB2HSV)
# print(hsv_image.shape)
# lower_color = np.array([0, 0, 100])
# upper_color = np.array([100, 255, 255])
# mask = cv.inRange(hsv_image, lower_color, upper_color)
# contours, hierarchy = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
#
# target_contours = []
# for contour in contours:
#     x, y, w, h = cv2.boundingRect(contour)
#     area = cv.contourArea(contour)
#     target_contours.append(contour)
# print(len(target_contours))

is_red = (redness > 200) * 255


cv.imshow('image', cv.cvtColor(np.astype(is_red, np.uint8), cv.COLOR_GRAY2RGB))
cv.waitKey(0)
