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
CAR = (255, 128, 0, 128)
WHITE = (255, 255, 255, 255)

SPEED_CONTROL = 0.3


class Visualizer:
    def __init__(self, _core: core.Core, control: bool = False):
        self.force_stop = False
        self.control = control

        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont("Cambria", FONT_SIZE)
        self.screen = pygame.display.set_mode(WINDOW_SIZE)

        self.core = _core
        
        ...

    def update(self, time: float) -> core.Core:

        for event in pygame.event.get():
            if (
                    event.type == pygame.QUIT
                    or event.type == pygame.KEYDOWN
                    and (event.key in [pygame.K_ESCAPE, pygame.K_q])
            ):
                exit()
            elif self.control:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_i:
                        self.core.brush = not self.core.brush
                    elif event.key == pygame.K_o:
                        self.core.back_open = not self.core.back_open
                
        keys = pygame.key.get_pressed()

        self.force_stop = keys[pygame.K_s]
        if keys[pygame.K_r]:
            self.core = core.Core(time)
        
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
        

        self.draw()

        return self.core

    def draw(self) -> None:

        self.screen.fill(BACK)

        draw_alpha.line(self.screen, WHITE, (MARGIN, MARGIN), (MARGIN + ROOM_SIZE[0], MARGIN), 2)
        draw_alpha.line(self.screen, WHITE, (MARGIN, MARGIN + ROOM_SIZE[1]),
                        (MARGIN + ROOM_SIZE[0], MARGIN + ROOM_SIZE[1]), 2)
        draw_alpha.line(self.screen, WHITE, (MARGIN, MARGIN), (MARGIN, MARGIN + ROOM_SIZE[1]), 2)
        draw_alpha.line(self.screen, WHITE, (MARGIN + ROOM_SIZE[0], MARGIN),
                        (MARGIN + ROOM_SIZE[0], MARGIN + ROOM_SIZE[1]), 2)

        for item, v in self.core.predicted_items.items():
            draw_alpha.circle(self.screen, (
                255, 255 if v[1] == 1 else 0, 0, int(16 * min(v[0], 8))), real2window(item), core.MERGE_RADIUS / UNIT)
            if v[2] > 0:
                draw_alpha.circle(self.screen, (255, 255, 255, 128), real2window(item), core.MERGE_RADIUS / UNIT)

        draw_alpha.polygon(self.screen, CAR, [real2window(v) for v in self.core.predicted_vertices[0] + self.core.predicted_vertices[1][::-1]])
        draw_alpha.circle(self.screen, WHITE, real2window(self.core.predicted_cords), 5)
        
        

        pygame.display.flip()


def real2window(vec: tuple[float, float]) -> tuple[float, float]:
    return core.vec_add(VEC_MARGIN, core.vec_multiply(vec, 1 / UNIT))
