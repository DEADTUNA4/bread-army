import pygame
from settings import WINDOW_WIDTH, RED, GOLD, WHITE, GRAY, BLACK


class HUD:
    def __init__(self):
        self.font_large = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 20)
        self.heart_anim = 0

    def update(self, dt=1.0):
        self.heart_anim += 0.05 * dt

    def render(self, surface, player, level_name, score=0, deaths=0):
        bar_surf = pygame.Surface((WINDOW_WIDTH, 90), pygame.SRCALPHA)
        bar_surf.fill((0, 0, 0, 100))
        pygame.draw.line(bar_surf, (100, 100, 100, 80), (0, 88), (WINDOW_WIDTH, 88), 2)
        surface.blit(bar_surf, (0, 0))

        heart_x = 20
        heart_y = 14
        for i in range(player.max_health):
            hx = heart_x + i * 32
            hy = heart_y

            if i < player.health:
                pulse = abs(int(self.heart_anim * 60) % 4 - 2)
                inner_color = (255 - pulse * 10, 50 + pulse * 5, 50 + pulse * 5)
                border_color = (200, 30, 30)
            else:
                inner_color = (50, 50, 50)
                border_color = (30, 30, 30)

            pygame.draw.polygon(surface, border_color,
                              [(hx + 12, hy + 2), (hx + 6, hy - 4), (hx, hy + 4),
                               (hx + 12, hy + 22), (hx + 24, hy + 4), (hx + 18, hy - 4)])
            pygame.draw.polygon(surface, inner_color,
                              [(hx + 12, hy + 6), (hx + 8, hy + 2), (hx + 4, hy + 6),
                               (hx + 12, hy + 18), (hx + 20, hy + 6), (hx + 16, hy + 2)])

        if player.powerup:
            badge_rect = pygame.Rect(20, 56, 60, 22)
            pygame.draw.rect(surface, (60, 60, 60), badge_rect, border_radius=4)
            pygame.draw.rect(surface, GOLD, badge_rect, 1, border_radius=4)
            pw_text = self.font_small.render(player.powerup.upper(), True, GOLD)
            surface.blit(pw_text, pw_text.get_rect(center=badge_rect.center))

        level_text = self.font_large.render(level_name, True, WHITE)
        shadow = self.font_large.render(level_name, True, BLACK)
        level_rect = level_text.get_rect(topright=(WINDOW_WIDTH - 18, 14))
        surface.blit(shadow, (level_rect.x + 1, level_rect.y + 1))
        surface.blit(level_text, level_rect)

        score_text = self.font_small.render(f"Score: {score}", True, (200, 200, 200))
        score_rect = score_text.get_rect(topright=(WINDOW_WIDTH - 18, 40))
        surface.blit(score_text, score_rect)

        if deaths > 0:
            death_text = self.font_small.render(f"Deaths: {deaths}", True, (255, 120, 120))
            death_rect = death_text.get_rect(topright=(WINDOW_WIDTH - 18, 60))
            surface.blit(death_text, death_rect)
