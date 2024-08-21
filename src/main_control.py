import time
from communication import stm_communication as stm
from communication import imu

from algorithm import vision
from algorithm import core

ENABLE_CAMERA = False  # True
CAMERA_COOLDOWN = 0.5

if ENABLE_CAMERA:
    from communication import camera

if __name__ == '__main__':

    start_time = time.time()

    stm = stm.STM()
    imu = imu.IMU()

    if ENABLE_CAMERA:
        camera = camera.Camera()
    else:
        camera = None

    core = core.Core()

    camera_last_used_time = -100

    while True:

        # TODO: what is the period of the cycle?

        time.sleep(0.001)
        print(time.time() - start_time)

        encoder_input = stm.get_encoder_input()
        ultrasonic_input = stm.get_ultrasonic_input()
        imu_input = imu.get_imu_input()

        camera_input = None
        if ENABLE_CAMERA and time.time() - camera_last_used_time > CAMERA_COOLDOWN:
            camera_image = camera.get_image_bgr()
            camera_last_used_time = time.time()
            camera_input = vision.process(camera_image)

        core.update(time.time() - start_time, encoder_input, ultrasonic_input, imu_input, camera_input)

        output = core.get_output()

        stm.send_output(output)

