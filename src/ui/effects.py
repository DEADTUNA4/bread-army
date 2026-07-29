import pygame
import random
import math


class Particle:
    def __init__(self, x, y, vx, vy, color, lifetime=30, size=4):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.alive = True

    def update(self, dt=1.0):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 0.1 * dt
        self.lifetime -= 1 * dt
        if self.lifetime <= 0:
            self.alive = False

    def draw(self, surface, camera):
        if not self.alive:
            return
        screen_pos = camera.apply(pygame.Rect(self.x, self.y, 0, 0))
        alpha = int((self.lifetime / self.max_lifetime) * 255)
        size = int(self.size * (self.lifetime / self.max_lifetime))
        if size < 1:
            size = 1
        color = (*self.color[:3], alpha)
        pygame.draw.circle(surface, color[:3], (int(screen_pos.x), int(screen_pos.y)), size)


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, count=10, color=(200, 180, 140), speed=3):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed_v = random.uniform(1, speed)
            vx = math.cos(angle) * speed_v
            vy = math.sin(angle) * speed_v - 1
            lifetime = random.randint(15, 40)
            size = random.randint(2, 6)
            self.particles.append(Particle(x, y, vx, vy, color, lifetime, size))

    def update(self, dt=1.0):
        for p in self.particles[:]:
            p.update(dt)
            if not p.alive:
                self.particles.remove(p)

    def draw(self, surface, camera):
        for p in self.particles:
            p.draw(surface, camera)


class ScreenShake:
    def __init__(self):
        self.intensity = 0
        self.offset = (0, 0)

    def shake(self, intensity=5, duration=10):
        self.intensity = intensity

    def update(self, dt=1.0):
        if self.intensity > 0:
            self.offset = (
                random.randint(-int(self.intensity), int(self.intensity)),
                random.randint(-int(self.intensity), int(self.intensity)),
            )
            self.intensity -= 0.5 * dt
            if self.intensity < 0.5:
                self.intensity = 0
        else:
            self.offset = (0, 0)
