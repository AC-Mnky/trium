# 关于仿真的基本方法论：
# 尽可能用简单的方法模拟现实情况，从而使得写出好的算法更为方便。最终在现实中测试时所使用的算法相较于仿真中使用的算法，只需要做一些参数的调整，不需要增加新的代码。

import time

import draw_alpha
import numpy as np
import pygame
from camera_convert import CameraState
from car import Car
from collectables import Red, Yellow
from room import Room

from algorithm import merge_radius

# 1px = 5mm
simulation_speed_up = 10
always_algorithm = True
display_algorithm = True
display_camera_and_brush = True

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((700, 500))
    clock = pygame.time.Clock()
    running = True
    font = pygame.font.SysFont("Arial", 16)

    room = Room(time.time(), pygame.Rect(50, 50, 600, 400))
    room.make_walls(2, 0.5, 1)

    Car(
        room,
        (255, 128, 0, 255),
        200,
        200,
        np.pi * 1.25,
        CameraState((205 / 5, 0, -170 / 5), (70, 0), (62.2, 48.8), (640, 480)),
    )
    # Car(room,
    #     (0, 0, 255, 255),
    #     500, 300, np.pi * 0.25,
    #     CameraState((205 / 5, 0, -170 / 5), (70, 0), (62.2, 48.8), (640, 480)))
    # Car(room,
    #     (128, 128, 128, 255),
    #     200, 300, np.pi * 0.75,
    #     CameraState((205 / 5, 0, -170 / 5), (70, 0), (62.2, 48.8), (640, 480)))
    # Car(room,
    #     (128, 128, 128, 255),
    #     500, 200, np.pi * 1.75,
    #     CameraState((205 / 5, 0, -170 / 5), (70, 0), (62.2, 48.8), (640, 480)))
    for i in range(5):
        Red(
            room,
            room.rand.randint(room.rect.left + 2, room.rect.right - 2),
            room.rand.randint(room.rect.top + 2, room.rect.bottom - 2),
        )
        Yellow(
            room,
            room.rand.randint(room.rect.left + 3, room.rect.right - 3),
            room.rand.randint(room.rect.top + 3, room.rect.bottom - 3),
        )

    while running:
        for event in pygame.event.get():
            if (
                event.type == pygame.QUIT
                or event.type == pygame.KEYDOWN
                and (event.key in [pygame.K_ESCAPE, pygame.K_q])
            ):
                running = False

        for c in room.cars:
            c.algorithm.update(c.camera.get_input(), c.encoder.get_input(), c.imu.get_input(), c.ultrasonic.get_input())

        # player control
        keys = pygame.key.get_pressed()

        for i, c in enumerate(room.cars):
            if keys[pygame.K_r]:
                c.algorithm.reset()
            if i > 1 or keys[pygame.K_SPACE] or always_algorithm:
                c.output(c.algorithm.wheel_output, c.algorithm.back_open_output)
            else:
                if i == 0:
                    back_open = keys[pygame.K_o]
                    if keys[pygame.K_UP]:
                        if keys[pygame.K_LEFT]:
                            c.output((0, 1), back_open)
                        elif keys[pygame.K_RIGHT]:
                            c.output((1, 0), back_open)
                        else:
                            c.output((1, 1), back_open)
                    elif keys[pygame.K_DOWN]:
                        if keys[pygame.K_LEFT]:
                            c.output((-1, 0), back_open)
                        elif keys[pygame.K_RIGHT]:
                            c.output((0, -1), back_open)
                        else:
                            c.output((-1, -1), back_open)
                    elif keys[pygame.K_LEFT]:
                        c.output((-1, 1), back_open)
                    elif keys[pygame.K_RIGHT]:
                        c.output((1, -1), back_open)
                elif i == 1:
                    back_open = keys[pygame.K_e]
                    if keys[pygame.K_w]:
                        if keys[pygame.K_a]:
                            c.output((0, 1), back_open)
                        elif keys[pygame.K_d]:
                            c.output((1, 0), back_open)
                        else:
                            c.output((1, 1), back_open)
                    elif keys[pygame.K_s]:
                        if keys[pygame.K_a]:
                            c.output((-1, 0), back_open)
                        elif keys[pygame.K_d]:
                            c.output((0, -1), back_open)
                        else:
                            c.output((-1, -1), back_open)
                    elif keys[pygame.K_a]:
                        c.output((-1, 1), back_open)
                    elif keys[pygame.K_d]:
                        c.output((1, -1), back_open)

        # physics
        for x in room.cars + room.reds + room.yellows:
            if x is not None:
                x.physics()

        # # car eat collectables
        # for c in room.cars:
        #     c_pos = c.body.position
        #     for i, r in enumerate(room.reds):
        #         if r is not None and c_pos.get_distance(r.body.position) < c.hole_width / 2:
        #             room.space.remove(r.body, r.shape)
        #             room.reds[i] = None
        #     for i, y in enumerate(room.yellows):
        #         if y is not None and c_pos.get_distance(y.body.position) < c.hole_width / 2:
        #             room.space.remove(y.body, y.shape)
        #             room.yellows[i] = None

        # draw
        screen.fill(pygame.Color("black"))
        if display_camera_and_brush:
            for c in room.cars:
                draw_alpha.polygon(
                    screen,
                    (255, 255, 255, 128) if c.camera_capturing else (255, 255, 255, 32),
                    [(v.rotated(c.body.angle) + c.body.position).int_tuple for v in c.camera_range.get_vertices()],
                )
                draw_alpha.polygon(
                    screen,
                    (255, 255, 255, 64),
                    [(v.rotated(c.body.angle) + c.body.position).int_tuple for v in c.brush.get_vertices()],
                )

        if display_algorithm:
            for x, v in room.cars[0].algorithm.predicted_collectables.items():
                draw_alpha.circle(screen, (255, 255 if v[1] == 1 else 0, 0, 16 * np.minimum(v[0], 8)), x, merge_radius)
                if v[2] > 0:
                    draw_alpha.circle(screen, (255, 255, 255, 128), x, merge_radius)

        for c in room.cars:
            for s in c.shapes:
                draw_alpha.polygon(
                    screen, s.color, [(v.rotated(c.body.angle) + c.body.position).int_tuple for v in s.get_vertices()]
                )
        for r in room.reds:
            if r is not None:
                draw_alpha.polygon(
                    screen,
                    (255, 0, 0, 255),
                    [(v.rotated(r.body.angle) + r.body.position).int_tuple for v in r.shape.get_vertices()],
                )
        for y in room.yellows:
            if y is not None:
                draw_alpha.circle(screen, (255, 255, 0, 255), y.body.position, 3)

        draw_alpha.rectangle(
            screen,
            (255, 255, 255, 255),
            (room.rect.left - 1, room.rect.top - 1, 2, room.rect.bottom - room.rect.top + 2),
        )
        draw_alpha.rectangle(
            screen,
            (255, 255, 255, 255),
            (room.rect.left - 1, room.rect.top - 1, room.rect.right - room.rect.left + 2, 2),
        )
        draw_alpha.rectangle(
            screen,
            (255, 255, 255, 255),
            (room.rect.right - 1, room.rect.top - 1, 2, room.rect.bottom - room.rect.top + 2),
        )
        draw_alpha.rectangle(
            screen,
            (255, 255, 255, 255),
            (room.rect.left - 1, room.rect.bottom - 1, room.rect.right - room.rect.left + 2, 2),
        )

        pygame.display.flip()

        # tick
        fps = 60
        dt = 1.0 / fps
        room.space.step(dt)
        room.time += dt

        clock.tick(fps * simulation_speed_up)
