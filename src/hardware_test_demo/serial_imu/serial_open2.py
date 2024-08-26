import serial

ser = serial.Serial()


def port_open_recv():  # 对串口的参数进行配置
    ser.port = "COM6"  # 串口号
    ser.baudrate = 9600  # 波特率
    ser.bytesize = 8  # 数据位数
    ser.stopbits = 1  # 停止位的比特数
    ser.parity = "N"  # 奇偶校验位
    ser.timeout = 15  # 超时
    ser.open()
    if ser.isOpen():
        print("串口打开成功！")
    else:
        print("串口打开失败！")


if __name__ == "__main__":
    port_open_recv()
