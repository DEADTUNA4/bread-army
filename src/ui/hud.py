import pygame
from settings import WINDOW_WIDTH, TILE_SIZE, RED, GOLD, WHITE


class HUD:
    def __init__(self):
        self.font = pygame.font.Font(None, 24)

    def render(self, surface, player, level_name, score=0, deaths=0):
        heart_x = 16
        heart_y = 16
        for i in range(player.max_health):
            color = RED if i < player.health else (60, 60, 60)
            pygame.draw.rect(surface, color, (heart_x + i * 28, heart_y, 24, 24))
            pygame.draw.rect(surface, (200, 50, 50) if i < player.health else (40, 40, 40), (heart_x + i * 28, heart_y, 24, 24), 2)

        if player.powerup:
            powerup_text = self.font.render(f"{player.powerup.upper()}", True, GOLD)
            surface.blit(powerup_text, (16, 50))

        level_text = self.font.render(level_name, True, WHITE)
        level_rect = level_text.get_rect(topright=(WINDOW_WIDTH - 16, 16))
        surface.blit(level_text, level_rect)

        score_text = self.font.render(f"SCORE: {score}", True, WHITE)
        score_rect = score_text.get_rect(topright=(WINDOW_WIDTH - 16, 40))
        surface.blit(score_text, score_rect)

        if deaths > 0:
            death_text = self.font.render(f"DEATHS: {deaths}", True, (255, 100, 100))
            death_rect = death_text.get_rect(topright=(WINDOW_WIDTH - 16, 64))
            surface.blit(death_text, death_rect)
