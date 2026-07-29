import pygame
import random
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from settings import WINDOW_WIDTH, WINDOW_HEIGHT, SKY_BLUE, RED, ORANGE, DARK_RED, WHITE, BLACK, GOLD, DEATH_DELAY
from src.engine.game import Game
from src.engine.state import State
from src.engine.physics import Physics
from src.engine.camera import Camera
from src.level.tilemap import TileMap
from src.level.spawner import Spawner
from src.entities.player import Player
from src.entities.projectile import Projectile
from src.ui.menu import MainMenu, PauseMenu, GameOverMenu, WinMenu
from src.ui.hud import HUD
from src.ui.effects import ParticleSystem, ScreenShake
from src.online.level_manager import LevelManager

LEVELS = ["level_01", "level_02", "level_03", "level_04", "level_05"]


class PlayingState(State):
    def __init__(self, game):
        super().__init__(game)
        self.physics = Physics()
        self.hud = HUD()
        self.particles = ParticleSystem()
        self.screen_shake = ScreenShake()
        self.level_manager = LevelManager()
        self.score = 0
        self.level_index = 0
        self.total_deaths = 0
        self.frame_counter = 0
        self.rage_flash = 0
        self.rage_quote = ""
        self.rage_quote_timer = 0
        self.reset_level()

    def reset_level(self):
        self.level_name = LEVELS[self.level_index]
        level_path = self.level_manager.get_level_path(self.level_name)
        if level_path is None:
            level_path = f"levels/{self.level_name}.json"

        self.tilemap = TileMap()
        self.tilemap.load(level_path)

        self.spawner = Spawner(level_path)
        self.camera = Camera(self.tilemap.pixel_width, self.tilemap.pixel_height)
        self.projectiles = []

        player_x, player_y = self.spawner.player_start
        self.player = Player(player_x, player_y)
        self.player.death_count = self.total_deaths

        self.enemies = [e for e in self.spawner.get_entities() if hasattr(e, 'hp')]
        self.powerups = [p for p in self.spawner.get_entities() if not hasattr(p, 'hp')]

        self.entities = self.spawner.get_entities()
        self.goal_x = self.tilemap.pixel_width - 64

    def enter(self):
        self.total_deaths = 0
        self.score = 0
        self.level_index = 0
        self.rage_flash = 0
        self.rage_quote = ""
        self.rage_quote_timer = 0
        self.reset_level()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.change_state("paused")
            elif event.key in (pygame.K_f, pygame.K_e):
                if self.player.attack():
                    attack_rect = self.player.get_attack_rect()
                    for enemy in self.enemies[:]:
                        if enemy.alive and attack_rect and attack_rect.colliderect(enemy.rect):
                            enemy.take_damage(1)
                            self.particles.emit(enemy.rect.centerx, enemy.rect.centery, 12, (200, 180, 140))
                            self.screen_shake.shake(3, 5)
                            if not enemy.alive:
                                self.score += 100

    def update(self, dt):
        self.frame_counter += 1

        if self.rage_quote_timer > 0:
            self.rage_quote_timer -= 1 * dt

        if self.rage_flash > 0:
            self.rage_flash -= 1 * dt

        if self.player.dying:
            self.player.update(dt)
            self.camera.follow(self.player)
            self.particles.emit(self.player.rect.centerx, self.player.rect.centery, 2, (200, 150, 100))
            if self.player.death_timer <= 0:
                self.total_deaths = self.player.death_count
                go_menu = self.game.state_machine.states.get("game_over")
                if go_menu:
                    go_menu.deaths = self.total_deaths
                    go_menu.score = self.score
                self.game.change_state("game_over")
            return

        if not self.player.alive:
            self.total_deaths = self.player.death_count
            go_menu = self.game.state_machine.states.get("game_over")
            if go_menu:
                go_menu.deaths = self.total_deaths
                go_menu.score = self.score
            self.game.change_state("game_over")
            return

        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        self.physics.apply_gravity(self.player, dt)

        solid_tiles = self.tilemap.get_solid_tiles()
        self.physics.move_and_collide(self.player, solid_tiles, dt)
        self.player.update(dt)

        self.camera.follow(self.player)

        for enemy in self.enemies[:]:
            enemy.update(solid_tiles, self.player, dt)
            if not enemy.alive:
                self.enemies.remove(enemy)
                self.particles.emit(enemy.rect.centerx, enemy.rect.centery, 20, (200, 180, 140))

        for proj in self.projectiles[:]:
            proj.update(solid_tiles, dt)
            if not proj.alive:
                self.projectiles.remove(proj)

        for powerup in self.powerups[:]:
            powerup.update(dt)
            if powerup.alive and self.physics.check_collision(powerup, self.player):
                powerup.apply(self.player)
                self.powerups.remove(powerup)
                self.score += 50

        for enemy in self.enemies:
            if not enemy.alive:
                continue
            attack_rect = enemy.get_attack_rect()
            if attack_rect and self.physics.check_collision(self.player, enemy):
                if self.player.take_damage(enemy.damage):
                    self.screen_shake.shake(12, 20)
                    self.rage_flash = 15
                    self.particles.emit(self.player.rect.centerx, self.player.rect.centery, 25, (255, 50, 50))
                    self.rage_quote = self.player.death_quote
                    self.rage_quote_timer = DEATH_DELAY
                    return

            for proj in self.projectiles[:]:
                if proj.owner == "player" and proj.alive and self.physics.check_collision(proj, enemy):
                    enemy.take_damage(1)
                    proj.alive = False
                    self.particles.emit(enemy.rect.centerx, enemy.rect.centery, 10, (200, 180, 140))
                    if not enemy.alive:
                        self.score += 100

        for hazard in self.tilemap.get_hazard_tiles():
            if self.player.rect.colliderect(hazard.rect):
                if self.player.take_damage(1):
                    self.screen_shake.shake(15, 25)
                    self.rage_flash = 20
                    self.particles.emit(self.player.rect.centerx, self.player.rect.centery, 30, (255, 100, 50))
                    self.rage_quote = self.player.death_quote
                    self.rage_quote_timer = DEATH_DELAY
                    return

        if self.player.rect.x >= self.goal_x:
            self.next_level()

        self.particles.update(dt)
        self.screen_shake.update(dt)

    def next_level(self):
        self.total_deaths = self.player.death_count
        if self.level_index + 1 >= len(LEVELS):
            win_menu = self.game.state_machine.states.get("win")
            if win_menu:
                win_menu.deaths = self.total_deaths
                win_menu.score = self.score
            self.game.change_state("win")
        else:
            self.level_index += 1
            self.reset_level()

    def render(self, surface):
        surface.fill(SKY_BLUE)

        self.tilemap.draw(surface, self.camera, self.frame_counter)

        goal_rect = pygame.Rect(self.goal_x, 0, 32, self.tilemap.pixel_height)
        screen_goal = self.camera.apply(goal_rect)
        if screen_goal.right > 0 and screen_goal.left < WINDOW_WIDTH:
            pulse = abs(int(self.frame_counter * 0.1)) % 30
            pygame.draw.rect(surface, (255, 215 + pulse, 0), screen_goal)
            pygame.draw.rect(surface, (200, 170, 0), screen_goal, 2)

        for powerup in self.powerups:
            powerup.draw(surface, self.camera)

        for enemy in self.enemies:
            enemy.draw(surface, self.camera)

        self.player.draw(surface, self.camera)

        for proj in self.projectiles:
            proj.draw(surface, self.camera)

        self.particles.draw(surface, self.camera)

        shake = self.screen_shake.offset
        if shake != (0, 0):
            surface.scroll(shake[0], shake[1])

        if self.rage_flash > 0:
            flash_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            flash_alpha = int(min(self.rage_flash / 15, 1.0) * 80)
            flash_surface.fill((255, 0, 0, flash_alpha))
            surface.blit(flash_surface, (0, 0))

        level_display = f"{self.level_name.replace('_', ' ').title()} ({self.level_index+1}/{len(LEVELS)})"
        self.hud.render(surface, self.player, level_display, self.score, self.total_deaths)

        if self.rage_quote_timer > 0 and self.rage_quote:
            quote_font = pygame.font.Font(None, 48)
            alpha = min(self.rage_quote_timer / 30, 1.0)
            quote_text = quote_font.render(self.rage_quote, True, (255, 50, 50))
            quote_rect = quote_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3))
            surface.blit(quote_text, quote_rect)

            sub_font = pygame.font.Font(None, 24)
            death_text = sub_font.render(f"Deaths: {self.total_deaths}", True, (200, 200, 200))
            death_rect = death_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3 + 40))
            surface.blit(death_text, death_rect)


def main():
    game = Game()

    main_menu = MainMenu(game)
    playing = PlayingState(game)
    paused = PauseMenu(game)
    game_over = GameOverMenu(game)
    win = WinMenu(game)

    game.state_machine.add_state("main_menu", main_menu)
    game.state_machine.add_state("playing", playing)
    game.state_machine.add_state("paused", paused)
    game.state_machine.add_state("game_over", game_over)
    game.state_machine.add_state("win", win)

    game.change_state("main_menu")
    game.run()


if __name__ == "__main__":
    main()
