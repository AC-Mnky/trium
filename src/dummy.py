import pygame
from numpy import clip

HALF_A = 10
A = HALF_A * 2
WIDTH = 4
BACK = (0, 0, 0)
FRONT = (255, 255, 255)
LOCK = (255, 0, 0)
CLICK_MAX_MILLISECONDS = 100


class Dummy:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((200, 200))
        self.motor = (0, 0)
        self.brush = True
        self.back_open = False
        self.left_rect = self.right_rect = self.top_rect = self.bottom_rect = pygame.Rect(0, 0, 0, 0)
        self.left_lock = False
        self.right_lock = False
        self.mouse_down_tick = -1000
        self.left_mouse_offset = None
        self.right_mouse_offset = None

    def get_output(self) -> tuple[tuple[float, float], bool, bool]:
        for event in pygame.event.get():
            if (
                    event.type == pygame.QUIT
                    or event.type == pygame.KEYDOWN
                    and (event.key in [pygame.K_ESCAPE, pygame.K_q])
            ):
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
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

        if pygame.mouse.get_pressed()[0]:
            if self.left_mouse_offset is not None:
                self.motor = clip((100 - pygame.mouse.get_pos()[1] + self.left_mouse_offset) / 50, -1, 1), self.motor[1]
            if self.right_mouse_offset is not None:
                self.motor = self.motor[0], clip((100 - pygame.mouse.get_pos()[1] + self.right_mouse_offset) / 50, -1,
                                                 1)

        keys = pygame.key.get_pressed()

        motor_prev = self.motor

        self.motor = (0, 0)
        if keys[pygame.K_UP]:
            if keys[pygame.K_LEFT]:
                self.motor = (0, 1)
            elif keys[pygame.K_RIGHT]:
                self.motor = (1, 0)
            else:
                self.motor = (1, 1)
        elif keys[pygame.K_DOWN]:
            if keys[pygame.K_LEFT]:
                self.motor = (-1, 0)
            elif keys[pygame.K_RIGHT]:
                self.motor = (0, -1)
            else:
                self.motor = (-1, -1)
        elif keys[pygame.K_LEFT]:
            self.motor = (-1, 1)
        elif keys[pygame.K_RIGHT]:
            self.motor = (1, -1)

        self.motor = self.motor[0] / 2, self.motor[1] / 2

        if self.left_lock:
            self.motor = motor_prev[0], self.motor[1]
        if self.right_lock:
            self.motor = self.motor[0], motor_prev[1]

        self.screen.fill(BACK)

        self.left_rect = pygame.Rect(50 - HALF_A, 100 - self.motor[0] * 50 - HALF_A, A, A)
        self.right_rect = pygame.Rect(150 - HALF_A, 100 - self.motor[1] * 50 - HALF_A, A, A)
        self.top_rect = pygame.Rect(100 - HALF_A, 50 - HALF_A, A, A)
        self.bottom_rect = pygame.Rect(100 - HALF_A, 150 - HALF_A, A, A)

        pygame.draw.rect(self.screen, LOCK if self.left_lock else FRONT, self.left_rect)
        pygame.draw.rect(self.screen, LOCK if self.right_lock else FRONT, self.right_rect)
        pygame.draw.rect(self.screen, FRONT, self.top_rect, 0 if self.brush else WIDTH)
        pygame.draw.rect(self.screen, FRONT, self.bottom_rect, 0 if self.back_open else WIDTH)

        pygame.display.flip()

        return self.motor, self.brush, self.back_open
