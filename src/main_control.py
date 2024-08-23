import time

ENABLE_COMMUNICATION = True  # True
ENABLE_CAMERA = False  # True
ENABLE_CORE = True  # True
USE_DUMMY = True  # False

CAMERA_COOLDOWN = 0.5

if ENABLE_COMMUNICATION:
    from communication import stm_communication as stm
    from communication import imu
if ENABLE_CAMERA:
    from communication import camera
    from algorithm import vision
if ENABLE_CORE:
    from algorithm import core
if USE_DUMMY:
    import dummy

if __name__ == '__main__':

    start_time = time.time()

    output = None
    encoder_and_ultrasonic_input = None
    imu_input = None

    stm = stm.STM() if ENABLE_COMMUNICATION else None
    imu = imu.IMU() if ENABLE_COMMUNICATION else None
    camera = camera.Camera() if ENABLE_CAMERA else None
    core = core.Core() if ENABLE_CORE else None
    dummy = dummy.Dummy() if USE_DUMMY else None

    camera_last_used_time = -100

    while True:

        # TODO: what is the period of the cycle?

        time.sleep(0.001)
        print(time.time() - start_time)

        camera_input = None

        if ENABLE_COMMUNICATION:
            encoder_and_ultrasonic_input = stm.get_encoder_and_ultrasonic_input()
            imu_input = imu.get_imu_input()

        if ENABLE_CAMERA and time.time() - camera_last_used_time > CAMERA_COOLDOWN:
            camera_image = camera.get_image_bgr()
            camera_last_used_time = time.time()
            camera_input = vision.process(camera_image)

        if ENABLE_CORE:
            core.update(time.time() - start_time, encoder_and_ultrasonic_input, imu_input, camera_input)
            output = core.get_output()
        if USE_DUMMY:
            output = dummy.get_output()

        stm.send_output(output)
