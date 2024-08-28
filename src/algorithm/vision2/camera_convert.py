import numpy as np


class CameraState:

    # 座标架：车向前为x，车向右为y，向下为z，方向与z轴夹角为theta，右手螺旋向下相对x轴旋转为phi，绕入射光方向右手螺旋偏转为omega
    # 方向指摄像头中央对准的位置
    # 摄像头必须是竖直对准的
    def __init__(
        self,
        camera_xyz: tuple[float, float, float],
        camera_rotation: tuple[float, float, float],
        fov: tuple[float, float],
        resolution: tuple[int, int],
    ):
        """
        Initializes the CameraConvert object.
        Args:
            camera_xyz (tuple[float, float, float]): The XYZ coordinates of the camera.
            camera_rotation (tuple[float, float, float]): The rotation angles of the camera in degrees.
            fov (tuple[float, float]): The field of view angles of the camera in degrees.
            resolution (tuple[int, int]): The resolution of the camera image.
        Returns:
            None
        """
        self.x, self.y, self.z = camera_xyz
        self.theta, self.phi, self.omega = np.radians(camera_rotation)
        self.half_fov_h, self.half_fov_v = np.radians(fov) / 2
        self.res_h, self.res_v = resolution

        self.trans_phi = np.array(
            (
                (np.cos(self.phi), np.sin(self.phi), 0),
                (-np.sin(self.phi), np.cos(self.phi), 0),
                (0, 0, 1),
            )
        )
        self.trans_theta = np.array(
            (
                (np.sin(self.theta), 0, np.cos(self.theta)),
                (0, 1, 0),
                (-np.cos(self.theta), 0, np.sin(self.theta)),
            )
        )
        self.trans_omega = np.array(
            (
                (1, 0, 0),
                (0, np.cos(self.omega), -np.sin(self.omega)),
                (0, np.sin(self.omega), np.cos(self.omega)),
            )
        )

        self.trans = np.dot(np.dot(self.trans_phi, self.trans_theta), self.trans_omega)

        self.img_to_relative_cords_mapping = np.array(
            (
                (1, 0, 0),
                (-np.tan(self.half_fov_h), 2 / self.res_h * np.tan(self.half_fov_h), 0),
                (-np.tan(self.half_fov_v), 0, 2 / self.res_v * np.tan(self.half_fov_v)),
            )
        )
        self.relative_cords_to_img_mapping = np.linalg.inv(
            self.img_to_relative_cords_mapping
        )

    def update(self):
        self.trans_phi = np.array(
            (
                (np.cos(self.phi), np.sin(self.phi), 0),
                (-np.sin(self.phi), np.cos(self.phi), 0),
                (0, 0, 1),
            )
        )
        self.trans_theta = np.array(
            (
                (np.sin(self.theta), 0, np.cos(self.theta)),
                (0, 1, 0),
                (-np.cos(self.theta), 0, np.sin(self.theta)),
            )
        )
        self.trans_omega = np.array(
            (
                (1, 0, 0),
                (0, np.cos(self.omega), -np.sin(self.omega)),
                (0, np.sin(self.omega), np.cos(self.omega)),
            )
        )

        self.trans = np.dot(np.dot(self.trans_phi, self.trans_theta), self.trans_omega)

        self.img_to_relative_cords_mapping = np.array(
            (
                (1, 0, 0),
                (-np.tan(self.half_fov_h), 2 / self.res_h * np.tan(self.half_fov_h), 0),
                (-np.tan(self.half_fov_v), 0, 2 / self.res_v * np.tan(self.half_fov_v)),
            )
        )
        self.relative_cords_to_img_mapping = np.linalg.inv(
            self.img_to_relative_cords_mapping
        )


def img2space(
    camera_state: CameraState, i: int, j: int, target_z: float = 0
) -> tuple[bool, float, float]:
    c = camera_state

    relative_cords = np.dot(c.img_to_relative_cords_mapping, (1, i, j))

    vec = np.dot(relative_cords, c.trans)

    on_the_ground = vec[2] > 0
    vec /= vec[2]

    x = c.x + (target_z - c.z) * vec[0]
    y = c.y + (target_z - c.z) * vec[1]

    return on_the_ground, x, y


def space2img(
    camera_state: CameraState, x: float, y: float, z: float = 0
) -> tuple[bool, int, int]:
    c = camera_state

    can_be_seen = True

    vec = np.array((x - c.x, y - c.y, z - c.z))
    if vec[0] < 0:
        can_be_seen = False

    relative_cords = np.dot(c.trans, vec)

    relative_cords /= relative_cords[0]

    _, i, j = np.dot(c.relative_cords_to_img_mapping, relative_cords)

    if not (0 <= i < c.res_h and 0 <= j < c.res_v):
        can_be_seen = False

    return can_be_seen, int(i), int(j)


if __name__ == "__main__":
    example_camera_state = CameraState(
        (100, 0, -200), (70, 0, 0), (100, 80), (640, 480)
    )

    print(img2space(example_camera_state, 320, 0))
    print(img2space(example_camera_state, 320, 400))
    print(img2space(example_camera_state, 320, 480))
    print(img2space(example_camera_state, 0, 480))

    _, x1, y1 = img2space(example_camera_state, 320, 400)
    print(space2img(example_camera_state, x1, y1))
