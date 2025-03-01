from pathlib import Path

import camera_convert
import core
import cv2
import find_color
import matplotlib.pyplot as plt
import numpy as np
from camera_convert import CameraState

DIFF_LEN = 0.01
IDEN_TIMES = 150
DATA_NUM = 8
MINIMUM_ERROR = 100

MAX_CHANGE = 1
CHANGING_RANGE = [5, 100, 100, 20, 0, 0, 10, 10]
ORIGIN_VALUE = [90, 18, -442, 55.9, 0.9, 0, 51.45, 51.09]

ENABLE_SMOOTH_FACTOR = True
OVERLAY_DISTANCE = 40  # The distance criterion of endpoints, deciding whether to merge two walls
LAMBDA = 0


def calculate_walls(cam: CameraState, image: cv2.UMat) -> np.ndarray:
    """
    Use given images to calculate the walls estimated by the algorithm.

    Args:
        cam (CameraState): The camera state object.
        image (cv2.UMat): The image to be processed.

    Returns:
        distances (np.ndarray): The distances of the walls in the image.
    """
    walls_in_image = find_color.find_wall_bottom_p(image)

    if walls_in_image is not None:
        walls_raw = [
            (
                camera_convert.img2space(cam, wall[0][0], wall[0][1])[1:],
                camera_convert.img2space(cam, wall[0][2], wall[0][3])[1:],
            )
            for wall in walls_in_image
        ]

    # print(len(walls_raw))

    walls = [walls_raw[0]]
    # merge walls if they are too close. here two endpoints are used to determine "close".
    for w_i in walls_raw:
        if not (
            core.get_length(core.vec_sub(walls[0][0], w_i[0])) < OVERLAY_DISTANCE
            and core.get_length(core.vec_sub(walls[0][1], w_i[1])) < OVERLAY_DISTANCE
        ):
            walls.append(w_i)
            break

    distances_raw = []
    # angles_raw = []

    for w in walls:
        point_1, point_2 = (w[0][0], w[0][1]), (w[1][0], w[1][1])
        line = core.vec_sub(point_2, point_1)
        perpendicular = core.vec_sub(point_1, core.projection(point_1, line))
        distance = core.get_length(perpendicular)
        # angle = c.get_angle(perpendicular)

        distances_raw.append(distance)
        # angles_raw.append(angle)

    if len(distances_raw) > 1:
        if distances_raw[1] > distances_raw[0]:
            distances_raw[0], distances_raw[1] = distances_raw[1], distances_raw[0]
    else:
        distances_raw.append(distances_raw[0])

    # distances = np.array(distances_raw)

    # angles = np.array(angles_raw)

    # distances and angles should be 2 elements long
    # parameters = distances

    return np.array(distances_raw)


def partial_dirivative(
    image: cv2.UMat,
    camera_xyz: tuple[float, float, float],
    camera_rotation: tuple[float, float, float],
    fov: tuple[float, float],
    dt: str,
) -> np.ndarray:
    """
    Calculate the partial derivative of the camera parameters with respect to the given change in dt.

    Args:
        image (cv2.UMat): A cv2.UMat object representing the image.
        camera_xyz (tuple): A tuple representing the camera's x, y, and z coordinates.
        camera_rotation (tuple): A tuple representing the camera's rotation angles (theta, phi, omega).
        fov (tuple): A tuple representing the camera's field of view angles (half_fov_h, half_fov_v).
        dt (string): A string representing the parameter to calculate the partial derivative for.

    Returns:
        partial_dirivative (np.ndarray):
            The partial derivative of the camera parameters with respect to the given change in dt.

    Notes:
        The function uses the DIFF_LEN constant for the change in dt.
    """
    cam_0 = CameraState(camera_xyz, camera_rotation, fov, (320, 240))
    cam_1 = CameraState(camera_xyz, camera_rotation, fov, (320, 240))

    if dt == "x":
        cam_1.x += DIFF_LEN
    elif dt == "y":
        cam_1.y += DIFF_LEN
    elif dt == "z":
        cam_1.z += DIFF_LEN

    elif dt == "theta":
        cam_1.theta += DIFF_LEN
    elif dt == "phi":
        cam_1.phi += DIFF_LEN
    elif dt == "omega":
        cam_1.omega += DIFF_LEN

    elif dt == "half_fov_h":
        cam_1.half_fov_h += DIFF_LEN
    elif dt == "half_fov_v":
        cam_1.half_fov_v += DIFF_LEN
    else:
        print("ERROR")

    cam_1.update()
    # 1/2 distances or angles calculate with two pairs of elements
    parameters_0 = calculate_walls(cam_0, image)
    parameters_1 = calculate_walls(cam_1, image)

    # dt_A1 = d_parameters[2]/STEP_LEN
    # dt_A2 = d_parameters[3]/STEP_LEN
    # return [dt_D1,dt_D2,dt_A1,dt_A2]

    del cam_0
    del cam_1
    # return [dt_D1, dt_D2]
    return (parameters_1 - parameters_0) / DIFF_LEN


def Jacobian(
    image: cv2.UMat,
    camera_xyz: tuple[float, float, float],
    camera_rotation: tuple[float, float, float],
    fov: tuple[float, float],
) -> np.matrix:
    """
    Calculate the Jacobian matrix for a given image with camera position, camera rotation, and field of view.

    Args:
        image (cv2.UMat): The image to be calculated.
        camera_xyz (tuple): The camera position in 3D space (x, y, z).
        camera_rotation (tuple): The camera rotation angles (theta, phi, omega).
        fov (tuple): The field of view angles (half_fov_h, half_fov_v).

    Returns:
        Jacobian (np.matrix): The Jacobian matrix.

    """
    Jacobian = np.asmatrix(
        [
            partial_dirivative(image, camera_xyz, camera_rotation, fov, "x"),
            partial_dirivative(image, camera_xyz, camera_rotation, fov, "y"),
            partial_dirivative(image, camera_xyz, camera_rotation, fov, "z"),
            partial_dirivative(image, camera_xyz, camera_rotation, fov, "theta"),
            partial_dirivative(image, camera_xyz, camera_rotation, fov, "phi"),
            partial_dirivative(image, camera_xyz, camera_rotation, fov, "omega"),
            partial_dirivative(image, camera_xyz, camera_rotation, fov, "half_fov_h"),
            partial_dirivative(image, camera_xyz, camera_rotation, fov, "half_fov_v"),
        ]
    )
    return Jacobian.T


if __name__ == "__main__":
    current_dir = Path(__file__).parent
    pic_dir = current_dir.parent.parent / "assets/openCV_pic/test_pics"
    image = []
    for i in range(DATA_NUM):
        pic_path = f"{pic_dir}/{i}.jpg"
        try:
            image.append(cv2.imread(pic_path))
        except FileNotFoundError:
            print("cannot open", pic_path)

    camera_xyz_0 = np.array([142, -38, -219])
    camera_rotation_0 = np.array([56.3, 0.9, -0.5])
    fov_0 = np.array([51.45, 51.09])
    resolution = (320, 240)
    E_test = np.array(
        [1180, 350, 1500, 690, 930, 900, 1180, 1100, 1760, 770, 1770, 1300, 2110, 350, 2230, 620]
    )  # Measured position
    p = np.concatenate((camera_xyz_0, camera_rotation_0, fov_0))
    d_p = np.zeros(8)

    dE_list = []

    for i in range(IDEN_TIMES):
        # Generate camera state objects
        print(f"p = {p}")
        cam = CameraState(tuple(p[0:3]), tuple(p[3:6]), tuple(p[6:8]), resolution)

        # Calculate the ideal position with the current parameters
        E_cal = np.array([calculate_walls(cam, image[j]) for j in range(DATA_NUM)]).reshape(-1)
        print(f"calculated E = {E_cal}")

        # Calculate the current error
        d_E = (E_test - E_cal).T
        print(f"|dE| = {np.linalg.norm(d_E)}")
        print(f"dE = {d_E}")

        if np.linalg.norm(d_E) > 3000:
            dE_list.append(3000)
        else:
            dE_list.append(np.linalg.norm(d_E))

        if np.linalg.norm(d_E) < MINIMUM_ERROR:
            break

        # Generate Jacobian matrix (NUM_OF_DATAx16x8)
        J = np.array(
            [Jacobian(image[j], tuple(p[0:3]), tuple(p[3:6]), tuple(p[6:8])) for j in range(DATA_NUM)]
        ).reshape(-1, 8)
        print(f"Jacobian = {J}")

        # Calculate the parameter compensation with the Jacobian matrix and error
        if ENABLE_SMOOTH_FACTOR:
            # Introduce a smooth factor to make the result curve smoother
            J_Tik = np.linalg.inv(J.T @ J + LAMBDA * np.eye(8)) @ J.T
            d_p = np.dot(J_Tik, d_E)
        else:
            d_p = np.dot(np.linalg.pinv(J), d_E)

        # to avoid p becoming too large
        d_p = np.array([np.atan(d_p[i]) for i in range(len(d_p))])
        d_p = MAX_CHANGE * d_p / (np.pi / 2)

        # compensate the paras
        p = np.reshape(p, (1, 8))
        p += d_p
        p = np.reshape(p, (8,))

        # restrict the range of paras
        # for j in range(len(p)):
        #     p[j] = CHANGING_RANGE[j] * math.atan(p[j] - ORIGIN_VALUE[j]) / (math.pi/2)  + ORIGIN_VALUE[j]

        print(f"p = {p}")
        print(f"d_p = {d_p}")
        print(f"loop {i} finished\n")

    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111)
    ax1.plot(dE_list)
    plt.show()
