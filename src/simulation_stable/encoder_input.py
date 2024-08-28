
class Encoder:
    def __init__(self, car):
        self.car = car

    def get_input(self):
        l, r = self.car.get_relative_velocity()
        return l[0], r[0]
