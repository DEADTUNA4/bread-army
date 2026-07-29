import pygame
import math
import random
from settings import TILE_SIZE, ENEMY_SPEED


class Enemy:
    def __init__(self, x, y, enemy_type="mold_slime"):
        self.rect = pygame.Rect(x, y, TILE_SIZE - 4, TILE_SIZE - 4)
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.type = enemy_type
        self.alive = True
        self.hp = 1
        self.speed = ENEMY_SPEED
        self.direction = -1
        self.damage = 1
        self.animation_frame = 0
        self.animation_timer = 0

        if enemy_type == "mold_slime":
            self.hp = 1
            self.speed = 0.8
            self.damage = 1
            self.color = (50, 180, 50)
            self.rect.height = TILE_SIZE - 8
        elif enemy_type == "stale_cracker":
            self.hp = 2
            self.speed = 0.5
            self.damage = 1
            self.color = (180, 150, 100)
        elif enemy_type == "evil_crouton":
            self.hp = 1
            self.speed = 2.0
            self.damage = 1
            self.color = (160, 100, 40)
        elif enemy_type == "bread_golem":
            self.hp = 10
            self.speed = 0.4
            self.damage = 2
            self.color = (120, 80, 40)
            self.rect.width = TILE_SIZE * 2
            self.rect.height = TILE_SIZE * 2

    def take_damage(self, amount=1):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False

    def update(self, tiles, player, dt=1.0):
        if not self.alive:
            return

        self.animation_timer += 1 * dt
        if self.animation_timer >= 12:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4

        if self.type == "mold_slime":
            self.vx = self.speed * self.direction
        elif self.type == "evil_crouton":
            if player:
                dx = player.rect.centerx - self.rect.centerx
                dy = player.rect.centery - self.rect.centery
                dist = math.sqrt(dx * dx + dy * dy)
                if dist > 0:
                    self.vx = (dx / dist) * self.speed
                    self.vy = (dy / dist) * self.speed * 0.5
            else:
                self.vx = self.speed * self.direction
        elif self.type == "stale_cracker":
            self.vx = self.speed * self.direction
        elif self.type == "bread_golem":
            self.vx = 0
            if player:
                dx = player.rect.centerx - self.rect.centerx
                self.direction = 1 if dx > 0 else -1

        self.vy += 0.5 * dt
        if self.vy > 15:
            self.vy = 15

        self.rect.x += self.vx * dt
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.vx > 0:
                    self.rect.right = tile.rect.left
                elif self.vx < 0:
                    self.rect.left = tile.rect.right
                self.direction *= -1
                self.vx *= -1

        self.rect.y += self.vy * dt
        self.on_ground = False
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.vy > 0:
                    self.rect.bottom = tile.rect.top
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:
                    self.rect.top = tile.rect.bottom
                    self.vy = 0

        if self.rect.top > 1000:
            self.alive = False

    def get_attack_rect(self):
        if self.type == "bread_golem":
            return pygame.Rect(self.rect.x - 10, self.rect.y, self.rect.width + 20, self.rect.height)
        return self.rect

    def draw(self, surface, camera):
        if not self.alive:
            return
        screen_rect = camera.apply(self.rect)
        wobble = math.sin(self.animation_timer * 0.5) * 2

        if self.type == "mold_slime":
            draw_rect = screen_rect.copy()
            draw_rect.y += wobble
            pygame.draw.ellipse(surface, self.color, draw_rect)
            pygame.draw.circle(surface, (0, 0, 0), (draw_rect.x + 8, draw_rect.y + 8), 3)
            pygame.draw.circle(surface, (0, 0, 0), (draw_rect.x + draw_rect.width - 8, draw_rect.y + 8), 3)
        elif self.type == "stale_cracker":
            pygame.draw.rect(surface, self.color, screen_rect)
            pygame.draw.rect(surface, (100, 80, 50), screen_rect, 2)
            crack_color = (80, 60, 30)
            pygame.draw.line(surface, crack_color, screen_rect.topleft, screen_rect.center, 1)
            pygame.draw.line(surface, crack_color, screen_rect.midtop, screen_rect.bottomright, 1)
        elif self.type == "evil_crouton":
            pygame.draw.rect(surface, self.color, screen_rect)
            pygame.draw.circle(surface, (255, 0, 0), (screen_rect.x + 8, screen_rect.y + 8), 3)
            pygame.draw.circle(surface, (255, 0, 0), (screen_rect.x + screen_rect.width - 8, screen_rect.y + 8), 3)
        elif self.type == "bread_golem":
            pygame.draw.rect(surface, self.color, screen_rect)
            arm_width = 8
            arm_height = screen_rect.height // 2
            left_arm = pygame.Rect(screen_rect.x - arm_width, screen_rect.y + 8, arm_width, arm_height)
            right_arm = pygame.Rect(screen_rect.right, screen_rect.y + 8, arm_width, arm_height)
            pygame.draw.rect(surface, self.color, left_arm)
            pygame.draw.rect(surface, self.color, right_arm)
            eye_rect = pygame.Rect(screen_rect.x + 16, screen_rect.y + 12, 32, 16)
            pygame.draw.rect(surface, (255, 0, 0), eye_rect)
