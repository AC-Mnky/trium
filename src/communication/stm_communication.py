import serial
import math

ENCODER_PULSE_EACH_ROUND = 22
ENCODER_READ_FREQUENCY = 500
PWM_PERIOD = 100

WHEEL_RADIUS = 33
STANDARD_SPEED = 280 / 60 * math.tau * WHEEL_RADIUS


class STM:
    def __init__(self):
        self.port = "/dev/ttyAMA5"
        self.baud = "115200"
        self.ser = serial.Serial(self.port, self.baud, parity=serial.PARITY_EVEN)
        self.message_length = 96
        self.message_head = bytes((128, ) * 4)
        if not self.ser.is_open:
            self.ser.open()

    def get_message(self):

        if not self.ser.is_open:
            self.ser.open()

        while True:
            flag_match = True
            for b in self.message_head:
                if self.ser.read(1)[0] != b:
                    flag_match = False
                    break
            if flag_match:
                break

        message = self.message_head + self.ser.read(self.message_length - len(self.message_head))

        print('Message from STM32:', message.hex(' '))

        # self.ser.close()

        return message

    def get_encoder_and_ultrasonic_input(self) -> tuple[float, float, int, int]:
        message: bytes = self.get_message()
        encoder_1: int = int.from_bytes(message[0:2], 'big')
        encoder_2: int = int.from_bytes(message[2:4], 'big')
        ultrasonic_1: int = int.from_bytes(message[4:6], 'big')
        ultrasonic_2: int = int.from_bytes(message[6:8], 'big')
        if encoder_1 >= 2 ** 15:
            encoder_1 -= 2 ** 16
        if encoder_2 >= 2 ** 15:
            encoder_2 -= 2 ** 16

        velocity_1 = encoder_1 * (ENCODER_READ_FREQUENCY / ENCODER_PULSE_EACH_ROUND) * math.tau * WHEEL_RADIUS
        velocity_2 = encoder_2 * (ENCODER_READ_FREQUENCY / ENCODER_PULSE_EACH_ROUND) * math.tau * WHEEL_RADIUS

        return velocity_1, velocity_2, ultrasonic_1, ultrasonic_2

    def send_message(self, message: bytes, max_length: int):

        message = message[:max_length]

        if not self.ser.is_open:
            self.ser.open()

        print('Message to STM32:', message.hex(' '))

        self.ser.write(message)

        # self.ser.close()
