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
        self.activated = False
        self.activation_range = 400
        self.patrol_timer = 0
        self.jump_timer = 0

        if enemy_type == "mold_slime":
            self.hp = 1
            self.speed = 1.2
            self.damage = 1
            self.color = (50, 180, 50)
            self.rect.height = TILE_SIZE - 8
        elif enemy_type == "stale_cracker":
            self.hp = 2
            self.speed = 0.8
            self.damage = 1
            self.color = (180, 150, 100)
        elif enemy_type == "evil_crouton":
            self.hp = 1
            self.speed = 2.5
            self.damage = 1
            self.color = (160, 100, 40)
            self.activation_range = 300
        elif enemy_type == "bread_golem":
            self.hp = 8
            self.speed = 0.6
            self.damage = 1
            self.color = (120, 80, 40)
            self.rect.width = TILE_SIZE * 2
            self.rect.height = TILE_SIZE * 2
            self.activation_range = 500
        elif enemy_type == "mold_king":
            self.hp = 15
            self.speed = 1.0
            self.damage = 1
            self.color = (30, 120, 30)
            self.rect.width = TILE_SIZE * 2
            self.rect.height = TILE_SIZE * 2
            self.activation_range = 600
        elif enemy_type == "crumb_fly":
            self.hp = 1
            self.speed = 1.5
            self.damage = 1
            self.color = (100, 80, 60)
            self.flying = True
            self.activation_range = 350

    def take_damage(self, amount=1):
        self.hp -= amount
        self.vx += random.choice([-2, 2])
        if self.hp <= 0:
            self.alive = False

    def update(self, tiles, player, dt=1.0):
        if not self.alive:
            return

        self.animation_timer += 1 * dt
        if self.animation_timer >= 12:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4

        if player and not player.dying:
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < self.activation_range:
                self.activated = True

        if not self.activated:
            self.patrol_timer += 1 * dt
            if self.patrol_timer > 120:
                self.direction *= -1
                self.patrol_timer = 0
            if not getattr(self, 'flying', False):
                self.vx = self.speed * 0.3 * self.direction
            else:
                self.vx = self.speed * 0.5 * math.sin(self.animation_timer * 0.05)
                self.vy = math.cos(self.animation_timer * 0.03) * self.speed * 0.5
        else:
            if player:
                dx = player.rect.centerx - self.rect.centerx
                self.direction = 1 if dx > 0 else -1

                if self.type == "mold_slime":
                    self.vx = self.speed * self.direction
                    self.jump_timer += 1 * dt
                    if self.jump_timer > 90 and self.on_ground:
                        self.vy = -7
                        self.jump_timer = 0
                elif self.type == "evil_crouton":
                    self.vx = self.speed * 1.2 * self.direction
                    self.jump_timer += 1 * dt
                    if self.jump_timer > 60 and self.on_ground:
                        self.vy = -8
                        self.jump_timer = 0
                elif self.type == "stale_cracker":
                    self.vx = self.speed * self.direction
                elif self.type == "bread_golem" or self.type == "mold_king":
                    self.vx = self.speed * self.direction
                    self.jump_timer += 1 * dt
                    if self.jump_timer > 150 and self.on_ground:
                        self.vy = -9
                        self.jump_timer = 0
                elif self.type == "crumb_fly":
                    angle = math.atan2(dy, dx)
                    self.vx = math.cos(angle) * self.speed
                    self.vy = math.sin(angle) * self.speed

        if not getattr(self, 'flying', False):
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

        if not getattr(self, 'flying', False):
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
        else:
            self.rect.y += self.vy * dt

        if self.rect.top > 1000:
            self.alive = False

    def get_attack_rect(self):
        if self.type in ("bread_golem", "mold_king"):
            return pygame.Rect(self.rect.x - 8, self.rect.y, self.rect.width + 16, self.rect.height)
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
            if self.activated:
                pygame.draw.ellipse(surface, (200, 50, 50), draw_rect, 2)
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
            if self.activated:
                pygame.draw.rect(surface, (255, 0, 0), (screen_rect.x + 8, screen_rect.y + 8, 6, 6))
                pygame.draw.rect(surface, (255, 0, 0), (screen_rect.right - 14, screen_rect.y + 8, 6, 6))
            else:
                pygame.draw.circle(surface, (0, 0, 0), (screen_rect.x + 8, screen_rect.y + 8), 3)
                pygame.draw.circle(surface, (0, 0, 0), (screen_rect.right - 8, screen_rect.y + 8), 3)
        elif self.type in ("bread_golem", "mold_king"):
            pygame.draw.rect(surface, self.color, screen_rect)
            arm_width = 12
            arm_height = screen_rect.height // 2
            left_arm = pygame.Rect(screen_rect.x - arm_width, screen_rect.y + 8, arm_width, arm_height)
            right_arm = pygame.Rect(screen_rect.right, screen_rect.y + 8, arm_width, arm_height)
            pygame.draw.rect(surface, self.color, left_arm)
            pygame.draw.rect(surface, self.color, right_arm)
            eye_color = (255, 0, 0) if self.activated else (80, 80, 80)
            pygame.draw.rect(surface, eye_color, (screen_rect.x + 16, screen_rect.y + 12, 24, 12))
            hp_bar_w = screen_rect.width
            hp_bar = pygame.Rect(screen_rect.x, screen_rect.y - 8, hp_bar_w * (self.hp / (15 if self.type == "mold_king" else 8)), 4)
            pygame.draw.rect(surface, (255, 0, 0), hp_bar)
        elif self.type == "crumb_fly":
            wing_offset = math.sin(self.animation_timer * 0.8) * 6
            pygame.draw.ellipse(surface, self.color, screen_rect)
            pygame.draw.line(surface, self.color, (screen_rect.centerx, screen_rect.centery), (screen_rect.x - 8, screen_rect.centery + wing_offset), 2)
            pygame.draw.line(surface, self.color, (screen_rect.centerx, screen_rect.centery), (screen_rect.right + 8, screen_rect.centery + wing_offset), 2)
            pygame.draw.circle(surface, (255, 0, 0), (screen_rect.x + 6, screen_rect.y + 6), 2)
            pygame.draw.circle(surface, (255, 0, 0), (screen_rect.right - 6, screen_rect.y + 6), 2)
