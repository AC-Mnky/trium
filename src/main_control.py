import time

ENABLE_STM_INPUT = False  # True
ENABLE_IMU = False  # True
ENABLE_CAMERA = False  # True
ENABLE_CORE = True  # True
ENABLE_DUMMY = False  # False
USE_DUMMY = False  # False
ENABLE_STM_OUTPUT = False  # True

CAMERA_COOLDOWN = 0.5
CYCLE_MIN_TIME = 0.02

if ENABLE_STM_INPUT or ENABLE_STM_OUTPUT:
    from communication import stm_communication as stm
if ENABLE_IMU:
    from communication import imu
if ENABLE_CAMERA:
    from communication import camera
    from algorithm import vision
if ENABLE_CORE:
    from algorithm import core
if ENABLE_DUMMY:
    import dummy


def real_time() -> float:
    return time.time() - start_time


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
    imu_input = None
    stm32_input = None

    stm = stm.STM() if ENABLE_STM_INPUT or ENABLE_STM_OUTPUT else None
    if stm is not None:
        print('STM32 connected, used time:', next(module_time))

    imu = imu.IMU() if ENABLE_IMU else None
    if imu is not None:
        print('IMU connected, used time:', next(module_time))

    camera = camera.Camera() if ENABLE_CAMERA else None
    camera_last_used_time = -100
    if camera is not None:
        print('CAMERA enabled, used time:', next(module_time))

    core = core.Core(real_time()) if ENABLE_CORE else None
    if core is not None:
        print('Core initialized, used time:', next(module_time))

    dummy = dummy.Dummy() if USE_DUMMY else None
    if dummy is not None:
        print('Dummy started, used time:', next(module_time))

    cycle_count = 0

    print('System initialized, used time in total:', next(cycle_time))

    while True:

        cycle_count += 1
        cycle_start_time = real_time()
        print('\nCycle', cycle_count, 'begins.')

        camera_input = None

        if ENABLE_STM_INPUT:
            stm32_input = stm.get_message()
            # encoder_and_ultrasonic_input = stm.get_encoder_and_ultrasonic_input()
            print('Got STM32 input, used time:', next(module_time))
        if ENABLE_IMU:
            imu_input = imu.get_imu_input()
            print('Got IMU input, used time:', next(module_time))

        if ENABLE_CAMERA and real_time() - camera_last_used_time > CAMERA_COOLDOWN:
            camera_last_used_time = real_time()
            camera_image = camera.get_image_bgr()
            print('Got camera input, used time:', next(module_time))
            camera_input = vision.process(camera_last_used_time, camera_image)
            print('Processed camera input, used time:', next(module_time))

        if ENABLE_CORE:
            core.update(real_time(), stm32_input, imu_input, camera_input)
            output = core.get_output()
            print('Got core output:', output.hex(' '))
            print('Used time:', next(module_time))

        if ENABLE_DUMMY:
            dummy_output = dummy.get_output(stm32_input)
            if USE_DUMMY:
                output = dummy_output
            print('Got dummy output:', dummy_output.hex(' '))
            print('Used time:', next(module_time))

        if ENABLE_STM_OUTPUT:
            stm.send_message(output)
            print('Sent out output to STM32, used time:', next(module_time))

        sleep_time = max(0.0, cycle_start_time + CYCLE_MIN_TIME - real_time())
        print('Cycle', cycle_count, 'ends, used time in total:', next(cycle_time))
        time.sleep(sleep_time)
        print('Slept:', next(cycle_time))
        next(module_time)
