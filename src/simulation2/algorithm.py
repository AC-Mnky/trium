import numpy as np
from pymunk.vec2d import Vec2d


class Algorithm:
    def __init__(self, car):
        self.car = car

        self.predicted_x = None
        self.predicted_y = None
        self.predicted_angle = None
        self.last_update_time = 0

        self.predicted_reds = []

        self.output = (0, 0)

    def update(self, camera_input, encoder_input, imu_input, ultrasonic_input):
        dt = self.car.room.time - self.last_update_time
        self.last_update_time = self.car.room.time

        # infer current movement from encoder
        inferred_angular_speed = (encoder_input[0] - encoder_input[1]) / self.car.distance_between_wheels
        inferred_relative_velocity = Vec2d((encoder_input[0] + encoder_input[1]) / 2,
                                           -inferred_angular_speed * self.car.wheel_x_offset)

        # predict current position and angle
        if self.predicted_angle is not None:
            self.predicted_angle += dt * inferred_angular_speed
            inferred_velocity = inferred_relative_velocity.rotated(self.predicted_angle)
            if self.predicted_x is not None:
                self.predicted_x += dt * inferred_velocity[0]
            if self.predicted_y is not None:
                self.predicted_y += dt * inferred_velocity[1]
        else:
            self.predicted_x = self.predicted_y = None

        # analyze camera input
        if camera_input is not None:
            print()
            print('delta_x: ', (self.predicted_x or np.nan) - self.car.body.position[0])
            print('delta_y: ', (self.predicted_y or np.nan) - self.car.body.position[1])
            print('delta_θ: ', (self.predicted_angle or np.nan) - self.car.body.angle)
            if camera_input[2] is not None:
                self.predicted_x = camera_input[2]
            if camera_input[3] is not None:
                self.predicted_y = camera_input[3]
            if camera_input[4] is not None:
                self.predicted_angle = camera_input[4]

            if len(camera_input[0] + camera_input[1]) > 0:
                self.output = (1, 1)
            else:
                self.output = (1, -1)




# class Algorithm:
#     def __init__(self, car):
#         self.car = car
#         self.old_angle = None
#         self.stuck_pos = car.body.position
#         self.stuck_time = 0
#
#     def calc(self, camera_info):
#         self.stuck_time += 1
#         if self.stuck_time > 420:
#             self.stuck_time = rand.randint(150, 250)
#         elif self.stuck_time > 360:
#             return 1, 1
#         elif self.stuck_time > 300:
#             return 1, -1
#         if (self.car.body.position - self.stuck_pos).length > self.car.length:
#             self.stuck_pos = self.car.body.position
#             self.stuck_time = 0
#         if not (
#                 room_left + 30 < self.car.body.position.x < room_right - 30 and room_top + 30 < self.car.body.position.y
#                 < room_bottom - 30):
#             self.old_angle = None
#         for x in camera_info.seen_obstacles + camera_info.seen_cars:
#             if (x - self.car.body.position).length < 60:
#                 if self.old_angle is None:
#                     self.old_angle = self.car.body.angle
#                 return -1, 1
#         if self.old_angle is not None:
#             a = self.old_angle - self.car.body.angle
#             a -= round(a / np.tau) * np.tau
#             if a > 0.1:
#                 return 1, -0.25
#             elif a < -0.1:
#                 return -0.25, 1
#             else:
#                 self.old_angle = None
#                 return 1, 1
#         if len(camera_info.seen_reds) == 0:
#             self.old_angle = None
#             return -1, 1
#         pos = Vec2d(0, 0)
#         shortest = 1000
#         for r1 in camera_info.seen_reds:
#             if (r1 - self.car.body.position).length < shortest:
#                 shortest = (r1 - self.car.body.position).length
#                 pos = r1
#         a = (pos - self.car.body.position).angle - self.car.body.angle
#         a -= round(a / np.tau) * np.tau
#         if a > 0.1:
#             return 1, -1
#         elif a < -0.1:
#             return -1, 1
#         else:
#             return 1, 1
