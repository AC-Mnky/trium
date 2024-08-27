import pygame

try:
    from algorithm import core
    from algorithm import draw_alpha
except ModuleNotFoundError:
    import core
    import draw_alpha
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
RED = (255, 0, 0, 255)
WHITE = (255, 255, 255, 255)


class Visualizer:
    def __init__(self, _core: core.Core):
        self.force_stop = False

        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont("Cambria", FONT_SIZE)
        self.screen = pygame.display.set_mode(WINDOW_SIZE)

        self.core = _core
        ...

    def update(self) -> None:

        for event in pygame.event.get():
            if (
                    event.type == pygame.QUIT
                    or event.type == pygame.KEYDOWN
                    and (event.key in [pygame.K_ESCAPE, pygame.K_q])
            ):
                exit()

        self.draw()

        ...

    def draw(self) -> None:

        self.screen.fill(BACK)

        draw_alpha.line(self.screen, WHITE, (MARGIN, MARGIN), (MARGIN + ROOM_SIZE[0], MARGIN), 2)
        draw_alpha.line(self.screen, WHITE, (MARGIN, MARGIN + ROOM_SIZE[1]),
                        (MARGIN + ROOM_SIZE[0], MARGIN + ROOM_SIZE[1]), 2)
        draw_alpha.line(self.screen, WHITE, (MARGIN, MARGIN), (MARGIN, MARGIN + ROOM_SIZE[1]), 2)
        draw_alpha.line(self.screen, WHITE, (MARGIN + ROOM_SIZE[0], MARGIN),
                        (MARGIN + ROOM_SIZE[0], MARGIN + ROOM_SIZE[1]), 2)

        draw_alpha.circle(self.screen, WHITE, real2window(self.core.predicted_cords), 20)
        draw_alpha.line(self.screen, RED, real2window(self.core.predicted_cords), real2window(
            core.vec_add(self.core.predicted_cords, core.rotated((core.LENGTH, 0), self.core.predicted_angle))), 5)

        pygame.display.flip()


def real2window(vec: tuple[float, float]) -> tuple[float, float]:
    return core.vec_add(VEC_MARGIN, core.vec_multiply(vec, 1 / UNIT))
