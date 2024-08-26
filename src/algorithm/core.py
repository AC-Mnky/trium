import numpy as np
from struct import unpack
from pymunk.vec2d import Vec2d

ENABLE_INFER_POSITION_FROM_WALLS = False  # True

np.tau = 2 * np.pi

PWM_PERIOD = 100
DISTANCE_PER_ENCODER = 33 * np.tau / 44 / 20.4
WIDTH = 154
LENGTH = 205
COM_TO_CAR_BACK = 87  # center of mass to car back
WIDTH_WITH_WHEELS = 208
# hole_width = 68
WHEEL_X_OFFSET = -COM_TO_CAR_BACK + 98
DISTANCE_BETWEEN_WHEELS = 182
LEFT_WHEEL = Vec2d(WHEEL_X_OFFSET, -DISTANCE_BETWEEN_WHEELS / 2)
RIGHT_WHEEL = Vec2d(WHEEL_X_OFFSET, DISTANCE_BETWEEN_WHEELS / 2)

ROOM_X = 3000
ROOM_Y = 2000

INITIAL_CORD_X = 200
INITIAL_CORD_Y = 200
INITIAL_ANGLE = 0

MAX_CORD_DIFFERENCE = 100
MAX_CORD_RELATIVE_DIFFERENCE = 0.2
MAX_ANGLE_DIFFERENCE = 0.4
GOOD_SEEN_WALL_LENGTH = 500

MERGE_RADIUS = 75
CONTACT_CENTER_TO_BACK = 180
CONTACT_RADIUS = 40
SEEN_ITEMS_DECAY_EXPONENTIAL = 0.5
ALL_ITEMS_DECAY_EXPONENTIAL = 0.999
DELETE_VALUE = 0.2
INTEREST_ADDITION = 5
INTEREST_MAXIMUM = 30
AIM_ANGLE = 0.05
ROOM_MARGIN = 100

MOTOR_SPEED = 0.9


def calc_weight(cord_difference: float, angle_difference: float, distance_to_wall: float,
                seen_wall_length: float) -> float:
    weight = 0.5
    if np.abs(cord_difference) > MAX_CORD_DIFFERENCE:
        return 0
    if np.abs(cord_difference / distance_to_wall) > MAX_CORD_RELATIVE_DIFFERENCE:
        return 0
    if np.abs(angle_difference) > MAX_ANGLE_DIFFERENCE:
        return 0
    if seen_wall_length < GOOD_SEEN_WALL_LENGTH:
        weight *= seen_wall_length / GOOD_SEEN_WALL_LENGTH
    return weight


def merge_item_prediction(dictionary):
    while True:
        substitution = None

        for k1, v1 in dictionary.items():

            neighbour_of_k1 = {}
            for k2, v2 in dictionary.items():
                if v1[1] == v2[1] and k1.get_distance(k2) < MERGE_RADIUS:
                    neighbour_of_k1[k2] = v2

            if len(neighbour_of_k1) > 1:
                pos_sum = Vec2d(0, 0)
                value_sum = 0
                interest_max = 0
                for k2, v2 in neighbour_of_k1.items():
                    pos_sum += k2 * v2[0]
                    value_sum += v2[0]
                    interest_max = max(interest_max, v2[2])
                pos_avg = pos_sum / value_sum
                substitution = (neighbour_of_k1, pos_avg, value_sum, v1[1], interest_max)
                break

        if substitution is None:
            break

        for k in substitution[0]:
            dictionary.pop(k)
        dictionary[substitution[1]] = list(substitution[2:])


class Core:
    def __init__(self, time: float):
        self.predicted_cords = Vec2d(INITIAL_CORD_X, INITIAL_CORD_Y)
        self.predicted_angle = INITIAL_ANGLE
        self.last_update_time = time

        self.predicted_items: dict[Vec2d, list[float, int, float]] = {}

        self.status_code = 1
        self.motor = [0.0, 0.0]
        self.brush = False
        self.back_open = False
        self.motor_PID = [[15, 10, 40, 10, 0, 10, 5, 0], [15, 10, 40, 10, 0, 10, 5, 0]]

        self.stm_input = bytes((0,) * 96)

    # There is no reset function. When you want to reset the core, just create a new object.

    def get_closest_item(self) -> Vec2d or None:
        closest = None
        closest_distance = np.inf
        for x, v in self.predicted_items.items():
            x_distance = x.get_distance(self.predicted_cords) - v[2]
            if x_distance < closest_distance:
                closest = x
                closest_distance = x_distance
        return closest

    def infer_position_from_walls(self, walls):
        vote_x_angle = []
        vote_y_angle = []
        for w in walls:
            point_1, point_2 = Vec2d(w[0][0], w[0][1]), Vec2d(w[1][0], w[1][1])
            line = point_2 - point_1
            perpendicular = point_1 - point_1.projection(line)
            vote_x_angle.append(
                (ROOM_X - perpendicular.length, -perpendicular.angle, perpendicular.length, line.length))
            vote_x_angle.append(
                (perpendicular.length, np.pi - perpendicular.angle, perpendicular.length, line.length))
            vote_y_angle.append(
                (ROOM_Y - perpendicular.length, np.pi / 2 - perpendicular.angle, perpendicular.length,
                 line.length))
            vote_y_angle.append(
                (perpendicular.length, 3 * np.pi / 2 - perpendicular.angle, perpendicular.length, line.length))

        x_weight_sum = y_weight_sum = angle_weight_sum = 1
        x_diff_sum = y_diff_sum = angle_diff_sum = 0

        for v in vote_x_angle:
            x_diff = v[0] - self.predicted_cords[0]
            angle_diff = angle_subtract(v[1], self.predicted_angle)
            weight = calc_weight(x_diff, angle_diff, v[2], v[3])

            x_weight_sum += weight
            x_diff_sum += x_diff
            angle_weight_sum += weight
            angle_diff_sum += angle_diff

        for v in vote_y_angle:
            y_diff = v[0] - self.predicted_cords[0]
            angle_diff = angle_subtract(v[1], self.predicted_angle)
            weight = calc_weight(y_diff, angle_diff, v[2], v[3])

            y_weight_sum += weight
            y_diff_sum += y_diff
            angle_weight_sum += weight
            angle_diff_sum += angle_diff

        x_diff_average = x_diff_sum / x_weight_sum
        y_diff_average = y_diff_sum / y_weight_sum
        angle_diff_average = angle_diff_sum / angle_weight_sum

        self.predicted_cords += x_diff_average, y_diff_average
        self.predicted_angle += angle_diff_average

    def update(self,
               time: float,
               stm32_input: bytes,
               imu_input: ...,
               camera_input: tuple[float, list, list, list] | None) -> None:

        dt = time - self.last_update_time
        self.last_update_time = time

        if stm32_input is not None:
            self.stm_input = stm32_input

        # infer current relative movement from encoder
        encoder = unpack('<h', self.stm_input[68:70])[0], unpack('<h', self.stm_input[36:38])[0]
        inferred_angular_speed = (encoder[0] - encoder[1]) / DISTANCE_BETWEEN_WHEELS
        inferred_relative_velocity = Vec2d((encoder[0] + encoder[1]) / 2, -inferred_angular_speed * WHEEL_X_OFFSET)

        # predict current position
        self.predicted_angle += dt * inferred_angular_speed
        inferred_velocity = inferred_relative_velocity.rotated(self.predicted_angle)
        self.predicted_cords += inferred_velocity

        # analyze camera input
        if camera_input is not None:
            camera_time, camera_reds, camera_yellows, camera_walls = camera_input

            if ENABLE_INFER_POSITION_FROM_WALLS:
                self.infer_position_from_walls(camera_walls)

            for red in camera_reds:
                cords = red.rotated(self.predicted_angle) + self.predicted_cords
                if ROOM_MARGIN < cords[0] < ROOM_X - ROOM_MARGIN and ROOM_MARGIN < cords[1] < ROOM_Y - ROOM_MARGIN:
                    self.predicted_items[cords] = [self.predicted_items.get(cords, (0, 0))[0] + 2, 0, 0]
            for yellow in camera_yellows:
                cords = yellow.rotated(self.predicted_angle) + self.predicted_cords
                if ROOM_MARGIN < cords[0] < ROOM_X - ROOM_MARGIN and ROOM_MARGIN < cords[1] < ROOM_Y - ROOM_MARGIN:
                    self.predicted_items[cords] = [self.predicted_items.get(cords, (0, 1))[0] + 3, 1, 0]

            merge_item_prediction(self.predicted_items)

            # TODO: seen items decay

        # decay all items and delete items with low value
        contact_center = self.predicted_cords + Vec2d(1, 0).rotated(self.predicted_angle) * (
                CONTACT_CENTER_TO_BACK - COM_TO_CAR_BACK)
        items_to_delete = []
        for item in self.predicted_items:
            self.predicted_items[item][0] *= ALL_ITEMS_DECAY_EXPONENTIAL
            if item.get_distance(contact_center) < CONTACT_RADIUS or self.predicted_items[item][0] < DELETE_VALUE:
                items_to_delete.append(item)
        for item in items_to_delete:
            self.predicted_items.pop(item)

        # go toward closest item
        item = self.get_closest_item()
        if item is None:
            self.motor = [MOTOR_SPEED, -MOTOR_SPEED]
        else:
            self.predicted_items[item][2] = min(self.predicted_items[item][2] + INTEREST_ADDITION,
                                                INTEREST_MAXIMUM)
            item_angle = angle_subtract((item - self.predicted_cords).angle, self.predicted_angle)
            if item_angle > AIM_ANGLE:
                self.motor = [MOTOR_SPEED, -MOTOR_SPEED]
            elif item_angle < -AIM_ANGLE:
                self.motor = [-MOTOR_SPEED, MOTOR_SPEED]
            else:
                self.motor = [MOTOR_SPEED, MOTOR_SPEED]

    def get_output(self) -> ...:
        output = (
                [
                    128,
                    self.status_code,
                    int(self.motor[1] * PWM_PERIOD),
                    int(self.motor[0] * PWM_PERIOD),
                    int(self.brush),
                    int(self.back_open),
                    0,
                    0,
                ]
                + self.motor_PID[1]
                + self.motor_PID[0]
        )

        if self.status_code > 0:
            self.status_code = 0

        for i in range(len(output)):
            if output[i] < 0:
                output[i] += 256

        return bytes(output)


def angle_subtract(angle1: float, angle2: float) -> float:
    diff = angle1 - angle2
    diff -= round(diff / np.tau) * np.tau
    return diff
