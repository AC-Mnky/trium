import time
from communication import stm_communication as stm
from communication import imu
from communication import camera
from algorithm import vision
from algorithm import core

CAMERA_COOLDOWN = 0.5

if __name__ == '__main__':

    stm = stm.STM()
    imu = imu.IMU()
    camera = camera.Camera()

    core = core.Core()

    camera_last_used_time = -100

    while True:

        # TODO: what is the period of the cycle?

        encoder_input = stm.get_encoder_input()
        ultrasonic_input = stm.get_ultrasonic_input()
        imu_input = imu.get_imu_input()

        camera_input = None
        if time.time() - camera_last_used_time > CAMERA_COOLDOWN:
            camera_image = camera.get_image_bgr()
            camera_last_used_time = time.time()
            camera_input = vision.process(camera_image)

        core.update(time.time(), encoder_input, ultrasonic_input, imu_input, camera_input)

        output = core.get_output()

        stm.send_output(output)

