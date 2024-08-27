import serial


class IMU:
    """
    Class of the IMU sensor, which reads data through a serial port under USART protocol.
    """

    def __init__(self):
        """
        Initializes the IMU class with the port and baud rate.
        """
        # self.port = "COM6"  # PC
        self.port = "/dev/ttyAMA5"  # Pi 4B
        self.baud = 115200

    def get_imu_input(self) -> None:
        """
        Reads IMU data from a serial port.
        """
        ser = serial.Serial(self.port, self.baud, timeout=0.5)
        print(ser.is_open)

        # A test demo. May be modified later.
        for _ in range(1):
            datahex = ser.read(33)
            self._process_input_data(datahex)

    def _extract_acceleration(self, datahex: bytes) -> list:
        """
        Calculates the acceleration values from the given hexadecimal data.

        Args:
            datahex (bytes): The input data in hexadecimal format.

        Returns:
            acc (list): A list containing the acceleration values [acc_x, acc_y, acc_z].
        """
        axl = datahex[0]
        axh = datahex[1]
        ayl = datahex[2]
        ayh = datahex[3]
        azl = datahex[4]
        azh = datahex[5]

        k_acc = 16.0

        acc_x = (axh << 8 | axl) / 32768.0 * k_acc
        acc_y = (ayh << 8 | ayl) / 32768.0 * k_acc
        acc_z = (azh << 8 | azl) / 32768.0 * k_acc

        if acc_x >= k_acc:
            acc_x -= 2 * k_acc
        if acc_y >= k_acc:
            acc_y -= 2 * k_acc
        if acc_z >= k_acc:
            acc_z -= 2 * k_acc

        acc = [acc_x, acc_y, acc_z]
        return acc

    def _extract_angular_velocity(self, datahex: bytes) -> list:
        """
        Calculates the angular velocity from the given hexadecimal data.

        Args:
            datahex (bytes): The input data in hexadecimal format.

        Returns:
            gyro (list): A list containing the angular velocity values [gyro_x, gyro_y, gyro_z].
        """
        wxl = datahex[0]
        wxh = datahex[1]
        wyl = datahex[2]
        wyh = datahex[3]
        wzl = datahex[4]
        wzh = datahex[5]

        k_gyro = 2000.0

        gyro_x = (wxh << 8 | wxl) / 32768.0 * k_gyro
        gyro_y = (wyh << 8 | wyl) / 32768.0 * k_gyro
        gyro_z = (wzh << 8 | wzl) / 32768.0 * k_gyro

        if gyro_x >= k_gyro:
            gyro_x -= 2 * k_gyro
        if gyro_y >= k_gyro:
            gyro_y -= 2 * k_gyro
        if gyro_z >= k_gyro:
            gyro_z -= 2 * k_gyro

        gyro = [gyro_x, gyro_y, gyro_z]
        return gyro

    def _extract_angle(self, datahex: bytes) -> list:
        """
        Calculates the angles from the given hexadecimal data.

        Args:
            datahex (bytes): The input data in hexadecimal format.

        Returns:
            angle (list): A list containing the calculated angles [angle_x, angle_y, angle_z].
        """
        rxl = datahex[0]
        rxh = datahex[1]
        ryl = datahex[2]
        ryh = datahex[3]
        rzl = datahex[4]
        rzh = datahex[5]

        k_angle = 180.0

        angle_x = (rxh << 8 | rxl) / 32768.0 * k_angle
        angle_y = (ryh << 8 | ryl) / 32768.0 * k_angle
        angle_z = (rzh << 8 | rzl) / 32768.0 * k_angle

        if angle_x >= k_angle:
            angle_x -= 2 * k_angle
        if angle_y >= k_angle:
            angle_y -= 2 * k_angle
        if angle_z >= k_angle:
            angle_z -= 2 * k_angle

        angle = [angle_x, angle_y, angle_z]
        return angle

    def _process_input_data(self, inputdata: bytes) -> None:
        """
        Process the input data and extract acceleration, angular velocity, and angle information.

        Args:
            inputdata (bytes): The input data to be processed.

        Returns:
            None

        Prints:
            Acceleration (g): The acceleration values in g-force.
            Angular_Velocity (deg/s): The angular velocity values in degrees per second.
            Angle (deg): The angle values in degrees.
        """
        ACCData = [0.0] * 8
        GYROData = [0.0] * 8
        AngleData = [0.0] * 8
        FrameState = 0  # 通过0x后面的值判断属于哪一种情况
        Bytenum = 0  # 读取到这一段的第几位
        CheckSum = 0  # 求和校验位
        acceleration = [0.0] * 3
        angular_velocity = [0.0] * 3
        Angle = [0.0] * 3
        for data in inputdata:  # 在输入的数据进行遍历
            if FrameState == 0:  # 当未确定状态的时候，进入以下判断
                if (
                    data == 0x55 and Bytenum == 0
                ):  # 0x55位于第一位时候，开始读取数据，增大bytenum
                    CheckSum = data
                    Bytenum = 1
                    continue
                elif (
                    data == 0x51 and Bytenum == 1
                ):  # 在byte不为0 且 识别到 0x51 的时候，改变frame
                    CheckSum += data
                    FrameState = 1
                    Bytenum = 2
                elif data == 0x52 and Bytenum == 1:  # 同理
                    CheckSum += data
                    FrameState = 2
                    Bytenum = 2
                elif data == 0x53 and Bytenum == 1:
                    CheckSum += data
                    FrameState = 3
                    Bytenum = 2
            elif FrameState == 1:  # acc    #已确定数据代表加速度

                if Bytenum < 10:  # 读取8个数据
                    ACCData[Bytenum - 2] = data  # 从0开始
                    CheckSum += data
                    Bytenum += 1
                else:
                    if data == (CheckSum & 0xFF):  # 假如校验位正确
                        acceleration = self._extract_acceleration(ACCData)
                    CheckSum = 0  # 各数据归零，进行新的循环判断
                    Bytenum = 0
                    FrameState = 0
            elif FrameState == 2:  # gyro

                if Bytenum < 10:
                    GYROData[Bytenum - 2] = data
                    CheckSum += data
                    Bytenum += 1
                else:
                    if data == (CheckSum & 0xFF):
                        angular_velocity = self._extract_angular_velocity(GYROData)
                    CheckSum = 0
                    Bytenum = 0
                    FrameState = 0
            elif FrameState == 3:  # angle

                if Bytenum < 10:
                    AngleData[Bytenum - 2] = data
                    CheckSum += data
                    Bytenum += 1
                else:
                    if data == (CheckSum & 0xFF):
                        Angle = self._extract_angle(AngleData)
                        print("Acceleration(g):", acceleration)
                        print("Angular_Velocity(deg/s):", angular_velocity)
                        print("Angle(deg):", Angle)
                        print("\n")
                    CheckSum = 0
                    Bytenum = 0
                    FrameState = 0


if __name__ == "__main__":
    imu = IMU()
    imu.get_imu_input()
