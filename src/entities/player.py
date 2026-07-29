import pygame
import random
from settings import PLAYER_SPEED, PLAYER_JUMP, PLAYER_MAX_HEALTH, TILE_SIZE, RAGE_QUOTES, DEATH_DELAY


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
        self.death_timer = 0
        self.dying = False
        self.death_quote = ""
        self.attack_timer = 0
        self.attacking = False
        self.attack_cooldown = 15
        self.animation_frame = 0
        self.animation_timer = 0
        self.death_count = 0
        self.kickback = 0

    def handle_input(self, keys):
        if self.dying:
            return
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
        if self.dying or self.attack_timer > 0:
            return False
        self.attacking = True
        self.attack_timer = self.attack_cooldown
        return True

    def take_damage(self, amount=1):
        if self.invincible > 0 or not self.alive or self.dying:
            return False
        self.health -= amount
        self.invincible = 30
        if self.health <= 0:
            self.health = 0
            self.die()
        return True

    def die(self):
        if self.dying:
            return
        self.dying = True
        self.alive = False
        self.death_timer = DEATH_DELAY
        self.death_count += 1
        self.death_quote = random.choice(RAGE_QUOTES)
        self.vy = PLAYER_JUMP * 0.7
        self.kickback = random.choice([-1, 1]) * 3

    def heal(self, amount=1):
        self.health = min(self.health + amount, self.max_health)

    def update(self, dt=1.0):
        if self.dying:
            self.death_timer -= 1 * dt
            self.vy += 0.3 * dt
            self.vx = self.kickback * 0.9
            self.kickback *= 0.95
            self.rect.x += self.vx * dt
            self.rect.y += self.vy * dt
            return

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

    def get_attack_rect(self):
        if not self.attacking:
            return None
        if self.facing_right:
            return pygame.Rect(self.rect.right, self.rect.centery - 16, 20, 32)
        else:
            return pygame.Rect(self.rect.left - 20, self.rect.centery - 16, 20, 32)

    def draw(self, surface, camera):
        screen_rect = camera.apply(self.rect)

        if self.dying:
            flash = int(self.death_timer // 4) % 2
            if flash:
                pygame.draw.ellipse(surface, (255, 100, 100), screen_rect)
            else:
                pygame.draw.ellipse(surface, (255, 200, 200), screen_rect)

            font = pygame.font.Font(None, 16)
            text = font.render("x_x", True, (0, 0, 0))
            text_rect = text.get_rect(center=screen_rect.center)
            surface.blit(text, text_rect)
            return

        if not self.alive:
            return

        if self.invincible > 0 and int(self.invincible // 3) % 2 == 0:
            return

        body_color = (210, 180, 140)
        pygame.draw.ellipse(surface, body_color, screen_rect)
        hat_rect = pygame.Rect(screen_rect.x - 2, screen_rect.y - 6, screen_rect.width + 4, 10)
        pygame.draw.ellipse(surface, (50, 50, 150), hat_rect)

        eye_x = screen_rect.right - 8 if self.facing_right else screen_rect.left + 2
        if self.vx != 0:
            eye_y = screen_rect.y + 10 + int(abs(self.vx))
        else:
            eye_y = screen_rect.y + 12
        pygame.draw.circle(surface, (0, 0, 0), (eye_x, min(eye_y, screen_rect.bottom - 8)), 3)

        if self.attacking:
            sword_rect = pygame.Rect(0, 0, 16, 4)
            if self.facing_right:
                sword_rect.midleft = screen_rect.midright
            else:
                sword_rect.midright = screen_rect.midleft
            pygame.draw.rect(surface, (200, 200, 200), sword_rect)
