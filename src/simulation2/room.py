import random

import pygame
import pymunk


class Room:
    def __init__(self, random_seed, rect: pygame.Rect):
        self.rand = random.Random(random_seed)
        self.time = 0
        self.space = pymunk.Space()
        self.rect = rect

        self.walls = []
        self.reds = []
        self.yellows = []
        self.cars = []

    def make_walls(self, wall_width, friction, elasticity):
        r = self.rect
        self.walls = [
            pymunk.Segment(self.space.static_body, (r.left, r.bottom), (r.left, r.top), wall_width),
            pymunk.Segment(self.space.static_body, (r.left, r.top), (r.right, r.top), wall_width),
            pymunk.Segment(self.space.static_body, (r.right, r.top), (r.right, r.bottom), wall_width),
            pymunk.Segment(self.space.static_body, (r.left, r.bottom), (r.right, r.bottom), wall_width),
        ]
        for wall in self.walls:
            wall.friction = friction
            wall.elasticity = elasticity
            wall.group = 'wall'
        self.space.add(*self.walls)


if __name__ == "__main__":
    import time
    example_room = Room(time.time(), pygame.Rect(50, 50, 600, 400))
    example_room.make_walls(2, 0.5)
