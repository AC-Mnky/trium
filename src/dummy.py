import pygame
from numpy import clip

HALF_A = 10
A = HALF_A * 2
WIDTH = 4
BACK = (0, 0, 0)
FRONT = (255, 255, 255)
LOCK = (255, 0, 0)
# MOUSE_ON = (255, 255, 0)
CLICK_MAX_MILLISECONDS = 200
MAX_SPEED_CLIP = 1
MIN_PID_CLIP = 0
MAX_PID_CLIP = 127


class Dummy:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont('Cambria Math', 20)
        self.screen = pygame.display.set_mode((400, 200))
        self.motor = [0.0, 0.0]
        self.brush = True
        self.back_open = False
        self.left_rect = self.right_rect = self.top_rect = self.bottom_rect = pygame.Rect(0, 0, 0, 0)
        self.text_rect = [[[pygame.Rect(0, 0, 0, 0), ] * 3, ] * 3, ] * 2
        self.left_lock = False
        self.right_lock = False
        self.mouse_down_tick = -1000
        self.left_mouse_offset = None
        self.right_mouse_offset = None
        self.mouse_on_text = None

        self.motor_PID = [[3, 2, 0, 10, 0, 10], [3, 2, 0, 10, 0, 10]]

    def get_output(self) -> list[
                                list[float, float],  # motor speed / max speed
                                bool,  # brush
                                bool,  # back open
                                list[  # motor PID
                                    list[int, int, int, int, int, int],  # left motor Kp_mul, Kp_frac, Ki_..., Kd_...
                                    list[int, int, int, int, int, int],  # right motor Kp_mul, Kp_frac, Ki_..., Kd_...
                                    ],
                                ]:
        pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if (
                    event.type == pygame.QUIT
                    or event.type == pygame.KEYDOWN
                    and (event.key in [pygame.K_ESCAPE, pygame.K_q])
            ):
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_down_tick = pygame.time.get_ticks()
                if self.top_rect.collidepoint(pos):
                    self.brush = not self.brush
                if self.bottom_rect.collidepoint(pos):
                    self.back_open = not self.back_open
                if self.left_rect.collidepoint(pos):
                    self.left_lock = True
                    self.left_mouse_offset = pos[1] - self.left_rect.centery
                if self.right_rect.collidepoint(pos):
                    self.right_lock = True
                    self.right_mouse_offset = pos[1] - self.right_rect.centery
            elif event.type == pygame.MOUSEBUTTONUP:
                if pygame.time.get_ticks() - self.mouse_down_tick < CLICK_MAX_MILLISECONDS:
                    if self.left_mouse_offset is not None:
                        self.left_lock = False
                    if self.right_mouse_offset is not None:
                        self.right_lock = False
                self.left_mouse_offset = None
                self.right_mouse_offset = None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    self.brush = not self.brush
                elif event.key == pygame.K_o:
                    self.back_open = not self.back_open
            elif event.type == pygame.MOUSEWHEEL:
                if self.mouse_on_text is not None:
                    print(self.mouse_on_text)
                    a, b = self.mouse_on_text[0], self.mouse_on_text[1] * 2 + self.mouse_on_text[2] // 2
                    self.motor_PID[a][b] += event.y
                    self.motor_PID[a][b] = int(clip(self.motor_PID[a][b], MIN_PID_CLIP, MAX_PID_CLIP))

        if pygame.mouse.get_pressed()[0]:
            if self.left_mouse_offset is not None:
                self.motor[0] = float(clip((100 - pygame.mouse.get_pos()[1] + self.left_mouse_offset) / 50,
                                           -MAX_SPEED_CLIP, MAX_SPEED_CLIP))
            if self.right_mouse_offset is not None:
                self.motor[1] = float(clip((100 - pygame.mouse.get_pos()[1] + self.right_mouse_offset) / 50,
                                           -MAX_SPEED_CLIP, MAX_SPEED_CLIP))

        keys = pygame.key.get_pressed()

        motor_prev = self.motor

        self.motor = [0, 0]
        if keys[pygame.K_UP]:
            if keys[pygame.K_LEFT]:
                self.motor = [0, 1]
            elif keys[pygame.K_RIGHT]:
                self.motor = [1, 0]
            else:
                self.motor = [1, 1]
        elif keys[pygame.K_DOWN]:
            if keys[pygame.K_LEFT]:
                self.motor = [-1, 0]
            elif keys[pygame.K_RIGHT]:
                self.motor = [0, -1]
            else:
                self.motor = [-1, -1]
        elif keys[pygame.K_LEFT]:
            self.motor = [-1, 1]
        elif keys[pygame.K_RIGHT]:
            self.motor = [1, -1]

        self.motor = [self.motor[0] / 2, self.motor[1] / 2]

        if self.left_lock:
            self.motor[0] = motor_prev[0]
        if self.right_lock:
            self.motor[1] = motor_prev[1]

        self.screen.fill(BACK)

        self.left_rect = pygame.Rect(150 - HALF_A, 100 - self.motor[0] * 50 - HALF_A, A, A)
        self.right_rect = pygame.Rect(250 - HALF_A, 100 - self.motor[1] * 50 - HALF_A, A, A)
        self.top_rect = pygame.Rect(200 - HALF_A, 50 - HALF_A, A, A)
        self.bottom_rect = pygame.Rect(200 - HALF_A, 150 - HALF_A, A, A)

        pygame.draw.rect(self.screen, LOCK if self.left_lock else FRONT, self.left_rect)
        pygame.draw.rect(self.screen, LOCK if self.right_lock else FRONT, self.right_rect)
        pygame.draw.rect(self.screen, FRONT, self.top_rect, 0 if self.brush else WIDTH)
        pygame.draw.rect(self.screen, FRONT, self.bottom_rect, 0 if self.back_open else WIDTH)

        self.mouse_on_text = None
        for i in range(2):
            for j in range(3):
                text = self.font.render(str(self.motor_PID[i][2 * j]), True, FRONT)
                rect = text.get_rect()
                offset = 50 + 250 * i - rect.centerx, 50 + 50 * j - rect.centery
                self.text_rect[i][j][0] = rect.move(offset).inflate(20, 20)
                if self.text_rect[i][j][0].collidepoint(pos):
                    self.mouse_on_text = i, j, 0
                    text = self.font.render(str(self.motor_PID[i][2 * j]), True, BACK, FRONT)
                self.screen.blit(text, offset)

                text = self.font.render('/', True, FRONT)
                rect = text.get_rect()
                offset = 75 + 250 * i - rect.centerx, 50 + 50 * j - rect.centery
                self.text_rect[i][j][1] = rect.move(offset).inflate(20, 20)
                self.screen.blit(text, offset)

                text = self.font.render(str(self.motor_PID[i][2 * j + 1]), True, FRONT)
                rect = text.get_rect()
                offset = 100 + 250 * i - rect.centerx, 50 + 50 * j - rect.centery
                self.text_rect[i][j][2] = rect.move(offset).inflate(20, 20)
                if self.text_rect[i][j][2].collidepoint(pos):
                    self.mouse_on_text = i, j, 2
                    text = self.font.render(str(self.motor_PID[i][2 * j + 1]), True, BACK, FRONT)
                self.screen.blit(text, offset)

                # self.screen.blit(self.font.render('/', True, FRONT),
                #                  (200 + 120 * (i * 2 - 1) - 10, 50 + 50 * j - 10))
                # self.screen.blit(self.font.render(str(self.motor_PID[i][2 * j + 1]), True, FRONT),
                #                  (200 + 90 * (i * 2 - 1) - 10, 50 + 50 * j - 10))

        pygame.display.flip()

        return [self.motor, self.brush, self.back_open, self.motor_PID]
