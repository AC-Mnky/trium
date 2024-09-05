import serial
import time

ser = serial.Serial("COM13", 115200)

if not ser.isOpen():
    ser.open()

print("open success")

ser.write(b"\x01")

counter = 0

while True:
    t = time.time()
    count = ser.inWaiting()
    if count > 0:
        recv = []
        # recv = [hex(i) for i in ser.read(count)]
        for i in ser.read(count):
            if hex(i) == "0x11":
                pass
            else:
                recv.append(hex(i))
        print(f"recv{counter}:")
        print(recv)
        print("\n")
        counter += 1
        ser.flushOutput()
        ser.flushInput()
    time.sleep(2)
    # recv = ser.read(10)
    # print(recv)
