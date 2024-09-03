import argparse
import time

parser = argparse.ArgumentParser(description="No description")
parser.add_argument("-d", dest="disable", action="store_true", help="Disable core visualization")
parser.set_defaults(disable=False)
args = parser.parse_args()

ENABLE_STM_INPUT   = True  # True
STM_INPUT_PROTOCOL = 127  # 127 | 128
ENABLE_IMU = True  # True
ENABLE_CAMERA = True  # True
ENABLE_VISION = True  # True
ENABLE_CORE = True  # True
ENABLE_STM_OUTPUT = True  # True

ENABLE_DUMMY = False  # False
DUMMY_CONTROL = True  # Whatever
ENABLE_CORE_VISUALIZER = True  # False
if args.disable:
    ENABLE_CORE_VISUALIZER = False
VISUALIZER_CONTROL = True  # False
MAX_MESSAGE_LENGTH = 6  # 6

CAMERA_COOLDOWN = 0.0
CYCLE_MIN_TIME = 0.0

if ENABLE_STM_INPUT or ENABLE_STM_OUTPUT:
    from communication import stm_communication as stm
if ENABLE_IMU:
    from communication import imu
if ENABLE_CAMERA:
    from communication import camera
if ENABLE_VISION:
    from algorithm import vision
if ENABLE_CORE:
    from algorithm import core
if ENABLE_DUMMY:
    if ENABLE_CORE_VISUALIZER:
        ENABLE_CORE_VISUALIZER = False
        print("Visualizer disabled by dummy.")
    import dummy
if ENABLE_CORE_VISUALIZER:
    from algorithm import core_visualizer

DEBUG_INFO = True
CAMERA_DEBUG_INFO = True
DEBUG_RESET = False
core.CORE_TIME_DEBUG = True  # False

FORCE_STOP_MESSAGE = bytes((128, 1, 0, 0, True, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0))


def real_time() -> float:
    return time.time() - start_time


def time_since_last_call(mul: int = 1000):
    last_call = start_time
    while True:
        temp = time.time() - last_call
        last_call += temp
        yield int(mul * temp)


if __name__ == "__main__":
    try:

        start_time = time.time()

        cycle_time = time_since_last_call()
        module_time = time_since_last_call()
        if DEBUG_INFO:
            print("\nLaunching")

        output = None
        imu_input = None
        unpacked_stm32_input = None
        stm32_input = None

        stm = stm.STM(STM_INPUT_PROTOCOL) if ENABLE_STM_INPUT or ENABLE_STM_OUTPUT else None
        if stm is not None:
            if DEBUG_INFO:
                print("STM32 connected, used time:", next(module_time))

        imu = imu.IMU() if ENABLE_IMU else None
        if imu is not None:
            if DEBUG_INFO:
                print("IMU connected, used time:", next(module_time))

        camera = camera.Camera() if ENABLE_CAMERA else None
        camera_last_used_time = -100
        if camera is not None:
            if DEBUG_INFO or CAMERA_DEBUG_INFO:
                print("CAMERA enabled, used time:", next(module_time))

        core = core.Core(real_time(), STM_INPUT_PROTOCOL) if ENABLE_CORE else None
        if core is not None:
            if DEBUG_INFO:
                print("Core initialized, used time:", next(module_time))

        dummy = dummy.Dummy(DUMMY_CONTROL, STM_INPUT_PROTOCOL) if ENABLE_DUMMY else None
        if dummy is not None:
            if DEBUG_INFO:
                print("Dummy plugged in, used time:", next(module_time))

        visualizer = core_visualizer.Visualizer(core, VISUALIZER_CONTROL) if ENABLE_CORE_VISUALIZER else None
        if visualizer is not None:
            if DEBUG_INFO:
                print("Visualizer initialized, used time:", next(module_time))

        cycle_count = 0

        if DEBUG_INFO:
            print("System initialized, used time in total:", next(cycle_time))

        while True:

            cycle_count += 1
            cycle_start_time = real_time()
            if DEBUG_INFO:
                print("\nCycle", cycle_count, "begins.")

            camera_input = None

            if ENABLE_STM_INPUT:
                stm32_input, unpacked_stm32_input = stm.get_message()
                if DEBUG_INFO:
                    print("Got STM32 input, used time:", next(module_time))
            if ENABLE_IMU:
                imu_input = imu.get_imu_input()
                if DEBUG_INFO:
                    print("Got IMU input:", imu_input)
                if DEBUG_INFO:
                    print("used time:", next(module_time))

            if ENABLE_CAMERA and real_time() - camera_last_used_time > CAMERA_COOLDOWN:
                camera_last_used_time = real_time()
                camera_image = camera.get_image_bgr()
                if DEBUG_INFO or CAMERA_DEBUG_INFO:
                    print("Got camera input, used time:", next(module_time))
                if ENABLE_VISION:
                    camera_input = vision.process(camera_last_used_time, camera_image)
                    if DEBUG_INFO or CAMERA_DEBUG_INFO:
                        print("Processed camera input, used time:", next(module_time))
                    # print(camera_input)

            if ENABLE_CORE:
                core.update(real_time(), stm32_input, unpacked_stm32_input, imu_input, camera_input)
                output = core.get_output()
                if DEBUG_INFO:
                    print("Got core output:", output.hex(" "))
                if DEBUG_INFO:
                    print("Used time:", next(module_time))

            if ENABLE_DUMMY:
                dummy_output = dummy.get_output(stm32_input, unpacked_stm32_input)
                if DUMMY_CONTROL:
                    output = dummy_output
                if dummy.force_stop:
                    output = FORCE_STOP_MESSAGE
                if DEBUG_INFO:
                    print("Got dummy output:", dummy_output.hex(" "))
                if DEBUG_INFO:
                    print("Used time:", next(module_time))

            if ENABLE_CORE_VISUALIZER:
                core = visualizer.update(real_time())
                output = core.get_output()
                if visualizer.force_stop:
                    output = FORCE_STOP_MESSAGE
                if DEBUG_INFO:
                    print("Visualization used time:", next(module_time))

            if ENABLE_STM_OUTPUT:
                if output[1] == 1:
                    stm.reset_time()
                    if DEBUG_RESET:
                        print("STM time reset.")
                stm.send_message(output, MAX_MESSAGE_LENGTH)
                if DEBUG_INFO:
                    print("Sent out output to STM32, used time:", next(module_time))

            sleep_time = max(0.0, cycle_start_time + CYCLE_MIN_TIME - real_time())
            if DEBUG_INFO:
                print("Cycle", cycle_count, "ends, used time in total:", next(cycle_time))
            time.sleep(sleep_time)
            if DEBUG_INFO:
                print("Slept:", next(cycle_time))
            next(module_time)
    finally:
        if stm is not None:
            for i in range(64):
                stm.send_message(FORCE_STOP_MESSAGE, MAX_MESSAGE_LENGTH)
            print("\n\nFORCE STOPPED")
