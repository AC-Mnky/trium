import numpy as np
import pymunk
from pymunk.vec2d import Vec2d

from room import Room
from algorithm import Algorithm
from camera_input import Camera
from imu_input import Imu
from ultrasonic_input import Ultrasonic
import camera_convert


class Car:
    width = 45.6
    length = 42
    hole_width = 13
    hole_length = 26
    left_wheel = Vec2d(-5, -20.1)
    right_wheel = Vec2d(-5, 20.1)

    mass = 1
    moment = 1000
    parallel_drag = 0.01
    perpendicular_drag = 0.1
    angular_drag = 5000
    friction = 0.5
    elasticity = 0.5
    left_wheel_max_speed = right_wheel_max_speed = 42  # 每秒一个车身
    left_wheel_max_force = right_wheel_max_force = 5
    left_wheel_force = right_wheel_force = 0

    camera_capturing = False

    def __init__(self, room: Room, color, x, y, camera_state: camera_convert.CameraState):
        self.room = room

        self.body = pymunk.Body(mass=self.mass, moment=self.moment)

        l = self.length
        w = self.width
        l0 = self.hole_length
        w0 = self.hole_width

        self.shapes = [
            pymunk.Poly(self.body, [(-l / 2, -w / 2), (-l / 2, w / 2), (l / 2 - l0, w / 2), (l / 2 - l0, -w / 2), ]),
            pymunk.Poly(self.body, [(l / 2 - l0, -w / 2), (l / 2 - l0, -w0 / 2), (l / 2, -w0 / 2), (l / 2, -w / 2), ]),
            pymunk.Poly(self.body, [(l / 2 - l0, w / 2), (l / 2 - l0, w0 / 2), (l / 2, w0 / 2), (l / 2, w / 2), ]),
        ]

        for s in self.shapes:
            s.color = color
            s.friction = self.friction
            s.elasticity = self.elasticity

        self.body.position = (x, y)

        self.camera = Camera(self, camera_state)
        self.imu = Imu(self)
        self.ultrasonic = Ultrasonic(self)

        cs = camera_state
        cb1, cx1, cy1 = camera_convert.img2space(cs, 0, 0)
        cb2, cx2, cy2 = camera_convert.img2space(cs, cs.res_h, 0)
        cb3, cx3, cy3 = camera_convert.img2space(cs, cs.res_h, cs.res_v)
        cb4, cx4, cy4 = camera_convert.img2space(cs, 0, cs.res_v)
        if not cb1:
            cx1, cy1 = cx4 + (cx4 - cx1) / np.sqrt((cx4 - cx1) ** 2 + (cy4 - cy1) ** 2) * 800, \
                       cy4 + (cy4 - cy1) / np.sqrt((cx4 - cx1) ** 2 + (cy4 - cy1) ** 2) * 800
        if not cb2:
            cx2, cy2 = cx3 + (cx3 - cx2) / np.sqrt((cx3 - cx2) ** 2 + (cy3 - cy2) ** 2) * 800, \
                       cy3 + (cy3 - cy2) / np.sqrt((cx3 - cx2) ** 2 + (cy3 - cy2) ** 2) * 800

        self.camera_range = pymunk.Poly(self.body, [(cx1, cy1), (cx2, cy2), (cx3, cy3), (cx4, cy4)])

        self.camera_range.color = (255, 255, 255, 32)
        self.camera_range.sensor = True

        self.algorithm = Algorithm(self)

        self.room.space.add(self.body, *self.shapes, self.camera_range)
        self.room.cars.append(self)

    def physics(self):
        left_wheel_relative_velocity = self.body.velocity.rotated(-self.body.angle) \
                                       + self.body.angular_velocity * self.left_wheel.rotated_degrees(90)
        right_wheel_relative_velocity = self.body.velocity.rotated(-self.body.angle) \
                                        + self.body.angular_velocity * self.right_wheel.rotated_degrees(90)
        self.body.apply_impulse_at_local_point(
            (self.left_wheel_force - self.parallel_drag * left_wheel_relative_velocity[0]) * Vec2d(1, 0)
            + (- self.perpendicular_drag * left_wheel_relative_velocity[1]) * Vec2d(0, 1), self.left_wheel)
        self.body.apply_impulse_at_local_point(
            (self.right_wheel_force - self.parallel_drag * right_wheel_relative_velocity[0]) * Vec2d(1, 0)
            + (- self.perpendicular_drag * right_wheel_relative_velocity[1]) * Vec2d(0, 1), self.right_wheel)

        self.body.torque -= self.body.angular_velocity * self.angular_drag
        self.left_wheel_force = self.right_wheel_force = 0

    def output(self, wheel_outputs):
        left_wheel_relative_velocity = self.body.velocity.rotated(-self.body.angle) \
                                       + self.body.angular_velocity * self.left_wheel.rotated_degrees(90)
        right_wheel_relative_velocity = self.body.velocity.rotated(-self.body.angle) \
                                        + self.body.angular_velocity * self.right_wheel.rotated_degrees(90)

        if left_wheel_relative_velocity[0] < self.left_wheel_max_speed * wheel_outputs[0]:
            self.left_wheel_force = self.left_wheel_max_force
        else:
            self.left_wheel_force = -self.left_wheel_max_force
        if right_wheel_relative_velocity[0] < self.right_wheel_max_speed * wheel_outputs[1]:
            self.right_wheel_force = self.right_wheel_max_force
        else:
            self.right_wheel_force = -self.right_wheel_max_force
