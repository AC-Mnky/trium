
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
        self.car.camera_capturing = True
        self.last_capture_time = self.car.room.time

        seen_reds = []
        for r in self.room.reds:
            if len(self.car.camera_range.shapes_collide(r.shape).points) > 0:
                seen_reds.append(self.car.body.world_to_local(r.body.position))

        seen_yellows = []
        for y in self.room.yellows:
            if len(self.car.camera_range.shapes_collide(y.shape).points) > 0:
                seen_yellows.append(self.car.body.world_to_local(y.body.position))

        wall_inferred_x = None
        wall_inferred_y = None
        wall_inferred_angle = None
        for w in self.room.walls[:2]:
            if len(self.car.camera_range.shapes_collide(w).points) > 0:
                wall_inferred_x = self.car.body.position[0]
                wall_inferred_angle = self.car.body.angle
        for w in self.room.walls[2:]:
            if len(self.car.camera_range.shapes_collide(w).points) > 0:
                wall_inferred_y = self.car.body.position[1]
                wall_inferred_angle = self.car.body.angle

        return seen_reds, seen_yellows, wall_inferred_x, wall_inferred_y, wall_inferred_angle
