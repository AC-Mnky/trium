import math
import random
import time
from typing import List
import pygame
import pymunk
import pymunk.pygame_util
from pymunk.vec2d import Vec2d

rand = random.Random(time.time())

pygame.init()
screen = pygame.display.set_mode((700, 500))
clock = pygame.time.Clock()
running = True
font = pygame.font.SysFont("Arial", 16)

room = pymunk.Space()

# 1px = 5mm

room_left, room_right = 50, 650
room_top, room_bottom = 50, 450
static: List[pymunk.Shape] = [
    pymunk.Segment(room.static_body, (room_left, room_bottom), (room_left, room_top), 2),
    pymunk.Segment(room.static_body, (room_left, room_top), (room_right, room_top), 2),
    pymunk.Segment(room.static_body, (room_right, room_top), (room_right, room_bottom), 2),
    pymunk.Segment(room.static_body, (room_left, room_bottom), (room_right, room_bottom), 2),
]

for s in static:
    s.friction = 0.5
    s.group = 1
room.add(*static)


# algorithm
class Algorithm:
    def __init__(self, car):
        self.car = car
        self.old_angle = None
        self.stuck_pos = car.body.position
        self.stuck_time = 0

    def calc(self, camera_info):
        self.stuck_time += 1
        if self.stuck_time > 420:
            self.stuck_time = 200
        elif self.stuck_time > 360:
            return 1, 1
        elif self.stuck_time > 300:
            return 1, -1
        if (self.car.body.position - self.stuck_pos).length > self.car.length:
            self.stuck_pos = self.car.body.position
            self.stuck_time = 0
        if not (
                room_left + 30 < self.car.body.position.x < room_right - 30 and room_top + 30 < self.car.body.position.y
                < room_bottom - 30):
            self.old_angle = None
        for x in camera_info.seen_obstacles + camera_info.seen_cars:
            if (x - self.car.body.position).length < 45:
                if self.old_angle is None:
                    self.old_angle = self.car.body.angle
                return -1, 1
        if self.old_angle is not None:
            a = self.old_angle - self.car.body.angle
            a -= round(a / math.tau) * math.tau
            if a > 0.1:
                return 1, -0.25
            elif a < -0.1:
                return -0.25, 1
            else:
                self.old_angle = None
                return 1, 1
        if len(camera_info.seen_reds) == 0:
            self.old_angle = None
            return -1, 1
        pos = Vec2d(0, 0)
        shortest = 1000
        for r1 in camera_info.seen_reds:
            if (r1 - self.car.body.position).length < shortest:
                shortest = (r1 - self.car.body.position).length
                pos = r1
        a = (pos - self.car.body.position).angle - self.car.body.angle
        a -= round(a / math.tau) * math.tau
        if a > 0.1:
            return 1, -1
        elif a < -0.1:
            return -1, 1
        else:
            return 1, 1


# car
class Car:
    left_wheel_max_force = right_wheel_max_force = 10
    drag = 0.1
    angular_drag = 5000
    width = 20
    length = 30
    hole_width = 16
    hole_length = 26
    left_wheel = Vec2d(-5, -width / 2)
    right_wheel = Vec2d(-5, width / 2)
    camera_loc = Vec2d(0, 5)
    camera_height = 20
    camera_angle = math.radians(20)
    camera_half_width_angle = math.radians(40)
    camera_half_height_angle = math.radians(30)
    left_wheel_force = right_wheel_force = 0

    def camera_rela_pos(self, angle1, angle2):
        v = [math.cos(self.camera_angle) + math.sin(self.camera_angle) * math.tan(angle2),
             math.tan(angle1),
             math.sin(self.camera_angle) - math.cos(self.camera_angle) * math.tan(angle2)]
        if v[2] <= 0:
            v[2] = 0.02
        return self.camera_height * v[0] / v[2], self.camera_height * v[1] / v[2]

    def camera_info(self):
        seen_cars = []
        for c1 in cars:
            if len(self.camera.shapes_collide(c1.shape1).points) > 0 or \
                    len(self.camera.shapes_collide(c1.shape2).points) > 0 or \
                    len(self.camera.shapes_collide(c1.shape3).points) > 0:
                seen_cars.append(c1.body.position)
        seen_reds = []
        for r1 in reds:
            if len(self.camera.shapes_collide(r1.shape).points) > 0:
                seen_reds.append(r1.body.position)
        seen_obstacles = []
        for o1 in obstacles:
            if len(self.camera.shapes_collide(o1.shape).points) > 0:
                seen_obstacles.append(o1.body.position)
        return CameraInfo(seen_cars, seen_reds, seen_obstacles)

    def __init__(self, color, x, y):
        self.body = pymunk.Body(mass=1, moment=500)
        self.shape1 = pymunk.Poly(
            self.body,
            [
                (-self.length / 2, -self.width / 2),
                (-self.length / 2, self.width / 2),
                (self.length / 2 - self.hole_length, self.width / 2),
                (self.length / 2 - self.hole_length, -self.width / 2),
            ],
        )
        self.shape2 = pymunk.Poly(
            self.body,
            [
                (self.length / 2 - self.hole_length, -self.width / 2),
                (self.length / 2 - self.hole_length, -self.hole_width / 2),
                (self.length / 2, -self.hole_width / 2),
                (self.length / 2, -self.width / 2),
            ],
        )
        self.shape3 = pymunk.Poly(
            self.body,
            [
                (self.length / 2 - self.hole_length, self.width / 2),
                (self.length / 2 - self.hole_length, self.hole_width / 2),
                (self.length / 2, self.hole_width / 2),
                (self.length / 2, self.width / 2),
            ],
        )
        self.shape1.color = self.shape2.color = self.shape3.color = color
        self.body.position = (x, y)
        self.camera = pymunk.Poly(self.body,
                                  [self.camera_rela_pos(-self.camera_half_width_angle, -self.camera_half_height_angle),
                                   self.camera_rela_pos(-self.camera_half_width_angle, self.camera_half_height_angle),
                                   self.camera_rela_pos(self.camera_half_width_angle, self.camera_half_height_angle),
                                   self.camera_rela_pos(self.camera_half_width_angle, -self.camera_half_height_angle)])
        self.camera.color = (255, 255, 255, 32)
        self.camera.sensor = True
        self.algorithm = Algorithm(self)
        room.add(self.body, self.shape1, self.shape2, self.shape3, self.camera)

    def input(self, wheel_inputs):
        self.left_wheel_force = wheel_inputs[0] * self.left_wheel_max_force
        self.right_wheel_force = wheel_inputs[1] * self.right_wheel_max_force

    def physics(self):
        self.body.apply_impulse_at_local_point(
            self.left_wheel_force * Vec2d(1, 0), self.left_wheel
        )
        self.body.apply_impulse_at_local_point(
            self.right_wheel_force * Vec2d(1, 0), self.right_wheel
        )
        self.body.apply_impulse_at_world_point(
            -self.drag * self.body.velocity, self.body.position
        )
        self.body.torque -= self.body.angular_velocity * self.angular_drag
        self.left_wheel_force = self.right_wheel_force = 0


class CameraInfo:
    def __init__(self, seen_cars, seen_reds, seen_obstacles):
        self.seen_cars = seen_cars
        self.seen_reds = seen_reds
        self.seen_obstacles = seen_obstacles


class Red:
    drag = 0.001
    angular_drag = 0.5

    def __init__(self, x, y):
        self.body = pymunk.Body(mass=0.01, moment=0.1)
        self.shape = pymunk.Poly(
            self.body, [(-2.5, -2.5), (-2.5, 2.5), (2.5, 2.5), (2.5, -2.5)]
        )
        self.shape.color = (255, 0, 0, 255)
        self.body.position = (x, y)

    def physics(self):
        self.body.apply_impulse_at_world_point(
            -self.drag * self.body.velocity, self.body.position
        )
        self.body.torque -= self.body.angular_velocity * self.angular_drag


class Obstacle:
    drag = 0.5
    angular_drag = 5000

    def __init__(self, x, y):
        self.body = pymunk.Body(mass=2, moment=1000)
        self.shape = pymunk.Circle(self.body, 20)
        self.shape.color = (64, 64, 255, 255)
        self.body.position = (x, y)

    def physics(self):
        self.body.apply_impulse_at_world_point(
            -self.drag * self.body.velocity, self.body.position
        )
        self.body.torque -= self.body.angular_velocity * self.angular_drag


cars = [Car((255, 128, 0, 255), 100, 100), Car((64, 64, 255, 255), 500, 300)]

reds = []
for i in range(10):
    reds.append(Red(rand.randint(room_left + 2, room_right - 2), rand.randint(room_top + 2, room_bottom - 2)))
    room.add(reds[-1].body, reds[-1].shape)

obstacles = []
for i in range(5):
    obstacles.append(
        Obstacle(rand.randint(room_left + 30, room_right - 30), rand.randint(room_top + 30, room_bottom - 30)))
    room.add(obstacles[-1].body, obstacles[-1].shape)


def draw_rect_alpha(surface, color, rect):
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, shape_surf.get_rect())
    surface.blit(shape_surf, rect)


def draw_circle_alpha(surface, color, center, radius):
    target_rect = pygame.Rect(center, (0, 0)).inflate((radius * 2, radius * 2))
    shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
    pygame.draw.circle(shape_surf, color, (radius, radius), radius)
    surface.blit(shape_surf, target_rect)


def draw_polygon_alpha(surface, color, points):
    lx, ly = zip(*points)
    min_x, min_y, max_x, max_y = min(lx), min(ly), max(lx), max(ly)
    target_rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
    shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
    pygame.draw.polygon(shape_surf, color, [(x - min_x, y - min_y) for x, y in points])
    surface.blit(shape_surf, target_rect)


while running:
    for event in pygame.event.get():
        if (
                event.type == pygame.QUIT
                or event.type == pygame.KEYDOWN
                and (event.key in [pygame.K_ESCAPE, pygame.K_q])
        ):
            running = False

    # input
    keys = pygame.key.get_pressed()

    if keys[pygame.K_SPACE]:
        cars[0].input(cars[0].algorithm.calc(cars[0].camera_info()))
    else:
        if keys[pygame.K_UP]:
            if keys[pygame.K_LEFT]:
                cars[0].input((0, 1))
            elif keys[pygame.K_RIGHT]:
                cars[0].input((1, 0))
            else:
                cars[0].input((1, 1))
        elif keys[pygame.K_DOWN]:
            if keys[pygame.K_LEFT]:
                cars[0].input((-1, 0))
            elif keys[pygame.K_RIGHT]:
                cars[0].input((0, -1))
            else:
                cars[0].input((-1, -1))
        elif keys[pygame.K_LEFT]:
            cars[0].input((-1, 1))
        elif keys[pygame.K_RIGHT]:
            cars[0].input((1, -1))
    cars[1].input(cars[1].algorithm.calc(cars[1].camera_info()))

    # physics
    for c in cars:
        c.physics()
    for r in reds:
        r.physics()
    for o in obstacles:
        o.physics()

    # draw
    screen.fill(pygame.Color("black"))
    # room.debug_draw(draw_options)

    # cars camera
    for c in cars:
        draw_polygon_alpha(screen, c.camera.color,
                           [(v.rotated(c.body.angle) + c.body.position).int_tuple for v in
                            c.camera.get_vertices()])
    # cars
    for c in cars:
        for s in c.shape1, c.shape2, c.shape3:
            draw_polygon_alpha(screen, s.color, [(v.rotated(c.body.angle) + c.body.position).int_tuple for v in
                                                 s.get_vertices()])
    # reds
    for r in reds:
        draw_polygon_alpha(screen, (255, 0, 0, 255),
                           [(v.rotated(r.body.angle) + r.body.position).int_tuple for v in r.shape.get_vertices()])
    # obstacles
    for o in obstacles:
        draw_circle_alpha(screen, (64, 64, 255, 255), o.body.position, o.shape.radius)
    # wall
    draw_rect_alpha(screen, (255, 255, 255, 255), (room_left - 1, room_top - 1, 2, room_bottom - room_top + 2))
    draw_rect_alpha(screen, (255, 255, 255, 255), (room_left - 1, room_top - 1, room_right - room_left + 2, 2))
    draw_rect_alpha(screen, (255, 255, 255, 255), (room_right - 1, room_top - 1, 2, room_bottom - room_top + 2))
    draw_rect_alpha(screen, (255, 255, 255, 255), (room_left - 1, room_bottom - 1, room_right - room_left + 2, 2))

    pygame.display.flip()

    # tick
    fps = 60
    dt = 1.0 / fps
    room.step(dt)

    clock.tick(fps)
