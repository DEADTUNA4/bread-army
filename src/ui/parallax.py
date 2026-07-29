import pygame
import math
from settings import WINDOW_WIDTH, WINDOW_HEIGHT


class ParallaxBackground:
    def __init__(self):
        self.layers = []
        self.generated = False

    def generate(self, level_width, level_height):
        self.layers = []
        self.level_width = level_width
        self.level_height = level_height
        self.generated = True

        self.sky_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.sky_surface.fill((100, 160, 220))
        for y in range(WINDOW_HEIGHT):
            ratio = y / WINDOW_HEIGHT
            r = int(100 + ratio * 40)
            g = int(160 + ratio * 20)
            b = int(220 - ratio * 60)
            pygame.draw.line(self.sky_surface, (r, g, b), (0, y), (WINDOW_WIDTH, y))

        self.far_mountains = self._gen_mountains(WINDOW_WIDTH * 2, 200, (90, 120, 80), 0.4)
        self.mid_mountains = self._gen_mountains(WINDOW_WIDTH * 2, 160, (70, 100, 60), 0.6)
        self.near_hills = self._gen_mountains(WINDOW_WIDTH * 2, 120, (100, 140, 80), 0.8)

        self.cloud_surface = pygame.Surface((WINDOW_WIDTH * 3, 120), pygame.SRCALPHA)
        for _ in range(15):
            cx = pygame.time.get_ticks() % (WINDOW_WIDTH * 3)
            cy = 20 + (hash(str(_)) % 80)
            cw = 40 + (hash(str(_ + 100)) % 80)
            ch = 15 + (hash(str(_ + 200)) % 15)
            pygame.draw.ellipse(self.cloud_surface, (255, 255, 255, 120), (cx, cy, cw, ch))
            pygame.draw.ellipse(self.cloud_surface, (255, 255, 255, 80), (cx + 10, cy - 5, cw - 10, ch + 10))

    def _gen_mountains(self, width, max_height, color, jaggedness):
        surface = pygame.Surface((width, max_height + 20), pygame.SRCALPHA)
        points = [(0, max_height + 20)]
        x = 0
        while x < width:
            h = max_height * (0.5 + 0.5 * math.sin(x * 0.01 * jaggedness + hash(str(color)) * 0.001))
            h += max_height * 0.3 * math.sin(x * 0.003 + hash(str(color)) * 0.01)
            h = max(10, min(max_height, int(h)))
            points.append((x, max_height - h))
            x += 2
        points.append((width, max_height + 20))
        points.append((0, max_height + 20))

        dark = tuple(max(0, c - 30) for c in color)
        light = tuple(min(255, c + 20) for c in color)

        pygame.draw.polygon(surface, color, points)
        for i in range(1, len(points) - 2):
            if i % 4 == 0:
                peak = points[i]
                shadow_points = [peak, points[i + 1], (peak[0], max_height + 20)]
                if len(shadow_points) >= 3:
                    pygame.draw.polygon(surface, dark, shadow_points)

        return surface

    def render(self, surface, camera, frame=0):
        if not self.generated:
            surface.fill(SKY_BLUE)
            return

        surface.blit(self.sky_surface, (0, 0))

        far_offset = -camera.rect.x * 0.05 % WINDOW_WIDTH
        surface.blit(self.far_mountains, (far_offset, WINDOW_HEIGHT - self.far_mountains.get_height() - 40))

        mid_offset = -camera.rect.x * 0.15 % WINDOW_WIDTH
        surface.blit(self.mid_mountains, (mid_offset, WINDOW_HEIGHT - self.mid_mountains.get_height() - 20))

        near_offset = -camera.rect.x * 0.3 % WINDOW_WIDTH
        surface.blit(self.near_hills, (near_offset, WINDOW_HEIGHT - self.near_hills.get_height()))

        cloud_offset = -camera.rect.x * 0.02 % (WINDOW_WIDTH * 3)
        cloud_y_offset = math.sin(frame * 0.005) * 3
        surface.blit(self.cloud_surface, (cloud_offset, cloud_y_offset - 20))

        sun_x = WINDOW_WIDTH - 120
        sun_y = 60
        glow = 40 + int(math.sin(frame * 0.02) * 5)
        pygame.draw.circle(surface, (255, 255, 200), (sun_x, sun_y), glow + 20)
        pygame.draw.circle(surface, (255, 255, 150), (sun_x, sun_y), glow)
        pygame.draw.circle(surface, (255, 255, 100), (sun_x, sun_y), glow - 10)
