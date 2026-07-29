import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, BLACK, WHITE, TAN, BROWN, RED, GOLD
from src.engine.state import State


class Menu(State):
    def __init__(self, game, options, title="Bread Army"):
        super().__init__(game)
        self.options = options
        self.title = title
        self.selected = 0

    def enter(self):
        self.selected = 0

    def exit(self):
        pass

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.options[self.selected][1]()

    def update(self, dt):
        pass

    def render(self, surface):
        surface.fill((50, 30, 10))

        title_font = pygame.font.Font(None, 64)
        title_text = title_font.render(self.title, True, TAN)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 100))
        surface.blit(title_text, title_rect)

        subtitle_font = pygame.font.Font(None, 24)
        subtitle_text = subtitle_font.render("A Baguette Soldier's Quest", True, BROWN)
        subtitle_rect = subtitle_text.get_rect(center=(WINDOW_WIDTH // 2, 140))
        surface.blit(subtitle_text, subtitle_rect)

        option_font = pygame.font.Font(None, 36)
        for i, (text, _) in enumerate(self.options):
            color = TAN if i == self.selected else (100, 80, 60)
            if i == self.selected:
                text = f"> {text} <"
            else:
                text = f"  {text}  "
            opt_text = option_font.render(text, True, color)
            opt_rect = opt_text.get_rect(center=(WINDOW_WIDTH // 2, 250 + i * 50))
            surface.blit(opt_text, opt_rect)

        credit_font = pygame.font.Font(None, 16)
        credit_text = credit_font.render("DEADTUNA4 - 2026", True, (80, 60, 40))
        credit_rect = credit_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30))
        surface.blit(credit_text, credit_rect)


class MainMenu(Menu):
    def __init__(self, game):
        options = [
            ("Start Game", lambda: game.change_state("playing")),
            ("Quit", lambda: setattr(game, 'running', False)),
        ]
        super().__init__(game, options, "Bread Army")

    def render(self, surface):
        surface.fill((30, 15, 5))

        title_font = pygame.font.Font(None, 72)
        title_text = title_font.render("BREAD ARMY", True, GOLD)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 80))
        surface.blit(title_text, title_rect)

        sub_font = pygame.font.Font(None, 28)
        sub_text = sub_font.render("Prepare to suffer.", True, RED)
        sub_rect = sub_text.get_rect(center=(WINDOW_WIDTH // 2, 130))
        surface.blit(sub_text, sub_rect)

        option_font = pygame.font.Font(None, 36)
        for i, (text, _) in enumerate(self.options):
            color = GOLD if i == self.selected else (100, 80, 60)
            if i == self.selected:
                text = f"> {text} <"
            else:
                text = f"  {text}  "
            opt_text = option_font.render(text, True, color)
            opt_rect = opt_text.get_rect(center=(WINDOW_WIDTH // 2, 250 + i * 50))
            surface.blit(opt_text, opt_rect)

        credit_font = pygame.font.Font(None, 16)
        credit_text = credit_font.render("DEADTUNA4 - 2026", True, (80, 60, 40))
        credit_rect = credit_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30))
        surface.blit(credit_text, credit_rect)


class PauseMenu(Menu):
    def __init__(self, game):
        options = [
            ("Resume", lambda: game.change_state("playing")),
            ("Main Menu", lambda: game.change_state("main_menu")),
        ]
        super().__init__(game, options, "Paused")


class GameOverMenu(Menu):
    def __init__(self, game):
        self.deaths = 0
        self.score = 0
        options = [
            ("Try Again", lambda: game.change_state("playing")),
            ("Main Menu", lambda: game.change_state("main_menu")),
        ]
        super().__init__(game, options, "YOU DIED")

    def render(self, surface):
        surface.fill((20, 0, 0))

        title_font = pygame.font.Font(None, 80)
        title_text = title_font.render("YOU DIED", True, RED)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 100))
        surface.blit(title_text, title_rect)

        stat_font = pygame.font.Font(None, 32)
        death_text = stat_font.render(f"Total Deaths: {self.deaths}", True, (200, 200, 200))
        death_rect = death_text.get_rect(center=(WINDOW_WIDTH // 2, 180))
        surface.blit(death_text, death_rect)

        score_text = stat_font.render(f"Score: {self.score}", True, GOLD)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, 220))
        surface.blit(score_text, score_rect)

        option_font = pygame.font.Font(None, 36)
        for i, (text, _) in enumerate(self.options):
            color = GOLD if i == self.selected else (100, 80, 60)
            if i == self.selected:
                text = f"> {text} <"
            else:
                text = f"  {text}  "
            opt_text = option_font.render(text, True, color)
            opt_rect = opt_text.get_rect(center=(WINDOW_WIDTH // 2, 320 + i * 50))
            surface.blit(opt_text, opt_rect)


class WinMenu(Menu):
    def __init__(self, game):
        self.deaths = 0
        self.score = 0
        options = [
            ("Play Again", lambda: game.change_state("playing")),
            ("Main Menu", lambda: game.change_state("main_menu")),
        ]
        super().__init__(game, options, "YOU SURVIVED")

    def render(self, surface):
        surface.fill((10, 20, 10))

        title_font = pygame.font.Font(None, 72)
        title_text = title_font.render("YOU SURVIVED", True, GOLD)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 80))
        surface.blit(title_text, title_rect)

        stat_font = pygame.font.Font(None, 32)
        death_text = stat_font.render(f"Total Deaths: {self.deaths}", True, (200, 200, 200))
        death_rect = death_text.get_rect(center=(WINDOW_WIDTH // 2, 160))
        surface.blit(death_text, death_rect)

        score_text = stat_font.render(f"Final Score: {self.score}", True, GOLD)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, 200))
        surface.blit(score_text, score_rect)

        if self.deaths == 0:
            gg_font = pygame.font.Font(None, 28)
            gg_text = gg_font.render("IMPOSSIBLE. You didn't die once?", True, (100, 255, 100))
            gg_rect = gg_text.get_rect(center=(WINDOW_WIDTH // 2, 250))
            surface.blit(gg_text, gg_rect)
        elif self.deaths < 5:
            gg_font = pygame.font.Font(None, 28)
            gg_text = gg_font.render(f"Not bad... only {self.deaths} deaths.", True, (200, 200, 200))
            gg_rect = gg_text.get_rect(center=(WINDOW_WIDTH // 2, 250))
            surface.blit(gg_text, gg_rect)
        elif self.deaths < 20:
            gg_font = pygame.font.Font(None, 28)
            gg_text = gg_font.render(f"You suffered {self.deaths} times. Worth it?", True, (255, 150, 100))
            gg_rect = gg_text.get_rect(center=(WINDOW_WIDTH // 2, 250))
            surface.blit(gg_text, gg_rect)
        else:
            gg_font = pygame.font.Font(None, 28)
            gg_text = gg_font.render(f"{self.deaths} deaths. You are a masochist.", True, RED)
            gg_rect = gg_text.get_rect(center=(WINDOW_WIDTH // 2, 250))
            surface.blit(gg_text, gg_rect)

        option_font = pygame.font.Font(None, 36)
        for i, (text, _) in enumerate(self.options):
            color = GOLD if i == self.selected else (100, 80, 60)
            if i == self.selected:
                text = f"> {text} <"
            else:
                text = f"  {text}  "
            opt_text = option_font.render(text, True, color)
            opt_rect = opt_text.get_rect(center=(WINDOW_WIDTH // 2, 340 + i * 50))
            surface.blit(opt_text, opt_rect)
