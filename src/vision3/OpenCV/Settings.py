import numpy as np


class Settings:
    def __init__(self):
        self.lower_red = np.array([0, 100, 100])
        self.upper_red = np.array([10, 255, 200])
        self.lower_blue = np.array([110, 100, 100])
        self.upper_blue = np.array([130, 255, 255])
        self.lower_green = np.array([50, 100, 100])
        self.upper_green = np.array([70, 255, 255])
        self.lower_yellow = np.array([26, 43, 46])
        self.upper_yellow = np.array([34, 255, 200])
