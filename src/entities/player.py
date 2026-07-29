import pygame
from settings import PLAYER_SPEED, PLAYER_JUMP, PLAYER_MAX_HEALTH, TILE_SIZE


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE - 4, TILE_SIZE * 2 - 4)
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.facing_right = True
        self.health = PLAYER_MAX_HEALTH
        self.max_health = PLAYER_MAX_HEALTH
        self.invincible = 0
        self.alive = True
        self.attack_timer = 0
        self.attacking = False
        self.attack_cooldown = 15
        self.powerup = None
        self.animation_frame = 0
        self.animation_timer = 0

    def handle_input(self, keys):
        self.vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -PLAYER_SPEED
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = PLAYER_SPEED
            self.facing_right = True
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vy = PLAYER_JUMP

    def attack(self):
        if self.attack_timer <= 0:
            self.attacking = True
            self.attack_timer = self.attack_cooldown
            return True
        return False

    def take_damage(self, amount=1):
        if self.invincible > 0 or not self.alive:
            return False
        self.health -= amount
        self.invincible = 60
        if self.health <= 0:
            self.health = 0
            self.alive = False
        return True

    def heal(self, amount=1):
        self.health = min(self.health + amount, self.max_health)

    def set_powerup(self, powerup):
        self.powerup = powerup

    def update(self, dt=1.0):
        if not self.alive:
            return

        if self.invincible > 0:
            self.invincible -= 1 * dt

        if self.attack_timer > 0:
            self.attack_timer -= 1 * dt
            if self.attack_timer <= 0:
                self.attacking = False

        self.animation_timer += 1 * dt
        if self.animation_timer >= 8:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4

        if self.rect.top > 1000:
            self.alive = False

    def get_attack_rect(self):
        if not self.attacking:
            return None
        if self.facing_right:
            return pygame.Rect(self.rect.right, self.rect.centery - 16, 20, 32)
        else:
            return pygame.Rect(self.rect.left - 20, self.rect.centery - 16, 20, 32)

    def draw(self, surface, camera):
        screen_rect = camera.apply(self.rect)
        if self.invincible > 0 and int(self.invincible // 4) % 2 == 0:
            return

        body_color = (210, 180, 140)
        if self.powerup == "toast":
            body_color = (180, 120, 60)
        elif self.powerup == "croissant":
            body_color = (220, 190, 140)

        pygame.draw.ellipse(surface, body_color, screen_rect)
        hat_rect = pygame.Rect(screen_rect.x - 4, screen_rect.y - 8, screen_rect.width + 8, 12)
        pygame.draw.ellipse(surface, (50, 50, 150), hat_rect)

        eye_x = screen_rect.right - 10 if self.facing_right else screen_rect.left + 2
        pygame.draw.circle(surface, (0, 0, 0), (eye_x, screen_rect.y + 12), 3)

        if self.attacking:
            sword_rect = pygame.Rect(0, 0, 16, 4)
            if self.facing_right:
                sword_rect.midleft = screen_rect.midright
            else:
                sword_rect.midright = screen_rect.midleft
            pygame.draw.rect(surface, (200, 200, 200), sword_rect)
