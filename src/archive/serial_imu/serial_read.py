import serial


def read_hex(serial):
    data = serial.read(2)

    return data


if __name__ == "__main__":
    ser2 = serial.Serial("COM12", 115200, timeout=3)  ##连接串口，打开

    while True:
        data = read_hex(ser2)  # 读取所有数据
        print(data)
