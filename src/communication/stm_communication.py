import math
import time
from struct import unpack

import serial

ENCODER_PULSE_EACH_ROUND = 22
ENCODER_READ_FREQUENCY = 500
PWM_PERIOD = 100

WHEEL_RADIUS = 33
STANDARD_SPEED = 280 / 60 * math.tau * WHEEL_RADIUS


class STM:
    def __init__(self, protocol: int):
        self.port = "/dev/ttyAMA0"
        self.baud = "115200"
        self.ser = serial.Serial(self.port, self.baud, parity=serial.PARITY_NONE)
        self.protocol = protocol
        self.message_length = 96 if protocol == 128 else 17
        self.message_head = bytes((128, ) * 4) if protocol == 128 else bytes((127, ))
        if not self.ser.is_open:
            self.ser.open()
        self.stm_start_time = time.time()
            
    def reset_time(self) -> None:
        self.stm_start_time = time.time()

    def get_message(self) -> tuple[bytes, list[int]]:

        if not self.ser.is_open:
            self.ser.open()
            
        unpacked_message = [0, 0, 0, 0]
        
        while True:
            
            while True:
                flag_match = True
                for b in self.message_head:
                    if self.ser.read(1)[0] != b:
                        flag_match = False
                        break
                if flag_match:
                    break

            message = self.message_head + self.ser.read(
                self.message_length - len(self.message_head)
            )
            
            if self.protocol == 128:
                ...  # TODO
            elif self.protocol == 127:
                encoder = (
                    unpack("<h", message[11:13])[0],
                    unpack("<h", message[5:7])[0],
                )
                tick = (
                    unpack("<I", message[7:11])[0],
                    unpack("<I", message[1:5])[0],
                )
                unpacked_message[0] += tick[0]
                unpacked_message[1] += tick[1]
                unpacked_message[2] += encoder[0]
                unpacked_message[3] += encoder[1]

            # print("Message from STM32:", message.hex(" "))
            
            lag = (time.time() - self.stm_start_time) * 1000 - unpack('<I', message[13:17])[0]
            # print("Message lag:", lag)
            # if lag < 25 or self.ser.inWaiting() < self.message_length:
            if self.ser.inWaiting() < self.message_length:
                break

        # self.ser.close()
        
        # message = bytes((0,) * 17)

        return message, unpacked_message

    def get_encoder_and_ultrasonic_input(self) -> tuple[float, float, int, int]:
        message: bytes = self.get_message()
        encoder_1: int = int.from_bytes(message[0:2], "big")
        encoder_2: int = int.from_bytes(message[2:4], "big")
        ultrasonic_1: int = int.from_bytes(message[4:6], "big")
        ultrasonic_2: int = int.from_bytes(message[6:8], "big")
        if encoder_1 >= 2**15:
            encoder_1 -= 2**16
        if encoder_2 >= 2**15:
            encoder_2 -= 2**16

        velocity_1 = (
            encoder_1
            * (ENCODER_READ_FREQUENCY / ENCODER_PULSE_EACH_ROUND)
            * math.tau
            * WHEEL_RADIUS
        )
        velocity_2 = (
            encoder_2
            * (ENCODER_READ_FREQUENCY / ENCODER_PULSE_EACH_ROUND)
            * math.tau
            * WHEEL_RADIUS
        )

        return velocity_1, velocity_2, ultrasonic_1, ultrasonic_2

    def send_message(self, message: bytes, max_length: int):

        message = message[:max_length]

        if not self.ser.is_open:
            self.ser.open()

        # print("Message to STM32:", message.hex(" "))

        self.ser.write(message)

        # self.ser.close()
