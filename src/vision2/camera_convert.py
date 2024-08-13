import math


class CameraState:

    # 座标架：车向前为x，车向右为y，向下为z，方向与z轴夹角为theta，右手螺旋向下相对x轴旋转为phi
    # 方向指摄像头中央对准的位置
    # 摄像头必须是竖直对准的
    def __init__(self, camera_xyz: (float, float, float), camera_rotation: (float, float), fov: (float, float),
                 resolution: (int, int)):
        self.x, self.y, self.z = camera_xyz
        self.theta = math.radians(camera_rotation[0])
        self.phi = math.radians(camera_rotation[1])
        self.fov_h = math.radians(fov[0])
        self.fov_v = math.radians(fov[1])
        self.res_h, self.res_v = resolution


def img2space(camera_state: CameraState, i: int, j: int, target_z: float = 0) -> (bool, float, float):
    c = camera_state

    h = (i / c.res_h - 1 / 2) * math.tan(c.fov_h)
    v = (j / c.res_v - 1 / 2) * math.tan(c.fov_v)

    vec_x = math.cos(c.phi) * math.sin(c.theta) + h * (-math.sin(c.phi)) + v * (-math.cos(c.phi) * math.cos(c.theta))
    vec_y = math.sin(c.phi) * math.sin(c.theta) + h * (+math.cos(c.phi)) + v * (-math.sin(c.phi) * math.cos(c.theta))
    vec_z = math.cos(c.theta) + v * math.sin(c.theta)

    on_the_ground = vec_z > 0
    x = c.x + (target_z - c.z) * vec_x / vec_z
    y = c.y + (target_z - c.z) * vec_y / vec_z

    return on_the_ground, x, y


def space2img(camera_state: CameraState, x: float, y: float, z: float = 0) -> (bool, int, int):
    c = camera_state

    can_be_seen = True

    vec_x = x - c.x
    vec_y = y - c.y
    vec_z = z - c.z
    if vec_x < 0:
        can_be_seen = False

    # TODO
    ...


example_camera_state = CameraState((100, 0, -200), (70, 0), (100, 60), (640, 480))

print(img2space(example_camera_state, 320, 0))
print(img2space(example_camera_state, 320, 400))
print(img2space(example_camera_state, 320, 480))
print(img2space(example_camera_state, 0, 480))
