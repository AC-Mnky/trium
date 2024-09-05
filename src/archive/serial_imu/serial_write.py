import serial
from time import sleep

ser = serial.Serial("COM9", 9600, timeout=15)  ##连接串口，同时调用了ser.opem()打开串口
ser.flushInput()  # 清除输入缓冲区
ser.flushOutput()  # 清除输出缓冲区

for i in range(10):
    ser.write("hello".encode("utf-8"))  # 写入数据
    sleep


ser.flushInput()  # 清除输入缓冲区
ser.flushOutput()  # 清除输出缓冲区
ser.close()
