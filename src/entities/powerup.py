import pygame
import math
from settings import TILE_SIZE


class PowerUp:
    def __init__(self, x, y, powerup_type="toast"):
        self.rect = pygame.Rect(x, y, TILE_SIZE - 8, TILE_SIZE - 8)
        self.type = powerup_type
        self.alive = True
        self.float_timer = 0

        self.colors = {
            "toast": (180, 120, 60),
            "croissant": (220, 190, 140),
            "bagel": (200, 160, 100),
            "sourdough": (160, 140, 100),
        }
        self.color = self.colors.get(powerup_type, (255, 255, 255))
        self.label = {
            "toast": "T",
            "croissant": "C",
            "bagel": "B",
            "sourdough": "S",
        }.get(powerup_type, "?")

    def update(self, dt=1.0):
        if not self.alive:
            return
        self.float_timer += 0.05 * dt

    def apply(self, player):
        player.set_powerup(self.type)
        if self.type == "toast":
            player.heal(1)
        self.alive = False

    def draw(self, surface, camera):
        if not self.alive:
            return
        screen_rect = camera.apply(self.rect)
        float_offset = math.sin(self.float_timer) * 4
        draw_rect = screen_rect.move(0, float_offset)

        pygame.draw.ellipse(surface, self.color, draw_rect)
        pygame.draw.ellipse(surface, (255, 255, 255, 128), draw_rect, 2)

        font = pygame.font.Font(None, 20)
        text = font.render(self.label, True, (255, 255, 255))
        text_rect = text.get_rect(center=draw_rect.center)
        surface.blit(text, text_rect)
