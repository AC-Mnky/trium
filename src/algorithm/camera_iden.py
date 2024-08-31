from pathlib import Path

import camera_convert
import core
import cv2
import find_color
import matplotlib.pyplot as plt
import numpy as np
from camera_convert import CameraState


DIFF_LEN = 0.05
IDEN_TIMES = 400
NUM_OF_DATA = 8
MINIMUM_ERROR = 100
LAM = 0



def calculate_walls(cam: CameraState, image: cv2.UMat):
    walls_in_image = find_color.find_wall_bottom_p(image)

    if walls_in_image is not None:
        walls_raw = [
            (
                camera_convert.img2space(cam, wall[0][0], wall[0][1])[1:],
                camera_convert.img2space(cam, wall[0][2], wall[0][3])[1:],
            )
            for wall in walls_in_image
        ]
        
    print(len(walls_raw))

    walls = [walls_raw[0]]
    # merge near walls
    for w_i in walls_raw:
        if not (
            core.get_length(core.vec_sub(walls[0][0], w_i[0])) < 40
            and core.get_length(core.vec_sub(walls[0][1], w_i[1])) < 40
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


    if(len(distances_raw) > 1):
        if distances_raw[1] > distances_raw[0]:
            distances_raw[0], distances_raw[1] = distances_raw[1], distances_raw[0]
    else:
        distances_raw.append(distances_raw[0])
    distances = np.array(distances_raw)

    # angles = np.array(angles_raw)

    # distances and angles should be 2 elements long
    # parameters = distances

    return np.array(distances_raw)


def partial_dirivative(image: cv2.UMat, camera_xyz_0: tuple, camera_rotation_0: tuple, fov_0: tuple, dt: str):

    cam_0 = CameraState(camera_xyz_0, camera_rotation_0, fov_0, (320, 240))
    cam_1 = CameraState(camera_xyz_0, camera_rotation_0, fov_0, (320, 240))

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


def Jacobian(image: cv2.UMat, camera_xyz_0: tuple, camera_rotation_0: tuple, fov_0: tuple):
    Jacobian = np.asmatrix(
        [
            partial_dirivative(image, camera_xyz_0, camera_rotation_0, fov_0, "x"),
            partial_dirivative(image, camera_xyz_0, camera_rotation_0, fov_0, "y"),
            partial_dirivative(image, camera_xyz_0, camera_rotation_0, fov_0, "z"),
            partial_dirivative(image, camera_xyz_0, camera_rotation_0, fov_0, "theta"),
            partial_dirivative(image, camera_xyz_0, camera_rotation_0, fov_0, "phi"),
            partial_dirivative(image, camera_xyz_0, camera_rotation_0, fov_0, "omega"),
            partial_dirivative(image, camera_xyz_0, camera_rotation_0, fov_0, "half_fov_h"),
            partial_dirivative(image, camera_xyz_0, camera_rotation_0, fov_0, "half_fov_v"),
        ]
    )
    return Jacobian.T


if __name__ == "__main__":
    current_dir = Path(__file__).parent
    pic_dir = current_dir.parent.parent / "assets" / "openCV_pic/test_pics"
    image = []
    for i in range(DATA_NUM):
        pic_path = f"{pic_dir}/{i}.jpg"
        if not Path(pic_path).is_file():
            print(f"cannot open {pic_path}")
        image.append(cv2.imread(pic_path))

    camera_xyz_0 = np.array([295, 12, -112.1])
    camera_rotation_0 = np.array([53.2, 0.9, 0.9])
    fov_0 = np.array([62.2, 62])
    resolution = (320, 240)
    E_test = np.array(
        [1180, 350, 1500, 690, 930, 900, 1180, 1100, 1760, 770, 1770, 1300, 2110, 350, 2230, 620]
    )  # 位置测量值
    p = np.concatenate((camera_xyz_0, camera_rotation_0, fov_0))
    d_p = np.zeros(8)

    dE_list = []

    for i in range(IDEN_TIMES):
        # 生成对象
        print("p = ", p)
        cam = CameraState(tuple(p[0:3]), tuple(p[3:6]), tuple(p[6:8]), resolution)

        # 根据当前参数计算理想位置
        E_cal = calculate_walls(
            cam, image[0]
        )  # [2 distances, (2 angels,) 2 distancess, (2 angels,)...], nparray
        for j in range(1, DATA_NUM):
            E_cal = np.concatenate((E_cal, calculate_walls(cam, image[j])))
        print("calculated E = ", E_cal)

        # Calculate the current error
        d_E = (E_test - E_cal).T
        print("|dE| = ", np.linalg.norm(d_E))
        print("dE = ", d_E)

        
        if np.linalg.norm(d_E) > 2500:
            dE_list.append(2500)
        else:
            dE_list.append(np.linalg.norm(d_E))
        
        #dE_list.append(d_E)

        if np.linalg.norm(d_E) < MINIMUM_ERROR:
            break

        # Generate Jacobian matrix (NUM_OF_DATAx16x8)
        J = np.array(
            [Jacobian(image[j], tuple(p[0:3]), tuple(p[3:6]), tuple(p[6:8])) for j in range(DATA_NUM)]
        ).reshape(-1, 8)
        print("Jacobian = ", J)



        
        #通过误差和雅可比矩阵解算参数
        J_Tik = np.linalg.inv(J.T@J + lam * np.eye(8)) @ J.T
        d_p = np.dot(np.linalg.pinv(J), d_E)


        # 补偿参数
        p = np.reshape(p, (1, 8))
        p += d_p
        p = np.reshape(p, (8,))

        print("p = ", p)

    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111)
    ax1.plot(dE_list)
    plt.show()

