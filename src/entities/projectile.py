import pygame
from settings import TILE_SIZE


class Projectile:
    def __init__(self, x, y, vx, vy, owner="player", color=(255, 255, 200)):
        self.rect = pygame.Rect(x, y, 8, 8)
        self.vx = vx
        self.vy = vy
        self.owner = owner
        self.color = color
        self.alive = True
        self.lifetime = 120

    def update(self, tiles, dt=1.0):
        if not self.alive:
            return

        self.rect.x += self.vx * dt
        self.rect.y += self.vy * dt
        self.lifetime -= 1 * dt

        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                self.alive = False
                return

        if self.lifetime <= 0:
            self.alive = False

    def draw(self, surface, camera):
        if not self.alive:
            return
        screen_rect = camera.apply(self.rect)
        pygame.draw.circle(surface, self.color, screen_rect.center, 4)
        pygame.draw.circle(surface, (255, 255, 255), screen_rect.center, 2)
