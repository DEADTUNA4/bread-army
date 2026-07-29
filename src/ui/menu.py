import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, BLACK, WHITE, TAN, BROWN


class Menu:
    def __init__(self, game, options, title="Bread Army"):
        self.game = game
        self.options = options
        self.title = title
        self.selected = 0

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


class PauseMenu(Menu):
    def __init__(self, game):
        options = [
            ("Resume", lambda: game.change_state("playing")),
            ("Main Menu", lambda: game.change_state("main_menu")),
        ]
        super().__init__(game, options, "Paused")


class GameOverMenu(Menu):
    def __init__(self, game):
        options = [
            ("Retry", lambda: game.change_state("playing")),
            ("Main Menu", lambda: game.change_state("main_menu")),
        ]
        super().__init__(game, options, "Game Over")


class WinMenu(Menu):
    def __init__(self, game):
        options = [
            ("Play Again", lambda: game.change_state("playing")),
            ("Main Menu", lambda: game.change_state("main_menu")),
        ]
        super().__init__(game, options, "Victory!")
