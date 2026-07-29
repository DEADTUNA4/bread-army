import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT


class Camera:
    def __init__(self, width, height):
        self.rect = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.smooth = 0.1

    def follow(self, target):
        x = target.rect.centerx - WINDOW_WIDTH // 2
        y = target.rect.centery - WINDOW_HEIGHT // 2

        x = max(0, min(x, self.width - WINDOW_WIDTH))
        y = max(0, min(y, self.height - WINDOW_HEIGHT))

        self.rect.x = self.rect.x + (x - self.rect.x) * self.smooth
        self.rect.y = self.rect.y + (y - self.rect.y) * self.smooth

    def apply(self, rect):
        return rect.move(-self.rect.x, -self.rect.y)

    def reset(self):
        self.rect.x = 0
        self.rect.y = 0
