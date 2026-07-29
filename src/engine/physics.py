import pygame
from settings import GRAVITY, TILE_SIZE


class Physics:
    def __init__(self, gravity=GRAVITY):
        self.gravity = gravity

    def apply_gravity(self, entity, dt=1.0):
        entity.vy += self.gravity * dt
        entity.vy = min(entity.vy, 15)

    def move_and_collide(self, entity, tiles, dt=1.0):
        entity.on_ground = False

        entity.vx *= 0.85 if entity.on_ground else 0.95
        if abs(entity.vx) < 0.1:
            entity.vx = 0

        entity.rect.x += entity.vx * dt
        self._collide_horizontal(entity, tiles)

        entity.rect.y += entity.vy * dt
        self._collide_vertical(entity, tiles)

    def _collide_horizontal(self, entity, tiles):
        for tile in tiles:
            if entity.rect.colliderect(tile.rect):
                if entity.vx > 0:
                    entity.rect.right = tile.rect.left
                elif entity.vx < 0:
                    entity.rect.left = tile.rect.right
                entity.vx = 0

    def _collide_vertical(self, entity, tiles):
        for tile in tiles:
            if entity.rect.colliderect(tile.rect):
                if entity.vy > 0:
                    entity.rect.bottom = tile.rect.top
                    entity.vy = 0
                    entity.on_ground = True
                elif entity.vy < 0:
                    entity.rect.top = tile.rect.bottom
                    entity.vy = 0

    def check_collision(self, a, b):
        return a.rect.colliderect(b.rect)
