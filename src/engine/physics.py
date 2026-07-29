import pygame
from settings import GRAVITY, TILE_SIZE


class Physics:
    def __init__(self, gravity=GRAVITY):
        self.gravity = gravity

    def apply_gravity(self, entity, dt=1.0):
        entity.vy += self.gravity * dt
        entity.vy = min(entity.vy, 15)

    def move_and_collide(self, entity, tiles, dt=1.0, map_bounds=None):
        entity.on_ground = False

        entity.vx *= 0.85 if entity.on_ground else 0.95
        if abs(entity.vx) < 0.1:
            entity.vx = 0

        step_size = 8
        dx = entity.vx * dt
        dy = entity.vy * dt

        steps_x = max(1, int(abs(dx) / step_size) + 1)
        steps_y = max(1, int(abs(dy) / step_size) + 1)

        step_dx = dx / steps_x
        step_dy = dy / steps_y

        for _ in range(int(steps_x)):
            entity.rect.x += step_dx
            for tile in tiles:
                if entity.rect.colliderect(tile.rect):
                    if step_dx > 0:
                        entity.rect.right = tile.rect.left
                    elif step_dx < 0:
                        entity.rect.left = tile.rect.right
                    entity.vx = 0

        for _ in range(int(steps_y)):
            entity.rect.y += step_dy
            for tile in tiles:
                if entity.rect.colliderect(tile.rect):
                    if step_dy > 0:
                        entity.rect.bottom = tile.rect.top
                        entity.vy = 0
                        entity.on_ground = True
                    elif step_dy < 0:
                        entity.rect.top = tile.rect.bottom
                        entity.vy = 0

        if map_bounds:
            if entity.rect.left < 0:
                entity.rect.left = 0
                entity.vx = 0
            if entity.rect.right > map_bounds[0]:
                entity.rect.right = map_bounds[0]
                entity.vx = 0
            if entity.rect.top < 0:
                entity.rect.top = 0
                entity.vy = 0

    def check_collision(self, a, b):
        return a.rect.colliderect(b.rect)
