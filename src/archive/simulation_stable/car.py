import camera_convert
import numpy as np
import pymunk
from camera_input import Camera
from encoder_input import Encoder
from imu_input import Imu
from pymunk.vec2d import Vec2d
from room import Room
from ultrasonic_input import Ultrasonic

from algorithm import Algorithm


class Car:
    width = 154 / 5
    length = 205 / 5
    com_to_car_back = 75 / 5  # center of mass to car back
    width_with_wheels = 208 / 5
    hole_width = 67 / 5
    hole_length = length - 10 / 5
    brush_effective_length = 90 / 5
    wheel_x_offset = - com_to_car_back + 98 / 5
    distance_between_wheels = (width + width_with_wheels) / 2
    left_wheel = Vec2d(wheel_x_offset, -distance_between_wheels / 2)
    right_wheel = Vec2d(wheel_x_offset, distance_between_wheels / 2)

    mass = 1
    moment = 1000
    parallel_drag = 0.01
    perpendicular_drag = 0.1
    angular_drag = 5000
    friction = 0.5
    elasticity = 0.5
    brush_force = 0.1
    left_wheel_max_speed = right_wheel_max_speed = 42  # 每秒一个车身
    left_wheel_max_force = right_wheel_max_force = 5
    left_wheel_force = right_wheel_force = 0

    camera_capturing = False

    def __init__(self, room: Room, color, x, y, angle, camera_state: camera_convert.CameraState):
        self.room = room

        self.body = pymunk.Body(mass=self.mass, moment=self.moment)

        l = self.length
        w = self.width
        lc = self.com_to_car_back
        l0 = self.hole_length
        w0 = self.hole_width
        e = self.brush_effective_length

        self.shapes = [
            pymunk.Poly(self.body, [(-lc, -w0 / 2), (-lc, w0 / 2), (-lc + l - l0, w0 / 2), (-lc + l - l0, -w0 / 2)]),
            pymunk.Poly(self.body, [(-lc, -w / 2), (-lc, -w0 / 2), (-lc + l, -w0 / 2), (-lc + l, -w / 2)]),
            pymunk.Poly(self.body, [(-lc, w / 2), (-lc, w0 / 2), (-lc + l, w0 / 2), (-lc + l, w / 2), ]),
        ]

        for s in self.shapes:
            s.color = color
            s.friction = self.friction
            s.elasticity = self.elasticity

        self.body.position = (x, y)
        self.body.angle = angle

        self.brush = pymunk.Poly(self.body,
                                 [(-lc + l - e, -w0 / 2), (-lc + l - e, w0 / 2), (-lc + l, w0 / 2), (-lc + l, -w0 / 2)])
        self.brush.sensor = True

        self.camera = Camera(self, camera_state)
        self.encoder = Encoder(self)
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

        self.room.space.add(self.body, *self.shapes, self.brush, self.camera_range)
        self.room.cars.append(self)

    def physics(self):
        left_wheel_relative_velocity, right_wheel_relative_velocity = self.get_relative_velocity()

        self.body.apply_impulse_at_local_point(
            (self.left_wheel_force - self.parallel_drag * left_wheel_relative_velocity[0]) * Vec2d(1, 0)
            + (- self.perpendicular_drag * left_wheel_relative_velocity[1]) * Vec2d(0, 1), self.left_wheel)
        self.body.apply_impulse_at_local_point(
            (self.right_wheel_force - self.parallel_drag * right_wheel_relative_velocity[0]) * Vec2d(1, 0)
            + (- self.perpendicular_drag * right_wheel_relative_velocity[1]) * Vec2d(0, 1), self.right_wheel)

        self.body.torque -= self.body.angular_velocity * self.angular_drag
        self.left_wheel_force = self.right_wheel_force = 0

        # brush
        for x in self.room.reds + self.room.yellows:
            if x is not None and len(self.brush.shapes_collide(x.shape).points) > 0:
                force = Vec2d(-self.brush_force, 0).rotated(self.body.angle)
                x.body.apply_impulse_at_world_point(force, x.body.position)
                self.body.apply_impulse_at_world_point(-force, x.body.position)

    def output(self, wheel_outputs: tuple[float, float], back_open: bool):
        left_wheel_relative_velocity, right_wheel_relative_velocity = self.get_relative_velocity()

        left_speed_diff = left_wheel_relative_velocity[0] - self.left_wheel_max_speed * wheel_outputs[0]
        if left_speed_diff < -0.1 * self.left_wheel_max_speed:
            self.left_wheel_force = self.left_wheel_max_force
        elif left_speed_diff > 0.1 * self.left_wheel_max_speed:
            self.left_wheel_force = -self.left_wheel_max_force
        else:
            self.left_wheel_force = 0

        right_speed_diff = right_wheel_relative_velocity[0] - self.right_wheel_max_speed * wheel_outputs[1]
        if right_speed_diff < -0.1 * self.right_wheel_max_speed:
            self.right_wheel_force = self.right_wheel_max_force
        elif right_speed_diff > 0.1 * self.right_wheel_max_speed:
            self.right_wheel_force = -self.right_wheel_max_force
        else:
            self.right_wheel_force = 0

        self.shapes[0].sensor = back_open

    def get_relative_velocity(self):
        return self.body.velocity.rotated(
            -self.body.angle) + self.body.angular_velocity * self.left_wheel.rotated_degrees(90), \
               self.body.velocity.rotated(
                   -self.body.angle) + self.body.angular_velocity * self.right_wheel.rotated_degrees(90)
