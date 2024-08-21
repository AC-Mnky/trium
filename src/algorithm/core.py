class Core:
    def __init__(self):
        ...  # TODO

    def reset(self) -> None:
        ...  # TODO

    def update(self,
               time: float,
               encoder_input: tuple[int, int],
               ultrasonic_input: ...,
               imu_input: ...,
               camera_input: ... | None) -> None:

        ...  # TODO

    def get_output(self) -> ...:
        ...  # TODO
