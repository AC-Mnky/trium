import serial
import math

ENCODER_PULSE_EACH_ROUND = 22
ENCODER_READ_FREQUENCY = 500
PWM_PERIOD = 100

WHEEL_RADIUS = 33
STANDARD_SPEED = 280/60*math.tau*WHEEL_RADIUS

class STM:
    def __init__(self):
        self.port = "/dev/ttyAMA0"
        self.baud = "115200"
        self.ser = serial.Serial(self.port, self.baud)
        self.message_length = 8

    def get_message(self):
        if not self.ser.is_open:
            self.ser.open()
        message = self.ser.read(self.message_length)
        self.ser.close()
        return message
    
    def get_encoder_and_ultrasonic_input(self) -> tuple[float, float, int, int]:
        message: bytes = self.get_message()
        encoder_1: int = int.from_bytes(message[0:2], 'big')
        encoder_2: int = int.from_bytes(message[2:4], 'big')
        ultrasonar_1: int = int.from_bytes(message[4:6], 'big')
        ultrasonar_2: int = int.from_bytes(message[6:8], 'big')
        if encoder_1 >= 2 ** 15:
            encoder_1 -= 2 ** 16
        if encoder_2 >= 2 ** 15:
            encoder_2 -= 2 ** 16

        velocity_1 = encoder_1*(ENCODER_READ_FREQUENCY/ENCODER_PULSE_EACH_ROUND)*math.tau*WHEEL_RADIUS
        velocity_2 = encoder_2*(ENCODER_READ_FREQUENCY/ENCODER_PULSE_EACH_ROUND)*math.tau*WHEEL_RADIUS

        return velocity_1, velocity_2, ultrasonar_1, ultrasonar_2
    
    def send_message(self,output):
        if not self.ser.is_open:
            self.ser.Open()

        message = [int(output[0][1] * PWM_PERIOD), int(output[0][0] * PWM_PERIOD), int(output[1]), int(output[2])]
        if message[0] < 0:
            message[0] += 256
        if message[1] < 0:
            message[1] += 256

        bytes(message)

        self.ser.write(message)
        self.ser.close()