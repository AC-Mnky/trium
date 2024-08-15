
# from car import Car


class Algorithm:
    def __init__(self, car):
        self.car = car
        self.movement = (0, 0)

    def get_output(self, camera_input, imu_input, ultrasonic_input):
        if camera_input is not None:
            if len(camera_input[0]) > 0:
                self.movement = (1, 1)
            else:
                self.movement = (1, -1)
        return self.movement

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

