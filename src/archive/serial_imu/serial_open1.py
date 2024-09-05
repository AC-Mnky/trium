import serial

if __name__ == "__main__":
    ser = serial.Serial("COM9", 9600, timeout=15)  ##连接串口，同时调用了ser.opem()打开串口
    ser_status = ser.is_open
    print("当前串口状态：" + str(ser_status))

    ser.close()
    ser_status = ser.is_open
    print("当前串口状态：" + str(ser_status))
