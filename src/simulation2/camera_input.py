
class Camera:
    def __init__(self, car, camera_state):
        self.car = car
        self.room = car.room
        self.camera_state = camera_state
        self.cooldown = 0.5
        self.last_capture_time = -10

    def get_input(self):
        if self.car.room.time - self.last_capture_time < self.cooldown:
            self.car.camera_capturing = False
            return None
        self.last_capture_time = self.car.room.time

        seen_reds = []
        seen_walls = []
        for r in self.room.reds:
            if len(self.car.camera_range.shapes_collide(r.shape).points) > 0:
                seen_reds.append(r.body.position)  # TODO: change to relative cords
        self.car.camera_capturing = True
        return seen_reds, seen_walls
