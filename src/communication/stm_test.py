import time

import serial

"""Test the serial communication with STM32"""

if __name__ == "__main__":
    ser = serial.Serial("/dev/ttyAMA0", "115200")
    ser.timeout = 1
    if ser.is_open:
        ser.close()
    ser.open()
    while True:
        # print(list(ser.read(5)))
        a = bytes([0, 1, 2, 3, 4, 5, 6, 7])
        print(a)
        ser.write(a)
        time.sleep(1)
