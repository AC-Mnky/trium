import pygame

HALF_A = 10
A = HALF_A * 2
WIDTH = 4
BACK = (0, 0, 0)
FRONT = (255, 255, 255)


class Dummy:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((200, 200))

    def get_output(self) -> tuple[tuple[float, float], bool, bool]:
        for event in pygame.event.get():
            if (
                    event.type == pygame.QUIT
                    or event.type == pygame.KEYDOWN
                    and (event.key in [pygame.K_ESCAPE, pygame.K_q])
            ):
                exit()

        keys = pygame.key.get_pressed()

        motor = (0, 0)
        brush = not keys[pygame.K_i]
        back_open = keys[pygame.K_o]

        if keys[pygame.K_UP]:
            if keys[pygame.K_LEFT]:
                motor = (0, 1)
            elif keys[pygame.K_RIGHT]:
                motor = (1, 0)
            else:
                motor = (1, 1)
        elif keys[pygame.K_DOWN]:
            if keys[pygame.K_LEFT]:
                motor = (-1, 0)
            elif keys[pygame.K_RIGHT]:
                motor = (0, -1)
            else:
                motor = (-1, -1)
        elif keys[pygame.K_LEFT]:
            motor = (-1, 1)
        elif keys[pygame.K_RIGHT]:
            motor = (1, -1)

        motor = motor[0] / 2, motor[1] / 2

        self.screen.fill(BACK)
        pygame.draw.rect(self.screen, FRONT, (50 - HALF_A, 100 - motor[0] * 50 - HALF_A, A, A))
        pygame.draw.rect(self.screen, FRONT, (150 - HALF_A, 100 - motor[1] * 50 - HALF_A, A, A))
        pygame.draw.rect(self.screen, FRONT, (100 - HALF_A, 50 - HALF_A, A, A), 0 if brush else WIDTH)
        pygame.draw.rect(self.screen, FRONT, (100 - HALF_A, 150 - HALF_A, A, A), 0 if not back_open else WIDTH)
        pygame.display.flip()

        return motor, brush, back_open
