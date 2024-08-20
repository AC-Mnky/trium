import serial
import time

if __name__ == "__main__":
    ser2 = serial.Serial("COM6", 9600, timeout=15)  ##连接串口，打开

    while True:
        Read = ser2.readline()  # 读取所有数据
        print(Read)
        time.sleep(1)