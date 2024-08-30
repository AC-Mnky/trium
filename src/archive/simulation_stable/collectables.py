import pymunk
from room import Room


class Red:
    drag = 0.001
    angular_drag = 0.5
    friction = 0.5
    elasticity = 0

    def __init__(self, room: Room, x, y):
        self.room = room

        self.body = pymunk.Body(mass=0.01, moment=0.1)

        self.shape = pymunk.Poly(self.body, [(-2.5, -2.5), (-2.5, 2.5), (2.5, 2.5), (2.5, -2.5)])
        self.shape.color = (255, 0, 0, 255)
        self.shape.friction = self.friction
        self.shape.elasticity = self.elasticity

        self.body.position = (x, y)

        self.room.space.add(self.body, self.shape)
        self.room.reds.append(self)

    def physics(self):
        self.body.apply_impulse_at_world_point(-self.drag * self.body.velocity, self.body.position)
        self.body.torque -= self.body.angular_velocity * self.angular_drag


class Yellow:
    drag = 0.0001
    angular_drag = 0.5
    friction = 0.5
    elasticity = 0.5

    def __init__(self, room: Room, x, y):
        self.room = room

        self.body = pymunk.Body(mass=0.01, moment=0.1)

        self.shape = pymunk.Circle(self.body, 3)
        self.shape.friction = self.friction
        self.shape.elasticity = self.elasticity

        self.shape.color = (255, 255, 0, 255)

        self.body.position = (x, y)

        self.room.space.add(self.body, self.shape)
        self.room.yellows.append(self)

    def physics(self):
        self.body.apply_impulse_at_world_point(-self.drag * self.body.velocity, self.body.position)
        self.body.torque -= self.body.angular_velocity * self.angular_drag
