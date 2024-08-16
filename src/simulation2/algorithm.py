import numpy as np
import pymunk
from pymunk.vec2d import Vec2d

np.tau = np.pi * 2

merge_radius = 15  # 75mm


def merge_collectable_prediction(dictionary):

    while True:
        substitution = None

        for k1, v1 in dictionary.items():

            neighbour_of_k1 = {}
            for k2, v2 in dictionary.items():
                if v1[1] == v2[1] and k1.get_distance(k2) < merge_radius:
                    neighbour_of_k1[k2] = v2

            if len(neighbour_of_k1) > 1:
                pos_sum = Vec2d(0, 0)
                value_sum = 0
                for k2, v2 in neighbour_of_k1.items():
                    pos_sum += k2 * v2[0]
                    value_sum += v2[0]
                pos_avg = pos_sum / value_sum
                substitution = (neighbour_of_k1, pos_avg, value_sum, v1[1])
                break

        if substitution is None:
            break

        for k in substitution[0]:
            dictionary.pop(k)
        dictionary[substitution[1]] = [substitution[2], substitution[3]]


class Algorithm:
    contact_radius = 20
    aim_angle = 0.05
    seen_decay_exponential = 0.5
    unseen_decay_exponential = 0.999
    delete_value = 0.2

    def __init__(self, car):
        self.car = car

        self.predicted_x = None
        self.predicted_y = None
        self.predicted_angle = None
        self.last_update_time = 0

        self.predicted_collectables: dict[Vec2d, list[float, int]] = {}

        self.output = (0, 0)

    def position_predictable(self) -> bool:
        return self.predicted_angle is not None and self.predicted_x is not None and self.predicted_y is not None

    def predicted_position(self) -> Vec2d:
        return Vec2d(self.predicted_x, self.predicted_y)

    def get_closest_collectable(self) -> Vec2d or None:
        closest = None
        closest_distance = np.inf
        for x in self.predicted_collectables:
            x_distance = x.get_distance(self.predicted_position())
            if x_distance < closest_distance:
                closest = x
                closest_distance = x_distance
        return closest

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

            if self.position_predictable():
                for x in camera_input[0]:
                    pos = x.rotated(self.predicted_angle) + Vec2d(self.predicted_x, self.predicted_y)
                    self.predicted_collectables[pos] = [self.predicted_collectables.get(pos, (0, 0))[0] + 2, 0]
                for y in camera_input[1]:
                    pos = y.rotated(self.predicted_angle) + Vec2d(self.predicted_x, self.predicted_y)
                    self.predicted_collectables[pos] = [self.predicted_collectables.get(pos, (0, 1))[0] + 3, 1]

                merge_collectable_prediction(self.predicted_collectables)

                predicted_camera_range = pymunk.Poly(self.car.room.space.static_body, [
                    (v.rotated(self.predicted_angle) + self.predicted_position()).int_tuple for v in
                    self.car.camera_range.get_vertices()])
                self.car.room.space.add(predicted_camera_range)
                for x in self.predicted_collectables:
                    if predicted_camera_range.point_query(x).distance < 0:
                        self.predicted_collectables[x][0] *= self.seen_decay_exponential
                self.car.room.space.remove(predicted_camera_range)

                print(self.predicted_collectables)
                print(len(self.predicted_collectables))

        to_delete_red = []
        for x in self.predicted_collectables:
            self.predicted_collectables[x][0] *= self.unseen_decay_exponential
            if x.get_distance(self.predicted_position()) < self.contact_radius \
                    or self.predicted_collectables[x][0] < self.delete_value:
                to_delete_red.append(x)
        for x in to_delete_red:
            self.predicted_collectables.pop(x)

        x = self.get_closest_collectable()
        if x is None or not self.position_predictable():
            self.output = (1, -1)
        else:
            x_angle = (x - self.predicted_position()).angle - self.predicted_angle
            x_angle -= round(x_angle / np.tau) * np.tau
            if x_angle > self.aim_angle:
                self.output = (1, -1)
            elif x_angle < -self.aim_angle:
                self.output = (-1, 1)
            else:
                self.output = (1, 1)

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
