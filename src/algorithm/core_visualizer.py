import pygame

try:
    import core
    import draw_alpha

except ModuleNotFoundError:
    import os
    import sys

    current_dir = os.path.dirname(__file__)
    sys.path.append(f"{current_dir}")
else:
    ...

UNIT = 5

REAL_ROOM_SIZE = (3000, 2000)

ROOM_SIZE = (REAL_ROOM_SIZE[0] // UNIT, REAL_ROOM_SIZE[1] // UNIT)

MARGIN = 50
VEC_MARGIN = (MARGIN, MARGIN)
WINDOW_SIZE = (ROOM_SIZE[0] + 2 * MARGIN, ROOM_SIZE[1] + 2 * MARGIN)
FONT_SIZE = 20

BACK = (0, 0, 0, 0)
CAR = (255, 128, 0, 128)
WHITE = (255, 255, 255, 255)
CAMERA = (255, 255, 255, 32)
CAMERA_SHOT = (255, 255, 255, 128)

SPEED_CONTROL = 0.5


class VisualizerInterrupt(Exception):
    def __init__(self):
        super(VisualizerInterrupt, self).__init__("interrupted")

    def __str__(self):
        return "interrupted"


class Visualizer:
    def __init__(self, _core: core.Core, control: bool = False):
        self.force_stop = False
        self.control = control

        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont("DejaVuSansMono", FONT_SIZE)
        self.screen = pygame.display.set_mode(WINDOW_SIZE)

        self.mouse_pos = 0

        self.core = _core

        self.brush = False
        self.back_open = False

        self.walls = []

        ...

    def update(self, time: float) -> core.Core:
        """
        Update the visualizer based on user input and time.

        Args:
            time (float): The current time.

        Returns:
            core (core.Core): The updated core object.
        """
        self.mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if (
                event.type == pygame.QUIT
                or event.type == pygame.KEYDOWN
                and (event.key in [pygame.K_ESCAPE, pygame.K_q])
            ):
                raise VisualizerInterrupt()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                cords = window2real(self.mouse_pos)
                if event.button == 1:  # left-click
                    self.core.predicted_items[cords] = [
                        self.core.predicted_items.get(cords, (0, 0))[0] + 2,
                        core.RED,
                        0,
                        0,
                    ]
                elif event.button == 3:  # right-click
                    self.core.predicted_items[cords] = [
                        self.core.predicted_items.get(cords, (0, 0))[0] + 3,
                        core.YELLOW,
                        0,
                        0,
                    ]
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    self.control = not self.control
                elif self.control:
                    if event.key == pygame.K_i:
                        self.brush = not self.brush
                    elif event.key == pygame.K_o:
                        self.back_open = not self.back_open

        keys = pygame.key.get_pressed()

        self.force_stop = keys[pygame.K_s]
        if keys[pygame.K_r]:
            self.core = core.Core(time, self.core.protocol)
        if keys[pygame.K_e]:
            self.core.status_code = 1

        if self.control:
            self.core.motor = [0, 0]
            if keys[pygame.K_UP]:
                if keys[pygame.K_LEFT]:
                    self.core.motor = [0, 1]
                elif keys[pygame.K_RIGHT]:
                    self.core.motor = [1, 0]
                else:
                    self.core.motor = [1, 1]
            elif keys[pygame.K_DOWN]:
                if keys[pygame.K_LEFT]:
                    self.core.motor = [-1, 0]
                elif keys[pygame.K_RIGHT]:
                    self.core.motor = [0, -1]
                else:
                    self.core.motor = [-1, -1]
            elif keys[pygame.K_LEFT]:
                self.core.motor = [-1, 1]
            elif keys[pygame.K_RIGHT]:
                self.core.motor = [1, -1]

            self.core.motor = [self.core.motor[0] * SPEED_CONTROL, self.core.motor[1] * SPEED_CONTROL]

            self.core.brush = self.brush
            self.core.back_open = self.back_open

        self.draw()

        return self.core

    def draw(self) -> None:
        """
        Draw the visualization of the algorithm on the screen.

        - This method fills the screen with a background color and then draws various shapes and
        lines to represent the algorithm's predicted items, walls, and other elements.
        - The visualization includes circles, lines, and polygons.

        Returns:
            None
        """
        self.screen.fill(BACK)

        draw_alpha.line(self.screen, WHITE, (MARGIN, MARGIN), (MARGIN + ROOM_SIZE[0], MARGIN), 2)
        draw_alpha.line(
            self.screen,
            WHITE,
            (MARGIN, MARGIN + ROOM_SIZE[1]),
            (MARGIN + ROOM_SIZE[0], MARGIN + ROOM_SIZE[1]),
            2,
        )
        draw_alpha.line(self.screen, WHITE, (MARGIN, MARGIN), (MARGIN, MARGIN + ROOM_SIZE[1]), 2)
        draw_alpha.line(
            self.screen,
            WHITE,
            (MARGIN + ROOM_SIZE[0], MARGIN),
            (MARGIN + ROOM_SIZE[0], MARGIN + ROOM_SIZE[1]),
            2,
        )

        for item, v in self.core.predicted_items.items():
            if v[3] == 5:
                color = (0, 0, 255)
            elif 1 <= v[3] <= 4:
                color = (0, 255, 0)
            else:
                if v[1] == core.YELLOW:
                    color = (255, 255, 0)
                else:
                    color = (255, 0, 0)
            draw_alpha.circle(
                self.screen,
                color + (min(v[0] * 32, 255),),
                real2window(item),
                core.MERGE_RADIUS / UNIT / 2,
            )
            if v[2] > 0:
                draw_alpha.circle(
                    self.screen, (255, 255, 255, 128), real2window(item), 10
                )

        if self.core.camera_input is not None:
            self.walls = self.core.camera_input[3]

        for wall in self.walls:
            try:
                draw_alpha.line(
                    self.screen,
                    (0, 128, 255, 128),
                    real2window(self.core.relative2absolute(wall[0])),
                    real2window(self.core.relative2absolute(wall[1])),
                    1,
                )
            except pygame.error:
                ...
        # car
        draw_alpha.polygon(
            self.screen,
            CAR,
            [real2window(v) for v in self.core.predicted_vertices[0] + self.core.predicted_vertices[1][::-1]],
        )
        draw_alpha.line(
            self.screen,
            WHITE,
            real2window(self.core.predicted_cords),
            real2window(self.core.relative2absolute((1000, 0))),
            1,
        )

        camera_color = CAMERA if self.core.camera_has_input else CAMERA_SHOT
        draw_alpha.polygon(
            self.screen, camera_color, [real2window(v) for v in self.core.predicted_camera_vertices[0:4]]
        )
        draw_alpha.polygon(
            self.screen, camera_color, [real2window(v) for v in self.core.predicted_camera_vertices[4:8]]
        )
        draw_alpha.circle(self.screen, WHITE, real2window(self.core.predicted_cords), 2)
        draw_alpha.circle(
            self.screen, (0, 0, 255, 64), real2window(self.core.contact_center), core.CONTACT_RADIUS / UNIT
        )

        self.core.get_output()

        # message IO
        text = self.font.render(self.core.output.hex(" "), True, WHITE)
        self.screen.blit(text, (10, 5))
        text = self.font.render(self.core.stm_input.hex(" "), True, WHITE)
        self.screen.blit(text, (10, 25))

        # message
        text = self.font.render(self.core.vision_message, True, WHITE)
        self.screen.blit(text, (10, WINDOW_SIZE[1] - 50 + 5))
        self.core.vision_message = "..."

        if self.core.vision_target_cords is not None:
            c = real2window(self.core.vision_target_cords)
            draw_alpha.line(self.screen, WHITE, core.vec_add(c, (-100, 0)), core.vec_add(c, (100, 0)), 1)
            draw_alpha.line(self.screen, WHITE, core.vec_add(c, (0, -100)), core.vec_add(c, (0, 100)), 1)
            draw_alpha.line(self.screen, WHITE, c, real2window(self.core.predicted_cords), 1)
            self.core.vision_target_cords = None

        pygame.display.flip()


def real2window(vec: tuple[float, float]) -> tuple[float, float]:
    """
    Convert a real coordinate to a window coordinate.

    Args:
        vec (tuple[float, float]): The real coordinate to be converted.

    Returns:
        tuple (tuple[float, float]): The converted window coordinate.
    """
    return core.vec_add(VEC_MARGIN, core.vec_mul(vec, 1 / UNIT))


def window2real(vec: tuple[float, float]) -> tuple[float, float]:
    """
    Convert a vector from window coordinates to real coordinates.

    Args:
        vec (tuple[float, float]): The vector in window coordinates.

    Returns:
        tuple (tuple[float, float]): The vector in real coordinates.
    """
    return core.vec_mul(core.vec_sub(vec, VEC_MARGIN), UNIT)
