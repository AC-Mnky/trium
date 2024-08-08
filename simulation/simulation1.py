import sys
import math
from typing import List

import pymunk, pygame
import pymunk.pygame_util
from pymunk.vec2d import Vec2d

import random, time

rand = random.Random(time.time())



pygame.init()
screen = pygame.display.set_mode((700, 500))
clock = pygame.time.Clock()
running = True
font = pygame.font.SysFont("Arial", 16)

room = pymunk.Space()
draw_options = pymunk.pygame_util.DrawOptions(screen)

# 1px = 5mm

static: List[pymunk.Shape] = [
    pymunk.Segment(room.static_body, (50, 450), (50, 50), 2),
    pymunk.Segment(room.static_body, (50, 50), (650, 50), 2),
    pymunk.Segment(room.static_body, (650, 50), (650, 450), 2),
    pymunk.Segment(room.static_body, (50, 450), (650, 450), 2),
]

for s in static:
    s.friction = 0.5
    s.group = 1
room.add(*static)


# car
class car:
    left_wheel_max_force = right_wheel_max_force = 10
    drag = 0.1
    angular_drag = 5000
    width = 20
    length = 30
    hole_width = 16
    hole_length = 26
    left_wheel = Vec2d(-5,-width/2)
    right_wheel = Vec2d(-5,width/2)
    camera_loc = Vec2d(0,5)
    camera_height = 20
    camera_angle = math.radians(20)
    camera_half_width_angle = math.radians(40)
    camera_half_height_angle = math.radians(30)
    left_wheel_force = right_wheel_force = 0
    
    def camera_relapos(self, angle1, angle2):
        v = [math.cos(self.camera_angle)+math.sin(self.camera_angle)*math.tan(angle2),
            math.tan(angle1),
            math.sin(self.camera_angle)-math.cos(self.camera_angle)*math.tan(angle2)]
        if(v[2]<=0):
            v[2] = 0.01
        return (self.camera_height*v[0]/v[2], self.camera_height*v[1]/v[2])
    
    def __init__(self,x,y):
        self.body = pymunk.Body(mass=1, moment=500)
        self.shape1 = pymunk.Poly(self.body, [(-self.length/2,-self.width/2),(-self.length/2,self.width/2),(self.length/2-self.hole_length,self.width/2),(self.length/2-self.hole_length,-self.width/2)])
        self.shape2 = pymunk.Poly(self.body, [(self.length/2-self.hole_length,-self.width/2),(self.length/2-self.hole_length,-self.hole_width/2),(self.length/2,-self.hole_width/2),(self.length/2,-self.width/2)])
        self.shape3 = pymunk.Poly(self.body, [(self.length/2-self.hole_length,self.width/2),(self.length/2-self.hole_length,self.hole_width/2),(self.length/2,self.hole_width/2),(self.length/2,self.width/2)])
        self.shape1.color = self.shape2.color = self.shape3.color = (255, 128, 0, 255)
        self.body.position = (x,y)
        self.camera = pymunk.Poly(self.body, [self.camera_relapos(-self.camera_half_width_angle,-self.camera_half_height_angle),self.camera_relapos(-self.camera_half_width_angle,self.camera_half_height_angle),self.camera_relapos(self.camera_half_width_angle,self.camera_half_height_angle),self.camera_relapos(self.camera_half_width_angle,-self.camera_half_height_angle)])
        self.camera.color = (64,64,64,255)
        self.camera.sensor = True
        room.add(self.body, self.shape1, self.shape2, self.shape3, self.camera)
        
    def input(self, wheel_inputs):
        self.left_wheel_force = wheel_inputs[0] * self.left_wheel_max_force
        self.right_wheel_force = wheel_inputs[1] * self.right_wheel_max_force
        
    def physics(self):
        self.body.apply_impulse_at_local_point(self.left_wheel_force * Vec2d(1,0), self.left_wheel)
        self.body.apply_impulse_at_local_point(self.right_wheel_force * Vec2d(1,0), self.right_wheel)
        self.body.apply_impulse_at_world_point(-self.drag * self.body.velocity, self.body.position)
        self.body.torque -= self.body.angular_velocity * self.angular_drag
        self.left_wheel_force = self.right_wheel_force = 0
        
    def algorithm(self, seen_reds):
        if(len(seen_reds) == 0):
            return (-1, 1)
        pos = Vec2d(0,0)
        shortest = 1000
        for p in seen_reds:
            if((p - self.body.position).length < shortest):
                shortest = (p - self.body.position).length
                pos = p
        a = (pos - self.body.position).angle - self.body.angle
        a -= round(a/math.tau)*math.tau
        if(a>0.1):
            return (1, -1)
        elif(a<-0.1):
            return (-1, 1)
        else:
            return (1, 1)



class red:
    drag = 0.001
    angular_drag = 0.5
    def __init__(self,x,y):
        self.body = pymunk.Body(mass=0.01, moment=0.1)
        self.shape = pymunk.Poly(self.body, [(-2.5,-2.5),(-2.5,2.5),(2.5,2.5),(2.5,-2.5)])
        self.shape.color = (255,0,0,255)
        self.body.position = (x,y)
    def physics(self):
        self.body.apply_impulse_at_world_point(-self.drag *self.body.velocity,self.body.position)
        self.body.torque -= self.body.angular_velocity * self.angular_drag

class obstacle:
    drag = 0.5
    angular_drag = 5000
    def __init__(self,x,y):
        self.body = pymunk.Body(mass=2, moment=1000)
        self.shape = pymunk.Circle(self.body, 20)
        self.shape.color = (192,192,192,255)
        self.body.position = (x,y)
    def physics(self):
        self.body.apply_impulse_at_world_point(-self.drag *self.body.velocity,self.body.position)
        self.body.torque -= self.body.angular_velocity * self.angular_drag
        
        
car0 = car(100,100)

reds = []
for i in range(10):
    reds.append(red(rand.randint(50,650), rand.randint(50,450)))
    room.add(reds[-1].body, reds[-1].shape)
    
obstacles = []
for i in range(5):
    obstacles.append(obstacle(rand.randint(80,620), rand.randint(80,420)))
    room.add(obstacles[-1].body, obstacles[-1].shape)




while running:
    for event in pygame.event.get():
        if (
            event.type == pygame.QUIT
            or event.type == pygame.KEYDOWN
            and (event.key in [pygame.K_ESCAPE, pygame.K_q])
        ):
            running = False
            
        
        
    #input
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_SPACE]:
        seen_reds = []
        for r in reds:
            if(len(car0.camera.shapes_collide(r.shape).points) > 0):
                seen_reds.append(r.body.position)
        car0.input(car0.algorithm(seen_reds))
    else:
        if keys[pygame.K_UP]:
            if keys[pygame.K_LEFT]:
                car0.input((0,1))
            elif keys[pygame.K_RIGHT]:
                car0.input((1,0))
            else:
                car0.input((1,1))
        elif keys[pygame.K_DOWN]:
            if keys[pygame.K_LEFT]:
                car0.input((-1,0))
            elif keys[pygame.K_RIGHT]:
                car0.input((0,-1))
            else:
                car0.input((-1,-1))
        elif keys[pygame.K_LEFT]:
            car0.input((-1,1))
        elif keys[pygame.K_RIGHT]:
            car0.input((1,-1))
    
    # physics
    car0.physics()
    for x in reds + obstacles:
        x.physics()
    
    
    # draw
    screen.fill(pygame.Color("black"))
    room.debug_draw(draw_options)
    pygame.display.flip()

    # tick
    fps = 60
    dt = 1.0 / fps
    room.step(dt)

    clock.tick(fps)


