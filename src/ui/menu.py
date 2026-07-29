import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, BLACK, WHITE, TAN, BROWN, RED, GOLD, GRAY
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

    def _render_options(self, surface, y_start=250):
        option_font = pygame.font.Font(None, 36)
        for i, (text, _) in enumerate(self.options):
            color = GOLD if i == self.selected else (100, 80, 60)
            if i == self.selected:
                display = f"> {text} <"
            else:
                display = f"  {text}  "
            opt_text = option_font.render(display, True, color)
            opt_rect = opt_text.get_rect(center=(WINDOW_WIDTH // 2, y_start + i * 50))
            surface.blit(opt_text, opt_rect)


class MainMenu(Menu):
    def __init__(self, game):
        self._game_ref = game
        options = [
            ("Start Game", lambda: game.change_state("playing")),
            ("Settings", lambda: self._open_settings(game)),
            ("Quit", lambda: setattr(game, 'running', False)),
        ]
        super().__init__(game, options, "Bread Army")

    def _open_settings(self, game):
        settings = game.state_machine.states.get("settings")
        if settings:
            settings.set_return("main_menu")
        game.change_state("settings")

    def enter(self):
        super().enter()

    def render(self, surface):
        surface.fill((20, 10, 5))

        for y in range(0, WINDOW_HEIGHT, 4):
            ratio = y / WINDOW_HEIGHT
            r = int(20 + ratio * 15)
            g = int(10 + ratio * 8)
            b = int(5 + ratio * 5)
            pygame.draw.line(surface, (r, g, b), (0, y), (WINDOW_WIDTH, y))

        title_font = pygame.font.Font(None, 80)
        shadow = title_font.render("BREAD ARMY", True, (30, 15, 5))
        surface.blit(shadow, shadow.get_rect(center=(WINDOW_WIDTH // 2 + 3, 93)))
        title_text = title_font.render("BREAD ARMY", True, GOLD)
        surface.blit(title_text, title_text.get_rect(center=(WINDOW_WIDTH // 2, 90)))

        sub_font = pygame.font.Font(None, 28)
        sub_text = sub_font.render("Prepare to suffer.", True, RED)
        surface.blit(sub_text, sub_text.get_rect(center=(WINDOW_WIDTH // 2, 140)))

        bread_y = 170
        crust = pygame.Rect(WINDOW_WIDTH // 2 - 40, bread_y, 80, 30)
        pygame.draw.ellipse(surface, (210, 180, 140), crust)
        pygame.draw.ellipse(surface, (160, 120, 70), crust, 2)

        self._render_options(surface, 260)

        credit_font = pygame.font.Font(None, 16)
        credit_text = credit_font.render("DEADTUNA4 - 2026", True, (80, 60, 40))
        surface.blit(credit_text, credit_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30)))


class PauseMenu(Menu):
    def __init__(self, game):
        self._game_ref = game
        options = [
            ("Resume", lambda: game.change_state("playing")),
            ("Settings", lambda: self._open_settings(game)),
            ("Main Menu", lambda: game.change_state("main_menu")),
        ]
        super().__init__(game, options, "Paused")

    def _open_settings(self, game):
        settings = game.state_machine.states.get("settings")
        if settings:
            settings.set_return("paused")
        game.change_state("settings")

    def enter(self):
        super().enter()

    def render(self, surface):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        title_font = pygame.font.Font(None, 64)
        title_text = title_font.render("PAUSED", True, TAN)
        surface.blit(title_text, title_text.get_rect(center=(WINDOW_WIDTH // 2, 120)))

        self._render_options(surface, 220)


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
        surface.fill((15, 0, 0))

        for y in range(0, WINDOW_HEIGHT, 3):
            ratio = y / WINDOW_HEIGHT
            r = int(15 + ratio * 20)
            pygame.draw.line(surface, (r, 0, 0), (0, y), (WINDOW_WIDTH, y))

        title_font = pygame.font.Font(None, 80)
        shadow = title_font.render("YOU DIED", True, (60, 0, 0))
        surface.blit(shadow, shadow.get_rect(center=(WINDOW_WIDTH // 2 + 3, 103)))
        title_text = title_font.render("YOU DIED", True, RED)
        surface.blit(title_text, title_text.get_rect(center=(WINDOW_WIDTH // 2, 100)))

        stat_font = pygame.font.Font(None, 32)
        death_text = stat_font.render(f"Total Deaths: {self.deaths}", True, (200, 200, 200))
        surface.blit(death_text, death_text.get_rect(center=(WINDOW_WIDTH // 2, 180)))

        score_text = stat_font.render(f"Score: {self.score}", True, GOLD)
        surface.blit(score_text, score_text.get_rect(center=(WINDOW_WIDTH // 2, 220)))

        self._render_options(surface, 320)


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
        surface.fill((5, 15, 5))

        for y in range(0, WINDOW_HEIGHT, 3):
            ratio = y / WINDOW_HEIGHT
            g = int(15 + ratio * 15)
            pygame.draw.line(surface, (5, g, 5), (0, y), (WINDOW_WIDTH, y))

        title_font = pygame.font.Font(None, 72)
        shadow = title_font.render("YOU SURVIVED", True, (30, 30, 0))
        surface.blit(shadow, shadow.get_rect(center=(WINDOW_WIDTH // 2 + 3, 83)))
        title_text = title_font.render("YOU SURVIVED", True, GOLD)
        surface.blit(title_text, title_text.get_rect(center=(WINDOW_WIDTH // 2, 80)))

        stat_font = pygame.font.Font(None, 32)
        surface.blit(stat_font.render(f"Total Deaths: {self.deaths}", True, (200, 200, 200)),
                     stat_font.render(f"Total Deaths: {self.deaths}", True, (200, 200, 200)).get_rect(center=(WINDOW_WIDTH // 2, 160)))
        surface.blit(stat_font.render(f"Final Score: {self.score}", True, GOLD),
                     stat_font.render(f"Final Score: {self.score}", True, GOLD).get_rect(center=(WINDOW_WIDTH // 2, 200)))

        gg_font = pygame.font.Font(None, 28)
        if self.deaths == 0:
            gg = gg_font.render("IMPOSSIBLE. You didn't die once?", True, (100, 255, 100))
        elif self.deaths < 5:
            gg = gg_font.render(f"Not bad... only {self.deaths} deaths.", True, (200, 200, 200))
        elif self.deaths < 20:
            gg = gg_font.render(f"You suffered {self.deaths} times. Worth it?", True, (255, 150, 100))
        else:
            gg = gg_font.render(f"{self.deaths} deaths. You are a masochist.", True, RED)
        surface.blit(gg, gg.get_rect(center=(WINDOW_WIDTH // 2, 250)))

        self._render_options(surface, 340)
