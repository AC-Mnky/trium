import time

ENABLE_COMMUNICATION = True  # True
ENABLE_IMU = False  # True
ENABLE_CAMERA = False  # True
ENABLE_CORE = True  # True
USE_DUMMY = True  # False

CAMERA_COOLDOWN = 0.5
CYCLE_MIN_TIME = 0.01

if ENABLE_COMMUNICATION:
    from communication import stm_communication as stm
if ENABLE_IMU:
    from communication import imu
if ENABLE_CAMERA:
    from communication import camera
    from algorithm import vision
if ENABLE_CORE:
    from algorithm import core
if USE_DUMMY:
    import dummy


def time_since_start(mul: int = 1000):
    return int(mul*(time.time() - start_time))


def time_since_last_call(mul: int = 1000):
    last_call = start_time
    while True:
        temp = time.time() - last_call
        last_call += temp
        yield int(mul*temp)


if __name__ == '__main__':

    start_time = time.time()

    cycle_time = time_since_last_call()
    module_time = time_since_last_call()
    print('\nLaunching')

    output = None
    encoder_and_ultrasonic_input = None
    imu_input = None

    stm = stm.STM() if ENABLE_COMMUNICATION else None
    if stm is not None:
        print('STM32 connected, used time:', next(module_time))

    imu = imu.IMU() if ENABLE_IMU else None
    if imu is not None:
        print('IMU connected, used time:', next(module_time))

    camera = camera.Camera() if ENABLE_CAMERA else None
    camera_last_used_time = -100
    if camera is not None:
        print('CAMERA enabled, used time:', next(module_time))

    core = core.Core() if ENABLE_CORE else None
    if core is not None:
        print('Core initialized, used time:', next(module_time))

    dummy = dummy.Dummy() if USE_DUMMY else None
    if dummy is not None:
        print('Dummy started, used time:', next(module_time))

    cycle_count = 0

    print('System initialized, used time in total:', next(cycle_time))

    while True:

        cycle_count += 1
        cycle_start_time = time.time()
        print('\nCycle', cycle_count, 'begins.')

        camera_input = None

        if ENABLE_COMMUNICATION:
            encoder_and_ultrasonic_input = stm.get_encoder_and_ultrasonic_input()
            print('Got STM32 input, used time:', next(module_time))
        if ENABLE_IMU:
            imu_input = imu.get_imu_input()
            print('Got IMU input, used time:', next(module_time))

        if ENABLE_CAMERA and time.time() - camera_last_used_time > CAMERA_COOLDOWN:
            camera_image = camera.get_image_bgr()
            camera_last_used_time = time.time()
            print('Got camera input, used time:', next(module_time))
            camera_input = vision.process(camera_image)
            print('Processed camera input, used time:', next(module_time))

        if ENABLE_CORE:
            core.update(time.time() - start_time, encoder_and_ultrasonic_input, imu_input, camera_input)
            output = core.get_output()
            print('Core calculated output, used time:', next(module_time))

        if USE_DUMMY:
            output = dummy.get_output()
            print('Got dummy output, used time:', next(module_time))

        if ENABLE_COMMUNICATION:
            stm.send_output(output)
            print('Sent out output to STM32, used time:', next(module_time))

        sleep_time = max(0.0, cycle_start_time + CYCLE_MIN_TIME - time.time())
        print('Cycle', cycle_count, 'ends, used time in total:', next(cycle_time))
        time.sleep(sleep_time)
        print('Slept:', next(cycle_time))
        next(module_time)
