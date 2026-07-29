import pygame
import math
from settings import TILE_SIZE


class MovingPlatform:
    def __init__(self, x, y, width, move_x=0, move_y=128, speed=0.03):
        self.rect = pygame.Rect(x, y, width, TILE_SIZE // 2)
        self.start_x = x
        self.start_y = y
        self.move_x = move_x
        self.move_y = move_y
        self.speed = speed
        self.timer = 0
        self.prev_x = x
        self.prev_y = y
        self.solid = True

    def update(self, dt=1.0):
        self.prev_x = self.rect.x
        self.prev_y = self.rect.y
        self.timer += self.speed * dt
        self.rect.x = self.start_x + math.sin(self.timer) * self.move_x
        self.rect.y = self.start_y + math.sin(self.timer) * self.move_y

    @property
    def carry_dx(self):
        return self.rect.x - self.prev_x

    @property
    def carry_dy(self):
        return self.rect.y - self.prev_y

    def draw(self, surface, camera):
        screen_rect = camera.apply(self.rect)
        pygame.draw.rect(surface, (100, 70, 40), screen_rect)
        pygame.draw.rect(surface, (140, 100, 60), screen_rect, 2)
        for i in range(0, self.rect.width, 8):
            ax = screen_rect.x + i
            pygame.draw.line(surface, (80, 55, 30), (ax, screen_rect.y), (ax, screen_rect.bottom), 1)


class CrumblingBlock:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.solid = True
        self.shaking = False
        self.shake_timer = 0
        self.crumble_time = 30
        self.respawn_time = 180
        self.timer = 0
        self.alpha = 255
        self.visible = True
        self.original_x = x
        self.original_y = y

    def on_step(self):
        if not self.shaking and self.solid:
            self.shaking = True
            self.shake_timer = self.crumble_time

    def update(self, dt=1.0):
        if self.shaking:
            self.shake_timer -= 1 * dt
            self.rect.x = self.original_x + (2 if int(self.shake_timer) % 4 < 2 else -2)
            if self.shake_timer <= 0:
                self.solid = False
                self.visible = False
                self.shaking = False
                self.timer = self.respawn_time
                self.rect.x = self.original_x

        if not self.solid:
            self.timer -= 1 * dt
            if self.timer <= 0:
                self.solid = True
                self.visible = True
                self.rect.x = self.original_x
                self.rect.y = self.original_y

    def draw(self, surface, camera):
        if not self.visible:
            return
        screen_rect = camera.apply(self.rect)
        color = (160, 120, 60) if not self.shaking else (180, 130, 70)
        pygame.draw.rect(surface, color, screen_rect)
        pygame.draw.rect(surface, (120, 80, 40), screen_rect, 1)
        if self.shaking:
            pygame.draw.line(surface, (100, 60, 30),
                           (screen_rect.x + 4, screen_rect.y + 4),
                           (screen_rect.centerx, screen_rect.centery), 1)
            pygame.draw.line(surface, (100, 60, 30),
                           (screen_rect.right - 4, screen_rect.y + 8),
                           (screen_rect.centerx, screen_rect.centery + 4), 1)


class DisappearingBlock:
    def __init__(self, x, y, appear_time=120, disappear_time=60):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.appear_time = appear_time
        self.disappear_time = disappear_time
        self.solid = True
        self.visible = True
        self.timer = appear_time
        self.phase = "solid"

    def update(self, dt=1.0):
        self.timer -= 1 * dt
        if self.phase == "solid" and self.timer <= 0:
            self.phase = "fading"
            self.timer = 20
        elif self.phase == "fading" and self.timer <= 0:
            self.phase = "gone"
            self.solid = False
            self.visible = False
            self.timer = self.disappear_time
        elif self.phase == "gone" and self.timer <= 0:
            self.phase = "appearing"
            self.timer = 20
        elif self.phase == "appearing" and self.timer <= 0:
            self.phase = "solid"
            self.solid = True
            self.visible = True
            self.timer = self.appear_time

    def draw(self, surface, camera):
        if not self.visible:
            return
        screen_rect = camera.apply(self.rect)
        if self.phase == "fading":
            pulse = int(abs(self.timer) * 10) % 2
            if pulse:
                pygame.draw.rect(surface, (180, 180, 220, 128), screen_rect)
            else:
                pygame.draw.rect(surface, (200, 200, 240), screen_rect)
        elif self.phase == "appearing":
            pulse = int(abs(self.timer) * 10) % 2
            if pulse:
                pygame.draw.rect(surface, (200, 200, 240), screen_rect)
            else:
                pygame.draw.rect(surface, (180, 180, 220), screen_rect)
        else:
            pygame.draw.rect(surface, (200, 200, 240), screen_rect)
        pygame.draw.rect(surface, (160, 160, 200), screen_rect, 1)


class FakeBlock:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.solid = False
        self.visible = True
        self.triggered = False

    def on_step(self):
        self.triggered = True

    def update(self, dt=1.0):
        if self.triggered:
            self.rect.y += 2 * dt

    def draw(self, surface, camera):
        if not self.visible:
            return
        screen_rect = camera.apply(self.rect)
        pygame.draw.rect(surface, (100, 60, 30), screen_rect)
        pygame.draw.rect(surface, (140, 100, 60), screen_rect, 2)
