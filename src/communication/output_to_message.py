
PWM_PERIOD = 100


def output_to_message(output) -> bytes:
    message = [0x80,
               int(output[0][1] * PWM_PERIOD),
               int(output[0][0] * PWM_PERIOD),
               int(output[1]),
               int(output[2])] \
                + output[3][1] \
                + output[3][0]

    for i in range(len(message)):
        if message[i] < 0:
            message[i] += 256

    message = bytes(message)
    return message
