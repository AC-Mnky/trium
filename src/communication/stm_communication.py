import serial

class STM:
    def __init__(self):
        self.port = "/dev/ttyAMA0"
        self.baud = "115200"
        self.ser = serial.Serial(self.port, self.baud)
        self.message_length = 8

    def get_message(self):
        if not self.ser.is_open:
            self.ser.Open()
        message = self.ser.read(self.message_length)
        self.ser.close()
        return message
    
    def due_data(self):
        