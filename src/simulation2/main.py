import numpy as np
import time
import pygame
import draw_alpha

from room import Room
from car import Car
from collectables import Red, Yellow
from camera_convert import CameraState

# 1px = 5mm

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((700, 500))
    clock = pygame.time.Clock()
    running = True
    font = pygame.font.SysFont("Arial", 16)

    room = Room(time.time(), pygame.Rect(50, 50, 600, 400))
    room.make_walls(2, 0.5, 1)

    Car(room,
        (255, 128, 0, 255),
        100, 100,
        CameraState((21, 0, -40), (70, 0), (64, 50), (640, 480)))
    for i in range(10):
        Red(room,
            room.rand.randint(room.rect.left + 2, room.rect.right - 2),
            room.rand.randint(room.rect.top + 2, room.rect.bottom - 2),)
        Yellow(room,
               room.rand.randint(room.rect.left + 3, room.rect.right - 3),
               room.rand.randint(room.rect.top + 3, room.rect.bottom - 3),)

    while running:
        for event in pygame.event.get():
            if (
                    event.type == pygame.QUIT
                    or event.type == pygame.KEYDOWN
                    and (event.key in [pygame.K_ESCAPE, pygame.K_q])
            ):
                running = False

        # output
        keys = pygame.key.get_pressed()

        for i, c in enumerate(room.cars):
            if i != 0 or keys[pygame.K_SPACE]:
                c.output(c.algorithm.get_output(c.camera.get_input(), c.imu.get_input(), c.ultrasonic.get_input()))
            else:
                if keys[pygame.K_UP]:
                    if keys[pygame.K_LEFT]:
                        c.output((0, 1))
                    elif keys[pygame.K_RIGHT]:
                        c.output((1, 0))
                    else:
                        c.output((1, 1))
                elif keys[pygame.K_DOWN]:
                    if keys[pygame.K_LEFT]:
                        c.output((-1, 0))
                    elif keys[pygame.K_RIGHT]:
                        c.output((0, -1))
                    else:
                        c.output((-1, -1))
                elif keys[pygame.K_LEFT]:
                    c.output((-1, 1))
                elif keys[pygame.K_RIGHT]:
                    c.output((1, -1))

        # physics
        for x in room.cars + room.reds + room.yellows:
            x.physics()

        # draw
        screen.fill(pygame.Color("black"))
        for c in room.cars:
            draw_alpha.polygon(screen, (255, 255, 255, 128) if c.camera_capturing else (255, 255, 255, 32),
                               [(v.rotated(c.body.angle) + c.body.position).int_tuple for v in
                                c.camera_range.get_vertices()])
        for c in room.cars:
            for s in c.shapes:
                draw_alpha.polygon(screen, s.color, [(v.rotated(c.body.angle) + c.body.position).int_tuple for v in
                                                     s.get_vertices()])
        for r in room.reds:
            draw_alpha.polygon(screen, (255, 0, 0, 255),
                               [(v.rotated(r.body.angle) + r.body.position).int_tuple for v in r.shape.get_vertices()])
        for y in room.yellows:
            draw_alpha.circle(screen, (255, 255, 0, 255), y.body.position, 3)
        draw_alpha.rectangle(screen, (255, 255, 255, 255),
                             (room.rect.left - 1, room.rect.top - 1, 2, room.rect.bottom - room.rect.top + 2))
        draw_alpha.rectangle(screen, (255, 255, 255, 255),
                             (room.rect.left - 1, room.rect.top - 1, room.rect.right - room.rect.left + 2, 2))
        draw_alpha.rectangle(screen, (255, 255, 255, 255),
                             (room.rect.right - 1, room.rect.top - 1, 2, room.rect.bottom - room.rect.top + 2))
        draw_alpha.rectangle(screen, (255, 255, 255, 255),
                             (room.rect.left - 1, room.rect.bottom - 1, room.rect.right - room.rect.left + 2, 2))

        pygame.display.flip()

        # tick
        fps = 60
        dt = 1.0 / fps
        room.space.step(dt)
        room.time += dt

        clock.tick(fps)
