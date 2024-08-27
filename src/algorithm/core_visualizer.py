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
WINDOW_SIZE = (ROOM_SIZE[0] + 2 * MARGIN, ROOM_SIZE[1] + 2 * MARGIN)
FONT_SIZE = 20

BACK = (0, 0, 0, 0)
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

        draw_alpha.circle(self.screen, WHITE, self.core.predicted_cords / UNIT, )

        pygame.display.flip()
