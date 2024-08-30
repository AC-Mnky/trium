import time

import serial


class IMU:
    """
    Class of the IMU sensor, which reads data through a serial port under USART protocol.
    """

    def __init__(self):
        """
        Initializes the IMU class with the port and baud rate.
        Current IMU retrieval rate: 200Hz.
        """
        # self.port = "COM6"  # PC
        self.port = "/dev/ttyAMA5"  # Pi 4B -> UART5
        self.baud = 115200
        self.ser_imu = serial.Serial(self.port, self.baud, timeout=0.5)

    def get_imu_input(
        self,
    ) -> tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]] | None:
        """
        Reads IMU data from a serial port.

        Returns:
            tuple (tuple | None): A tuple containing the acceleration, angular velocity, and angle values.
        """
        datahex = self.ser_imu.read(33)
        return self._process_input_data(datahex)

    def _extract_acceleration(self, datahex: bytes) -> tuple[float, float, float]:
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

        return acc_x, acc_y, acc_z

    def _extract_angular_velocity(self, datahex: bytes) -> tuple[float, float, float]:
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

        return gyro_x, gyro_y, gyro_z

    def _extract_angle(self, datahex: bytes) -> tuple[float, float, float]:
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

        return angle_x, angle_y, angle_z

    def _process_input_data(
        self, inputdata: bytes
    ) -> tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]] | None:
        """
        Process the input data and extract acceleration, angular velocity, and angle information.

        Args:
            inputdata (bytes): The input data to be processed.

        Returns:
            None

        Prints:
            acceleration (g): The acceleration values in g-force.
            angular_Velocity (deg/s): The angular velocity values in degrees per second.
            angle (deg): The angle values in degrees.
        """
        add_data = [0.0] * 8
        gyro_data = [0.0] * 8
        angle_data = [0.0] * 8
        frame_state = 0  # 通过0x后面的值判断属于哪一种情况
        byte_num = 0  # 读取到这一段的第几位
        check_sum = 0  # 求和校验位
        acceleration = [0.0] * 3
        angular_velocity = [0.0] * 3
        angle = [0.0] * 3

        for data in inputdata:  # 在输入的数据进行遍历
            if frame_state == 0:  # 当未确定状态的时候，进入以下判断
                if data == 0x55 and byte_num == 0:  # 0x55位于第一位时候，开始读取数据，增大bytenum
                    check_sum = data
                    byte_num = 1
                    continue
                elif data == 0x51 and byte_num == 1:  # 在byte不为0 且 识别到 0x51 的时候，改变frame
                    check_sum += data
                    frame_state = 1
                    byte_num = 2
                elif data == 0x52 and byte_num == 1:  # 同理
                    check_sum += data
                    frame_state = 2
                    byte_num = 2
                elif data == 0x53 and byte_num == 1:
                    check_sum += data
                    frame_state = 3
                    byte_num = 2
            elif frame_state == 1:  # acc    # 已确定数据代表加速度

                if byte_num < 10:  # 读取8个数据
                    add_data[byte_num - 2] = data  # 从0开始
                    check_sum += data
                    byte_num += 1
                else:
                    if data == (check_sum & 0xFF):  # 假如校验位正确
                        acceleration = self._extract_acceleration(add_data)
                    check_sum = 0  # 各数据归零，进行新的循环判断
                    byte_num = 0
                    frame_state = 0
            elif frame_state == 2:  # gyro

                if byte_num < 10:
                    gyro_data[byte_num - 2] = data
                    check_sum += data
                    byte_num += 1
                else:
                    if data == (check_sum & 0xFF):
                        angular_velocity = self._extract_angular_velocity(gyro_data)
                    check_sum = 0
                    byte_num = 0
                    frame_state = 0
            elif frame_state == 3:  # angle

                if byte_num < 10:
                    angle_data[byte_num - 2] = data
                    check_sum += data
                    byte_num += 1
                else:

                    if data == (check_sum & 0xFF):
                        angle = self._extract_angle(angle_data)
                        return acceleration, angular_velocity, angle
                    """ Debug printing codes

                        print("Acceleration(g):", acceleration)
                        print("Angular_Velocity(deg/s):", angular_velocity)
                        print("Angle(deg):", angle)
                        print("\n")
                    """
                    check_sum = 0
                    byte_num = 0
                    frame_state = 0

        return None


if __name__ == "__main__":
    # Test the IMU class
    imu = IMU()
    st = time.time()
    imu.get_imu_input()
    ed = time.time()
    print("Time:", ed - st)
