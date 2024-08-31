from camera_convert import CameraState
import find_color
import camera_convert
import cv2
import core as c
import os
import numpy as np
import matplotlib.pyplot as plt

DIFF_LEN = 0.05
IDEN_TIMES = 400
NUM_OF_DATA = 8
MINIMUM_ERROR = 100
LAM = 0

def calculate_walls(cam : CameraState, image : cv2.UMat):
    walls_in_image = find_color.find_wall_bottom_p(image)

    if walls_in_image is not None:
        walls_raw = [(camera_convert.img2space(cam, wall[0][0], wall[0][1])[1:],
                  camera_convert.img2space(cam, wall[0][2], wall[0][3])[1:] )
            for wall in walls_in_image]

    walls = [walls_raw[0]]
    #merge near walls
    for w_i in walls_raw:
        if not (c.get_length(c.vec_sub(walls[0][0], w_i[0])) < 50 and c.get_length(c.vec_sub(walls[0][1], w_i[1])) < 50):
            walls.append(w_i)
            break
    
    distances_raw = []
    #angles_raw = []
    
    for w in walls:
        point_1, point_2 = (w[0][0], w[0][1]), (w[1][0], w[1][1])
        line = c.vec_sub(point_2, point_1)
        perpendicular = c.vec_sub(point_1, c.projection(point_1, line))
        distance = c.get_length(perpendicular)
        #angle = c.get_angle(perpendicular)

        distances_raw.append(distance)
        #angles_raw.append(angle)

    if(len(distances_raw) > 1):
        if(distances_raw[1] > distances_raw[0]):
            distances_raw[0], distances_raw[1] = distances_raw[1], distances_raw[0]
    else:
        distances_raw.append(distances_raw[0])

    distances = np.array(distances_raw)
    #angles = np.array(angles_raw)

    #distances and angles should be 2 elements long
    #parameters = np.concatenate((distances, angles))
    parameters = distances
    
    return parameters

def partial_dirivative(image : cv2.UMat, camera_xyz_0 : tuple, camera_rotation_0 : tuple, fov_0 : tuple, dt : str):

    cam_0 = CameraState(camera_xyz_0, camera_rotation_0, fov_0, (320,240))
    cam_1 = CameraState(camera_xyz_0, camera_rotation_0, fov_0, (320,240))

    if(dt == "x"):
        cam_1.x += DIFF_LEN
    elif(dt == "y"):
        cam_1.y += DIFF_LEN
    elif(dt == "z"):
        cam_1.z += DIFF_LEN

    elif(dt == "theta"):
        cam_1.theta += DIFF_LEN
    elif(dt == "phi"):
        cam_1.phi += DIFF_LEN
    elif(dt == "omega"):
        cam_1.omega += DIFF_LEN

    elif(dt == "half_fov_h"):
        cam_1.half_fov_h += DIFF_LEN
    elif(dt == "half_fov_v"):
        cam_1.half_fov_v += DIFF_LEN
    else:
        print("ERROR")

    cam_1.update()
    # 1/2 distances or angles calculate with two pairs of elements
    parameters_1 = calculate_walls(cam_0, image)
    parameters_2 = calculate_walls(cam_1, image)

    # if dt == "theta":
    #     print(cam_0.theta)
    #     print(cam_1.theta)
    #     print(cam_0.trans)
    #     print(cam_1.trans)
    # print(parameters_1)
    # print(parameters_2)

    # differences between two distances and angles
    d_parameters = parameters_2 - parameters_1
    # print(d_parameters)

    dt_D1 = d_parameters[0]/DIFF_LEN
    dt_D2 = d_parameters[1]/DIFF_LEN

    # dt_A1 = d_parameters[2]/STEP_LEN
    # dt_A2 = d_parameters[3]/STEP_LEN

    #return [dt_D1,dt_D2,dt_A1,dt_A2]
    del cam_0
    del cam_1

    return [dt_D1,dt_D2]

def Jacobian(image : cv2.UMat, camera_xyz_0 : tuple, camera_rotation_0 : tuple, fov_0 : tuple):
    Jacobian = np.asmatrix(
        [partial_dirivative(image, camera_xyz_0, camera_rotation_0, fov_0, "x"),
         partial_dirivative(image, camera_xyz_0, camera_rotation_0, fov_0, "y"),
         partial_dirivative(image, camera_xyz_0, camera_rotation_0, fov_0, "z"),
         partial_dirivative(image, camera_xyz_0, camera_rotation_0, fov_0, "theta"),
         partial_dirivative(image, camera_xyz_0, camera_rotation_0, fov_0, "phi"),
         partial_dirivative(image, camera_xyz_0, camera_rotation_0, fov_0, "omega"),
         partial_dirivative(image, camera_xyz_0, camera_rotation_0, fov_0, "half_fov_h"),
         partial_dirivative(image, camera_xyz_0, camera_rotation_0, fov_0, "half_fov_v")
         ])
    return Jacobian.T
    #return Jacobian

if __name__ == "__main__":
    read_dir = "test_pics"
    image = []
    for i in range(NUM_OF_DATA):
        image_index = i
        filename = "F:/trium/assets/openCV_pic/" + read_dir + "/" + str(image_index) + ".jpg"
        if not os.path.isfile(filename):
            print("cannot open " + filename)
        image.append(cv2.imread(filename))

    camera_xyz_0 = np.array([295, 12, -221])
    camera_rotation_0 = np.array([53.2, 0.9, 0.9])
    fov_0 = np.array([62.2, 62])
    resolution =  (320,240)
    E_test = np.array([1180, 350, 1500, 690, 930, 900, 1180, 1100, 1760, 770, 1770, 1300, 2110, 350, 2230, 620]) #位置测量值
    p = np.concatenate((camera_xyz_0, camera_rotation_0, fov_0))
    d_p = np.zeros(8)

    dE_list = []

    for i in range(IDEN_TIMES):
        #生成对象
        print("p = ", p)
        cam = CameraState(tuple(p[0:3]), tuple(p[3:6]), tuple(p[6:8]), resolution)

        #根据当前参数计算理想位置
        E_cal = calculate_walls(cam, image[0]) #[2 distances, (2 angels,) 2 distancess, (2 angels,)...], nparray
        for j in range(1, NUM_OF_DATA):
            E_cal = np.concatenate((E_cal, calculate_walls(cam, image[j])))
        print("calculated E = ", E_cal)

        #求解当前误差
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

        #生成雅可比矩阵
        J = Jacobian(image[0], tuple(p[0:3]), tuple(p[3:6]), tuple(p[6:8])) # 16x8
        for j in range(1, NUM_OF_DATA):
            J = np.concatenate((J,Jacobian(image[j], tuple(p[0:3]), tuple(p[3:6]), tuple(p[6:8]))))
        print("Jacobian = ",J)

        
        #通过误差和雅可比矩阵解算参数
        J_Tik = np.linalg.inv(J.T@J + LAM * np.eye(8)) @ J.T
        d_p = np.dot(J_Tik, d_E)
        #d_p = np.dot(np.linalg.pinv(J), d_E)

        #补偿参数
        p = np.reshape(p, (1,8))
        p += d_p
        p = np.reshape(p, (8,))

        print("p = ", p)
    
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111)
    ax1.plot(dE_list)
    plt.show()
