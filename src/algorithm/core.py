import numpy as np
from struct import unpack

ENABLE_INFER_POSITION_FROM_WALLS = False  # True

np.tau = 2 * np.pi

PWM_PERIOD = 100
DISTANCE_PER_ENCODER = 33 * np.tau / 44 / 20.4
WIDTH = 154
LENGTH = 205
CM_TO_CAR_BACK = 87  # center of mass to car back
WIDTH_WITH_WHEELS = 208
# hole_width = 68
WHEEL_X_OFFSET = -CM_TO_CAR_BACK + 98
DISTANCE_BETWEEN_WHEELS = 178.3
LEFT_WHEEL = (WHEEL_X_OFFSET, -DISTANCE_BETWEEN_WHEELS / 2)
RIGHT_WHEEL = (WHEEL_X_OFFSET, DISTANCE_BETWEEN_WHEELS / 2)

ROOM_X = 3000
ROOM_Y = 2000

INITIAL_CORD_X = 200
INITIAL_CORD_Y = ROOM_Y - 200
INITIAL_ANGLE = 0

MAX_CORD_DIFFERENCE = 100
MAX_CORD_RELATIVE_DIFFERENCE = 0.2
MAX_ANGLE_DIFFERENCE = 0.4
GOOD_SEEN_WALL_LENGTH = 500

MERGE_RADIUS = 75
CONTACT_CENTER_TO_BACK = 180
CONTACT_RADIUS = 40
SEEN_ITEMS_DECAY_EXPONENTIAL = 0.5
ALL_ITEMS_DECAY_EXPONENTIAL = 1
DELETE_VALUE = 0.2
INTEREST_ADDITION = 5
INTEREST_MAXIMUM = 30
AIM_ANGLE = 0.2
ROOM_MARGIN = 200

MOTOR_SPEED = 0.5


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


def merge_item_prediction(dictionary) -> None:
    while True:
        substitution = None

        for k1, v1 in dictionary.items():

            neighbour_of_k1 = {}
            for k2, v2 in dictionary.items():
                if v1[1] == v2[1] and get_distance(k1, k2) < MERGE_RADIUS:
                    neighbour_of_k1[k2] = v2

            if len(neighbour_of_k1) > 1:
                pos_sum = (0, 0)
                value_sum = 0
                interest_max = 0
                for k2, v2 in neighbour_of_k1.items():
                    pos_sum = vec_add(pos_sum, vec_multiply(k2, v2[0]))
                    value_sum += v2[0]
                    interest_max = max(interest_max, v2[2])
                pos_avg = (pos_sum[0] / value_sum, pos_sum[1] / value_sum)
                substitution = (neighbour_of_k1, pos_avg, value_sum, v1[1], interest_max)
                break

        if substitution is None:
            break

        for k in substitution[0]:
            dictionary.pop(k)
        dictionary[substitution[1]] = list(substitution[2:])


class Core:
    def __init__(self, time: float):

        self.last_update_time = time

        self.status_code = 1
        self.motor = [0.0, 0.0].copy()
        self.brush = False
        self.back_open = False
        self.motor_PID = [[15, 10, 40, 10, 0, 10, 5, 0], [15, 10, 40, 10, 0, 10, 5, 0]].copy()

        self.stm_input = bytes((0,) * 96)
        self.imu_input = None
        self.camera_input = None

        self.predicted_cords = (INITIAL_CORD_X, INITIAL_CORD_Y)
        self.predicted_angle = INITIAL_ANGLE

        self.predicted_vertices = [[(0.0, 0.0), (0.0, 0.0)], [(0.0, 0.0), (0.0, 0.0)]].copy()

        self.predicted_items: dict[tuple[float, float], list[float, int, float]] = {}
        self.walls: list[tuple[tuple[float, float], tuple[float, float]]] = []

        # There is no reset function. When you want to reset the _core, just create a new object.

    def get_closest_item(self) -> tuple[float, float] | None:
        closest = None
        closest_distance = np.inf
        for x, v in self.predicted_items.items():
            x_distance = get_distance(x, self.predicted_cords) - v[2]
            if x_distance < closest_distance:
                closest = x
                closest_distance = x_distance
        return closest

    def infer_position_from_walls(self) -> None:
        vote_x_angle = []
        vote_y_angle = []
        for w in self.walls:
            point_1, point_2 = (w[0][0], w[0][1]), (w[1][0], w[1][1])
            line = vec_subtract(point_2, point_1)
            line_length = get_length(line)
            perpendicular = vec_subtract(point_1, projection(point_1, line))
            distance = get_length(perpendicular)
            angle = get_angle(perpendicular)
            vote_x_angle.append((ROOM_X - distance, -angle, distance, line_length))
            vote_x_angle.append((distance, np.pi - angle, distance, line_length))
            vote_y_angle.append((ROOM_Y - distance, np.pi / 2 - angle, distance, line_length))
            vote_y_angle.append((distance, 3 * np.pi / 2 - angle, distance, line_length))

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

    # Get realtime data from other modules
    def update(self,
               time: float,
               stm32_input: bytes,
               imu_input: tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]] | None,
               camera_input: tuple[float, list[tuple[float, float]], list[tuple[float, float]], list[
                   tuple[tuple[float, float], tuple[float, float]]]] | None) -> None:

        # calculate the time interval between two updates
        dt = time - self.last_update_time
        self.last_update_time = time

        # update all the input data
        if stm32_input is not None:
            self.stm_input = stm32_input
        if imu_input is not None:
            self.imu_input = imu_input
        if camera_input is not None:
            self.camera_input = camera_input

        if self.status_code > 0:
            self.status_code = 0

        """
        infer current relative movement from encoder.
        "inferred_angular_speed" = speed of rotating around the center of the car
        "inferred_relative_velocity" = speed of the center of the car
        paras have to be modified: WHEEL_X_OFFSET
        """
        
        encoder = unpack('<h', self.stm_input[68:70])[0], unpack('<h', self.stm_input[36:38])[0]
        inferred_angular_speed = (encoder[1] - encoder[0]) * DISTANCE_PER_ENCODER / DISTANCE_BETWEEN_WHEELS / dt
        inferred_relative_velocity = (
            (encoder[0] + encoder[1]) * DISTANCE_PER_ENCODER / 2 / dt, -inferred_angular_speed * WHEEL_X_OFFSET)

        # predict current position
        self.predicted_angle += dt * inferred_angular_speed
        inferred_velocity = rotated(inferred_relative_velocity, self.predicted_angle)
        self.predicted_cords = vec_add(vec_multiply(inferred_velocity, dt), self.predicted_cords)

        # calculate vertices
        for i in 0, 1:
            for j in 0, 1:
                self.predicted_vertices[i][j] = vec_add(
                    rotated((i * LENGTH - CM_TO_CAR_BACK, (j - 0.5) * WIDTH), self.predicted_angle),
                    self.predicted_cords)

        # analyze camera input
        if camera_input is not None:
            camera_time, camera_reds, camera_yellows, camera_walls = camera_input

            self.walls = camera_walls
            if ENABLE_INFER_POSITION_FROM_WALLS:
                self.infer_position_from_walls()

            for red in camera_reds:
                cords = vec_add(rotated(red, self.predicted_angle), self.predicted_cords)
                if ROOM_MARGIN < cords[0] < ROOM_X - ROOM_MARGIN and ROOM_MARGIN < cords[1] < ROOM_Y - ROOM_MARGIN:
                    self.predicted_items[cords] = [self.predicted_items.get(cords, (0, 0))[0] + 2, 0, 0]
            for yellow in camera_yellows:
                cords = vec_add(rotated(yellow, self.predicted_angle), self.predicted_cords)
                if ROOM_MARGIN < cords[0] < ROOM_X - ROOM_MARGIN and ROOM_MARGIN < cords[1] < ROOM_Y - ROOM_MARGIN:
                    self.predicted_items[cords] = [self.predicted_items.get(cords, (0, 1))[0] + 3, 1, 0]

            merge_item_prediction(self.predicted_items)

            # TODO: seen items decay

        # decay all items and delete items with low value
        contact_center = vec_multiply(vec_add(self.predicted_cords, rotated((1, 0), self.predicted_angle)), (
                CONTACT_CENTER_TO_BACK - CM_TO_CAR_BACK))
        items_to_delete = []
        for item in self.predicted_items:
            self.predicted_items[item][0] *= ALL_ITEMS_DECAY_EXPONENTIAL
            if get_distance(item, contact_center) < CONTACT_RADIUS or self.predicted_items[item][0] < DELETE_VALUE:
                items_to_delete.append(item)
        for item in items_to_delete:
            self.predicted_items.pop(item)

        # go toward the closest item
        item = self.get_closest_item()
        if item is None:
            self.motor = [0.25 * MOTOR_SPEED, -0.25 * MOTOR_SPEED]
        else:
            self.predicted_items[item][2] = min(self.predicted_items[item][2] + INTEREST_ADDITION,
                                                INTEREST_MAXIMUM)
            item_angle = angle_subtract(get_angle(vec_subtract(item, self.predicted_cords)), self.predicted_angle)
            if item_angle > AIM_ANGLE:
                self.motor = [MOTOR_SPEED, -MOTOR_SPEED]
            elif item_angle < -AIM_ANGLE:
                self.motor = [-MOTOR_SPEED, MOTOR_SPEED]
            else:
                self.motor = [MOTOR_SPEED, MOTOR_SPEED]

    #Give commands to the STM32
    def get_output(self) -> bytes:
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

        for i in range(len(output)):
            if output[i] < 0:
                output[i] += 256

        return bytes(output)


def get_distance(point1: tuple[float, float], point2: tuple[float, float]) -> float:
    return get_length(vec_subtract(point1, point2))


def get_length(vec: tuple[float, float]) -> float:
    return np.sqrt(vec[0] * vec[0] + vec[1] * vec[1])


def get_angle(vec: tuple[float, float]) -> float:
    if vec[0] == 0 and vec[1] == 0:
        return 0
    return np.arctan2(vec[1], vec[0])


def vec_add(vec1: tuple[float, float], vec2: tuple[float, float]) -> tuple[float, float]:
    return vec1[0] + vec2[0], vec1[1] + vec2[1]


def vec_subtract(vec1: tuple[float, float], vec2: tuple[float, float]) -> tuple[float, float]:
    return vec1[0] - vec2[0], vec1[1] - vec2[1]


def vec_multiply(vec: tuple[float, float], k: float) -> tuple[float, float]:
    return vec[0] * k, vec[1] * k


def angle_subtract(angle1: float, angle2: float) -> float:
    diff = angle1 - angle2
    diff -= round(diff / np.tau) * np.tau
    return diff


def projection(vec1: tuple[float, float], vec2: tuple[float, float]) -> tuple[float, float]:
    length_square = vec2[0] * vec2[0] + vec2[1] * vec2[1]
    if length_square == 0.0:
        return 0, 0
    dot = vec1[0] * vec2[0] + vec1[1] * vec2[1]
    new_length = dot / length_square
    return vec2[0] * new_length, vec2[1] * new_length


def rotated(vec: tuple[float, float], angle_radians: float) -> tuple[float, float]:
    cos = np.cos(angle_radians)
    sin = np.sin(angle_radians)
    x = vec[0] * cos - vec[1] * sin
    y = vec[0] * sin + vec[1] * cos
    return x, y
