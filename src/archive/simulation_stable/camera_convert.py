import numpy as np


class CameraState:

    # 座标架：车向前为x，车向右为y，向下为z，方向与z轴夹角为theta，右手螺旋向下相对x轴旋转为phi
    # 方向指摄像头中央对准的位置
    # 摄像头必须是竖直对准的
    def __init__(
        self,
        camera_xyz: tuple[float, float, float],
        camera_rotation: tuple[float, float],
        fov: tuple[float, float],
        resolution: tuple[int, int],
    ):
        self.x, self.y, self.z = camera_xyz
        self.theta = np.radians(camera_rotation[0])
        self.phi = np.radians(camera_rotation[1])
        self.half_fov_h = np.radians(fov[0]) / 2
        self.half_fov_v = np.radians(fov[1]) / 2
        self.res_h, self.res_v = resolution

        self.ax = np.array(
            (
                (np.cos(self.phi) * np.sin(self.theta), np.sin(self.phi) * np.sin(self.theta), np.cos(self.theta)),
                (-np.sin(self.phi), np.cos(self.phi), 0),
                (-np.cos(self.phi) * np.cos(self.theta), -np.sin(self.phi) * np.cos(self.theta), np.sin(self.theta)),
            )
        )


def img2space(camera_state: CameraState, i: int, j: int, target_z: float = 0) -> tuple[bool, float, float]:
    c = camera_state

    h = (2 * i / c.res_h - 1) * np.tan(c.half_fov_h)
    v = (2 * j / c.res_v - 1) * np.tan(c.half_fov_v)
    ax_coo = np.array((1, h, v))

    vec = np.dot(ax_coo, c.ax)

    on_the_ground = vec[2] > 0
    x = c.x + (target_z - c.z) * vec[0] / vec[2]
    y = c.y + (target_z - c.z) * vec[1] / vec[2]

    return on_the_ground, x, y


def space2img(camera_state: CameraState, x: float, y: float, z: float = 0) -> tuple[bool, int, int]:
    c = camera_state

    can_be_seen = True

    vec = np.array((x - c.x, y - c.y, z - c.z))
    if vec[0] < 0:
        can_be_seen = False

    ax_coo = np.dot(c.ax, vec)

    h = ax_coo[1] / ax_coo[0]
    v = ax_coo[2] / ax_coo[0]

    i = int(np.round((h / np.tan(c.half_fov_h) + 1) / 2 * c.res_h))
    j = int(np.round((v / np.tan(c.half_fov_v) + 1) / 2 * c.res_v))

    if not (0 <= i < c.res_h and 0 <= j < c.res_v):
        can_be_seen = False

    return can_be_seen, i, j


if __name__ == "__main__":
    example_camera_state = CameraState((100, 0, -200), (70, 0), (100, 80), (640, 480))

    print(img2space(example_camera_state, 320, 0))
    print(img2space(example_camera_state, 320, 400))
    print(img2space(example_camera_state, 320, 480))
    print(img2space(example_camera_state, 0, 480))

    _, x1, y1 = img2space(example_camera_state, 320, 400)
    print(space2img(example_camera_state, x1, y1))
