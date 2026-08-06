import pygame
import math
import sys
import os
import random

sys.path.insert(0, os.path.dirname(__file__))
from src.threed.settings import *

WIDTH, HEIGHT = 1024, 768
TILE = 32
GRAVITY = 0.6
JUMP = -12
SPEED = 4
FOV = 600


def project(x, y, z, cam_x, cam_y, cam_z, yaw, pitch):
    """Project 3D point to 2D screen. Returns (screen_x, screen_y, depth) or None."""
    dx = x - cam_x
    dy = y - cam_y
    dz = z - cam_z
    cy, sy = math.cos(yaw), math.sin(yaw)
    rx = dx * cy - dz * sy
    rz = dx * sy + dz * cy
    cp, sp = math.cos(pitch), math.sin(pitch)
    ry = dy * cp - rz * sp
    rz = dy * sp + rz * cp
    if rz < 0.3:
        return None
    sx = WIDTH / 2 + (rx / rz) * FOV
    sy = HEIGHT / 2 - (ry / rz) * FOV
    return (sx, sy, rz)


def draw_cube(surf, cx, cy, cz, sx, sy, sz, color, cam_x, cam_y, cam_z, yaw, pitch):
    """Draw a 3D cube. Returns average depth or None if behind camera."""
    corners = [
        (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5),
        (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5),
    ]
    proj = []
    for c in corners:
        p = project(cx + c[0] * sx, cy + c[1] * sy, cz + c[2] * sz,
                    cam_x, cam_y, cam_z, yaw, pitch)
        if p is None:
            return None
        proj.append(p)

    faces = [
        (0, 1, 2, 3, 0.0), (4, 5, 6, 7, -0.05), (1, 5, 6, 2, -0.15),
        (0, 4, 7, 3, -0.15), (3, 2, 6, 7, 0.15), (0, 1, 5, 4, -0.25),
    ]
    for i0, i1, i2, i3, shade in faces:
        pts = [proj[i0], proj[i1], proj[i2], proj[i3]]
        c = (max(0, min(1, color[0] + shade)), max(0, min(1, color[1] + shade)), max(0, min(1, color[2] + shade)))
        pygame.draw.polygon(surf, (int(c[0]*255), int(c[1]*255), int(c[2]*255)),
                           [(p[0], p[1]) for p in pts])
    return sum(p[2] for p in proj) / 8


class Game25D:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(f"Bread Army 2.5D - {VERSION}")
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 1.0
        self.frame = 0

        self.state = "menu"
        self.score = 0
        self.total_deaths = 0
        self.level_index = 0

        # Player (2D gameplay: x, y)
        self.px = 0
        self.py = 0
        self.vx = 0
        self.vy = 0
        self.p_health = 1
        self.p_max_health = 1
        self.p_alive = True
        self.p_dying = False
        self.p_death_timer = 0
        self.p_powerup = None
        self.p_attack_cd = 0
        self.p_grounded = False
        self.p_facing = 1
        self.p_depth = 0  # z position for rendering

        # Camera
        self.cam_yaw = 0.3  # slight angle for 2.5D look
        self.cam_pitch = -0.2
        self.cam_dist = 12

        # Level data
        self.tiles = []
        self.enemies = []
        self.powerups = []
        self.spikes = []
        self.goal = None
        self.cam_x = 0
        self.cam_y = 0

        # Visual
        self.rage_quote = ""
        self.rage_timer = 0
        self.cam_shake = 0

    def font(self, size=24):
        return pygame.font.Font(None, size)

    def text(self, txt, x, y, color=(255, 255, 255), size=24, center=False):
        f = self.font(size)
        s = f.render(txt, True, color)
        r = s.get_rect()
        if center:
            r.center = (x, y)
        else:
            r.topleft = (x, y)
        self.screen.blit(s, r)
        return r

    def hud(self):
        bar = pygame.Surface((WIDTH, 60), pygame.SRCALPHA)
        bar.fill((0, 0, 0, 120))
        self.screen.blit(bar, (0, 0))
        hearts = "♥" * self.p_health + "♡" * (self.p_max_health - self.p_health)
        self.text(hearts, 16, 10, (255, 50, 50), 28)
        if self.p_powerup:
            self.text(self.p_powerup.upper(), 16, 42, (255, 215, 0), 18)
        self.text(f"Score: {self.score}", WIDTH - 16, 10, (255, 255, 255), 22)
        self.text(f"Level {self.level_index + 1}/5", WIDTH - 16, 36, (180, 180, 180), 16)
        if self.total_deaths > 0:
            self.text(f"Deaths: {self.total_deaths}", WIDTH - 16, 56, (255, 100, 100), 16)
        if self.rage_timer > 0 and self.rage_quote:
            self.text(self.rage_quote, WIDTH // 2, HEIGHT // 2 - 60, (255, 50, 50), 32, center=True)

    def menu_screen(self):
        self.screen.fill((26, 15, 10))
        for y in range(0, HEIGHT, 4):
            r = y / HEIGHT
            pygame.draw.line(self.screen, (26 + r * 20, 15 + r * 10, 10 + r * 8), (0, y), (WIDTH, y))
        self.text("BREAD ARMY 2.5D", WIDTH // 2, 160, (255, 215, 0), 72, center=True)
        self.text("Prepare to suffer.", WIDTH // 2, 230, (150, 20, 20), 28, center=True)
        self.text("A/D - Move  |  Space - Jump  |  F - Attack", WIDTH // 2, 330, (180, 180, 180), 18, center=True)
        self.text("Press ENTER to start", WIDTH // 2, 420, (255, 255, 255), 32, center=True)
        self.text("Press ESC to quit", WIDTH // 2, 470, (128, 128, 128), 20, center=True)
        self.text(VERSION, WIDTH // 2, HEIGHT - 30, (100, 100, 100), 16, center=True)

    def game_over_screen(self):
        self.screen.fill((15, 0, 0))
        self.text("YOU DIED", WIDTH // 2, 180, (150, 20, 20), 72, center=True)
        if self.rage_quote:
            self.text(self.rage_quote, WIDTH // 2, 260, (255, 50, 50), 36, center=True)
        self.text(f"Score: {self.score}", WIDTH // 2, 340, (255, 215, 0), 32, center=True)
        self.text(f"Deaths: {self.total_deaths}", WIDTH // 2, 385, (255, 100, 100), 32, center=True)
        self.text("Press ENTER to retry", WIDTH // 2, 470, (255, 255, 255), 28, center=True)
        self.text("Press ESC for menu", WIDTH // 2, 515, (128, 128, 128), 20, center=True)

    def win_screen(self):
        self.screen.fill((5, 15, 5))
        self.text("YOU SURVIVED", WIDTH // 2, 180, (255, 215, 0), 72, center=True)
        self.text(f"Final Score: {self.score}", WIDTH // 2, 280, (255, 215, 0), 32, center=True)
        self.text(f"Deaths: {self.total_deaths}", WIDTH // 2, 325, (255, 100, 100), 32, center=True)
        if self.total_deaths == 0:
            c = "IMPOSSIBLE. You didn't die once?"
        elif self.total_deaths < 5:
            c = f"Not bad... only {self.total_deaths} deaths."
        elif self.total_deaths < 20:
            c = f"You suffered {self.total_deaths} times. Worth it?"
        else:
            c = f"{self.total_deaths} deaths. You are a masochist."
        self.text(c, WIDTH // 2, 380, (200, 200, 200), 24, center=True)
        self.text("Press ENTER to play again", WIDTH // 2, 470, (255, 255, 255), 28, center=True)
        self.text("Press ESC for menu", WIDTH // 2, 515, (128, 128, 128), 20, center=True)

    def load_level(self, idx):
        self.tiles.clear()
        self.enemies.clear()
        self.powerups.clear()
        self.spikes.clear()
        self.goal = None
        self.px = 64
        self.py = 0
        self.vx = 0
        self.vy = 0
        self.p_health = 1
        self.p_alive = True
        self.p_dying = False
        self.p_death_timer = 0
        self.p_powerup = None
        self.p_grounded = False
        self.rage_quote = ""
        self.rage_timer = 0

        levels = [self.l1, self.l2, self.l3, self.l4, self.l5]
        if idx < len(levels):
            levels[idx]()

    def add_tile(self, x, y, w=1, h=1, color=(0.5, 0.4, 0.3), spike=False):
        self.tiles.append({
            "x": x * TILE, "y": y * TILE, "w": w * TILE, "h": h * TILE,
            "color": color, "spike": spike
        })

    def add_enemy(self, etype, x, y, patrol=3):
        cfg = {
            "slime": {"color": (0.33, 0.42, 0.18), "scale": 0.8, "hp": 1, "speed": 1.5, "damage": 1},
            "crouton": {"color": (0.82, 0.41, 0.12), "scale": 0.7, "hp": 2, "speed": 2, "damage": 1},
            "cracker": {"color": (0.87, 0.72, 0.53), "scale": 0.6, "hp": 3, "speed": 2.5, "damage": 1},
            "golem": {"color": (0.55, 0.27, 0.07), "scale": 1.2, "hp": 5, "speed": 1, "damage": 2},
            "king": {"color": (0.5, 0.0, 0.13), "scale": 1.5, "hp": 10, "speed": 1.5, "damage": 3},
        }
        c = cfg[etype]
        self.enemies.append({
            "type": etype, "x": x * TILE, "y": y * TILE,
            "home_x": x * TILE, "patrol": patrol * TILE,
            "color": c["color"], "scale": c["scale"], "hp": c["hp"],
            "speed": c["speed"], "damage": c["damage"],
            "alive": True, "dir": 1, "atk_timer": 0, "flash": 0,
        })

    def add_powerup(self, ptype, x, y):
        cfg = {
            "toast": (0.71, 0.47, 0.24), "croissant": (0.86, 0.75, 0.55),
            "bagel": (0.78, 0.63, 0.39), "sourdough": (0.63, 0.55, 0.39),
        }
        self.powerups.append({
            "type": ptype, "x": x * TILE, "y": y * TILE,
            "color": cfg[ptype], "alive": True, "bob": random.random() * 6.28,
        })

    def l1(self):
        # Ground
        for i in range(20):
            self.add_tile(i, 14, 1, 1, (0.55, 0.45, 0.33))
        # Platforms
        self.add_tile(5, 11, 3, 1, (0.5, 0.5, 0.5))
        self.add_tile(10, 9, 3, 1, (0.5, 0.5, 0.5))
        self.add_tile(15, 11, 3, 1, (0.5, 0.5, 0.5))
        # Spikes
        self.add_tile(8, 13, 1, 1, (0.8, 0.1, 0.1), spike=True)
        # Enemies
        self.add_enemy("slime", 6, 10, 2)
        self.add_enemy("slime", 12, 8, 2)
        self.add_enemy("crouton", 16, 10, 3)
        # Powerups
        self.add_powerup("toast", 6, 9)
        self.add_powerup("croissant", 11, 7)
        # Goal
        self.goal = (18 * TILE, 13 * TILE)

    def l2(self):
        for i in range(25):
            self.add_tile(i, 14, 1, 1, (0.55, 0.45, 0.33))
        self.add_tile(4, 11, 2, 1, (0.5, 0.5, 0.5))
        self.add_tile(8, 9, 2, 1, (0.5, 0.5, 0.5))
        self.add_tile(12, 7, 2, 1, (0.5, 0.5, 0.5))
        self.add_tile(16, 9, 2, 1, (0.5, 0.5, 0.5))
        self.add_tile(20, 11, 3, 1, (0.5, 0.5, 0.5))
        self.add_tile(6, 13, 1, 1, (0.8, 0.1, 0.1), spike=True)
        self.add_tile(10, 13, 1, 1, (0.8, 0.1, 0.1), spike=True)
        self.add_tile(14, 13, 1, 1, (0.8, 0.1, 0.1), spike=True)
        self.add_enemy("slime", 5, 10, 2)
        self.add_enemy("crouton", 9, 8, 2)
        self.add_enemy("cracker", 17, 8, 3)
        self.add_enemy("slime", 21, 10, 2)
        self.add_powerup("toast", 12, 5)
        self.goal = (23 * TILE, 13 * TILE)

    def l3(self):
        for i in range(30):
            self.add_tile(i, 14, 1, 1, (0.55, 0.45, 0.33))
        self.add_tile(5, 11, 2, 1, (0.68, 0.85, 0.9))
        self.add_tile(9, 9, 2, 1, (0.68, 0.85, 0.9))
        self.add_tile(13, 7, 2, 1, (0.68, 0.85, 0.9))
        self.add_tile(17, 9, 2, 1, (0.68, 0.85, 0.9))
        self.add_tile(21, 11, 2, 1, (0.68, 0.85, 0.9))
        self.add_tile(25, 9, 3, 1, (0.5, 0.5, 0.5))
        self.add_tile(7, 13, 1, 1, (0.8, 0.1, 0.1), spike=True)
        self.add_tile(11, 13, 1, 1, (0.8, 0.1, 0.1), spike=True)
        self.add_tile(15, 13, 1, 1, (0.8, 0.1, 0.1), spike=True)
        self.add_enemy("slime", 6, 10, 2)
        self.add_enemy("crouton", 10, 8, 2)
        self.add_enemy("cracker", 18, 8, 2)
        self.add_enemy("golem", 26, 8, 4)
        self.add_powerup("bagel", 13, 5)
        self.goal = (28 * TILE, 13 * TILE)

    def l4(self):
        for i in range(35):
            self.add_tile(i, 14, 1, 1, (0.55, 0.45, 0.33))
        self.add_tile(5, 11, 2, 1, (0.7, 0.13, 0.13))
        self.add_tile(9, 9, 2, 1, (0.7, 0.13, 0.13))
        self.add_tile(13, 7, 2, 1, (0.7, 0.13, 0.13))
        self.add_tile(17, 9, 2, 1, (0.7, 0.13, 0.13))
        self.add_tile(21, 7, 2, 1, (0.7, 0.13, 0.13))
        self.add_tile(25, 9, 2, 1, (0.7, 0.13, 0.13))
        self.add_tile(29, 11, 3, 1, (0.7, 0.13, 0.13))
        self.add_tile(8, 13, 1, 1, (0.8, 0.1, 0.1), spike=True)
        self.add_tile(12, 13, 1, 1, (0.8, 0.1, 0.1), spike=True)
        self.add_tile(16, 13, 1, 1, (0.8, 0.1, 0.1), spike=True)
        self.add_tile(20, 13, 1, 1, (0.8, 0.1, 0.1), spike=True)
        self.add_tile(24, 13, 1, 1, (0.8, 0.1, 0.1), spike=True)
        self.add_enemy("slime", 6, 10, 2)
        self.add_enemy("crouton", 10, 8, 2)
        self.add_enemy("cracker", 18, 8, 2)
        self.add_enemy("golem", 22, 6, 3)
        self.add_enemy("slime", 30, 10, 2)
        self.add_powerup("sourdough", 21, 5)
        self.goal = (32 * TILE, 13 * TILE)

    def l5(self):
        for i in range(40):
            self.add_tile(i, 14, 1, 1, (0.55, 0.45, 0.33))
        self.add_tile(5, 11, 2, 1, (0.5, 0.5, 0.5))
        self.add_tile(9, 9, 2, 1, (0.5, 0.5, 0.5))
        self.add_tile(13, 7, 2, 1, (0.5, 0.5, 0.5))
        self.add_tile(17, 9, 2, 1, (0.5, 0.5, 0.5))
        self.add_tile(21, 7, 2, 1, (0.5, 0.5, 0.5))
        self.add_tile(25, 9, 2, 1, (0.5, 0.5, 0.5))
        self.add_tile(29, 7, 2, 1, (0.5, 0.5, 0.5))
        self.add_tile(33, 9, 3, 1, (0.5, 0.5, 0.5))
        self.add_tile(8, 13, 1, 1, (0.8, 0.1, 0.1), spike=True)
        self.add_tile(12, 13, 1, 1, (0.8, 0.1, 0.1), spike=True)
        self.add_tile(16, 13, 1, 1, (0.8, 0.1, 0.1), spike=True)
        self.add_tile(20, 13, 1, 1, (0.8, 0.1, 0.1), spike=True)
        self.add_tile(24, 13, 1, 1, (0.8, 0.1, 0.1), spike=True)
        self.add_tile(28, 13, 1, 1, (0.8, 0.1, 0.1), spike=True)
        self.add_enemy("slime", 6, 10, 2)
        self.add_enemy("crouton", 10, 8, 2)
        self.add_enemy("cracker", 18, 8, 2)
        self.add_enemy("golem", 22, 6, 3)
        self.add_enemy("slime", 30, 6, 2)
        self.add_enemy("king", 34, 8, 5)
        self.add_powerup("toast", 13, 5)
        self.add_powerup("bagel", 25, 7)
        self.add_powerup("sourdough", 29, 5)
        self.goal = (37 * TILE, 13 * TILE)

    def run(self):
        while self.running:
            self.dt = min(self.clock.tick(60) / 16.667, 3.0)
            self.frame += 1
            self.handle_events()
            self.update()
            self.render()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state in ("game_over", "win"):
                        self.state = "menu"
                    elif self.state == "playing":
                        self.state = "menu"
                    elif self.state == "menu":
                        self.running = False
                elif event.key == pygame.K_RETURN:
                    if self.state == "menu":
                        self.score = 0
                        self.total_deaths = 0
                        self.level_index = 0
                        self.load_level(0)
                        self.state = "playing"
                    elif self.state == "game_over":
                        self.total_deaths += 1
                        self.load_level(self.level_index)
                        self.state = "playing"
                    elif self.state == "win":
                        self.score = 0
                        self.total_deaths = 0
                        self.level_index = 0
                        self.load_level(0)
                        self.state = "playing"
                elif event.key == pygame.K_f and self.state == "playing":
                    self.try_attack()

    def try_attack(self):
        if self.p_attack_cd > 0 or self.p_dying:
            return
        self.p_attack_cd = 20
        self.cam_shake = 5
        attack_x = self.px + self.p_facing * TILE
        for e in self.enemies:
            if not e["alive"]:
                continue
            if abs(e["x"] - attack_x) < TILE * 1.5 and abs(e["y"] - self.py) < TILE:
                e["hp"] -= 1
                e["flash"] = 5
                if e["hp"] <= 0:
                    e["alive"] = False
                    self.score += 100

    def update(self):
        if self.state != "playing":
            return

        dt = self.dt
        keys = pygame.key.get_pressed()

        # Horizontal movement
        self.vx = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vx = -SPEED
            self.p_facing = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vx = SPEED
            self.p_facing = 1

        # Apply horizontal movement with collision
        new_x = self.px + self.vx * dt
        if not self.tile_collision(new_x, self.py, TILE//2, TILE//2):
            self.px = new_x

        # Gravity
        self.vy += GRAVITY * dt
        self.vy = min(self.vy, 15)
        new_y = self.py + self.vy * dt

        # Vertical collision
        if self.vy > 0:
            # Falling
            if self.tile_collision(self.px, new_y, TILE//2, TILE//2):
                # Land on top of tile
                tile_top = self.get_tile_top(self.px, new_y, TILE//2, TILE//2)
                if tile_top is not None:
                    self.py = tile_top - TILE//2
                    self.vy = 0
                    self.p_grounded = True
                else:
                    self.py = new_y
                    self.p_grounded = False
            else:
                self.py = new_y
                self.p_grounded = False
        elif self.vy < 0:
            # Jumping up
            if self.tile_collision(self.px, new_y, TILE//2, TILE//2):
                self.vy = 0
            else:
                self.py = new_y
        else:
            # Check if still grounded
            if self.tile_collision(self.px, self.py + 1, TILE//2, TILE//2):
                self.p_grounded = True
            else:
                self.p_grounded = False

        # Jump
        if keys[pygame.K_SPACE] and self.p_grounded:
            self.vy = JUMP
            self.p_grounded = False

        # Attack cooldown
        if self.p_attack_cd > 0:
            self.p_attack_cd -= 1

        # Death timer
        if self.p_dying:
            self.p_death_timer -= 1
            if self.p_death_timer <= 0:
                self.total_deaths += 1
                self.state = "game_over"
            return

        # Rage timer
        if self.rage_timer > 0:
            self.rage_timer -= 1
        if self.cam_shake > 0:
            self.cam_shake -= 1

        # Spikes
        for t in self.tiles:
            if t["spike"]:
                if abs(self.px - t["x"]) < TILE * 0.8 and abs(self.py - t["y"]) < TILE * 0.8:
                    self.die()

        # Enemies
        for e in self.enemies:
            if not e["alive"]:
                continue
            e["x"] += e["dir"] * e["speed"] * dt
            if abs(e["x"] - e["home_x"]) > e["patrol"]:
                e["dir"] *= -1
            if e["flash"] > 0:
                e["flash"] -= 1
            e["atk_timer"] += 1
            if e["atk_timer"] >= 60:
                if abs(e["x"] - self.px) < TILE * 1.2 and abs(e["y"] - self.py) < TILE:
                    e["atk_timer"] = 0
                    self.take_damage(e["damage"])

        # Powerups
        for pu in self.powerups:
            if not pu["alive"]:
                continue
            pu["bob"] += dt * 2
            if abs(pu["x"] - self.px) < TILE and abs(pu["y"] - self.py) < TILE:
                pu["alive"] = False
                self.p_powerup = pu["type"]
                self.score += 50
                if pu["type"] == "toast":
                    self.p_health = min(self.p_health + 1, self.p_max_health)

        # Goal
        if self.goal:
            if abs(self.px - self.goal[0]) < TILE and abs(self.py - self.goal[1]) < TILE:
                self.level_index += 1
                if self.level_index >= 5:
                    self.state = "win"
                else:
                    self.load_level(self.level_index)

        # Fall death
        if self.py > TILE * 20:
            self.die()

    def die(self):
        if self.p_dying:
            return
        self.p_dying = True
        self.p_death_timer = 90
        self.rage_quote = random.choice(RAGE_QUOTES)
        self.rage_timer = 90

    def take_damage(self, dmg):
        if self.p_dying:
            return
        self.p_health -= dmg
        if self.p_health <= 0:
            self.die()

    def tile_collision(self, x, y, hw, hh):
        """Check if a box at (x,y) with half-width hw and half-height hh collides with any solid tile."""
        for t in self.tiles:
            if t["spike"]:
                continue
            if (x + hw > t["x"] and x - hw < t["x"] + t["w"] and
                y + hh > t["y"] and y - hh < t["y"] + t["h"]):
                return True
        return False

    def get_tile_top(self, x, y, hw, hh):
        """Get the top surface y of the highest tile that the box would collide with when falling."""
        best = None
        for t in self.tiles:
            if t["spike"]:
                continue
            if (x + hw > t["x"] and x - hw < t["x"] + t["w"] and
                y + hh > t["y"] and y - hh < t["y"] + t["h"]):
                if best is None or t["y"] < best:
                    best = t["y"]
        return best

    def render(self):
        self.screen.fill((26, 15, 10))

        if self.state == "menu":
            self.menu_screen()
            pygame.display.flip()
            return
        elif self.state == "game_over":
            self.game_over_screen()
            pygame.display.flip()
            return
        elif self.state == "win":
            self.win_screen()
            pygame.display.flip()
            return

        # Camera follows player
        self.cam_x = self.px
        self.cam_y = self.py - 64

        # Camera shake
        shake_x = random.uniform(-3, 3) if self.cam_shake > 0 else 0
        shake_y = random.uniform(-2, 2) if self.cam_shake > 0 else 0

        cam_x = self.cam_x + shake_x
        cam_y = self.cam_y + shake_y
        cam_z = self.p_depth - self.cam_dist

        # Collect drawables
        draw_queue = []

        # Player
        p_color = (0.82, 0.71, 0.55)
        if self.p_powerup:
            pc = {"toast": (0.71, 0.47, 0.24), "croissant": (0.86, 0.75, 0.55),
                  "bagel": (0.78, 0.63, 0.39), "sourdough": (0.63, 0.55, 0.39)}
            p_color = pc.get(self.p_powerup, p_color)
        if self.p_dying:
            p_color = (1, 0.4, 0.4)
        draw_queue.append((self.px, self.py - TILE//2, self.p_depth + 1, 0.6, 1.0, 0.6, p_color))
        draw_queue.append((self.px, self.py - TILE, self.p_depth + 1, 0.8, 0.25, 0.8, (0.2, 0.2, 0.6)))

        # Goal
        if self.goal:
            bob = math.sin(self.frame * 0.05) * 8
            draw_queue.append((self.goal[0], self.goal[1] + bob, self.p_depth, 1, 0.3, 1, (1, 0.84, 0)))

        # Tiles
        for t in self.tiles:
            color = (0.8, 0.1, 0.1) if t["spike"] else t["color"]
            draw_queue.append((t["x"] + t["w"]/2, t["y"] + t["h"]/2, self.p_depth,
                              t["w"] / TILE, t["h"] / TILE, 1, color))

        # Enemies
        for e in self.enemies:
            if e["alive"]:
                sc = e["scale"]
                color = (1, 0.3, 0.3) if e["flash"] > 0 else e["color"]
                draw_queue.append((e["x"], e["y"], self.p_depth, sc, sc, sc, color))

        # Powerups
        for pu in self.powerups:
            if pu["alive"]:
                s = 0.35 + math.sin(pu["bob"]) * 0.05
                draw_queue.append((pu["x"], pu["y"], self.p_depth, s, s, s, pu["color"]))

        # Depth sort
        def depth_key(item):
            x, y, z = item[0], item[1], item[2]
            dx = x - cam_x
            dy = y - cam_y
            dz = z - cam_z
            cy, sy = math.cos(self.cam_yaw), math.sin(self.cam_yaw)
            rz = dx * sy + dz * cy
            return -rz

        draw_queue.sort(key=depth_key)

        # Render
        for item in draw_queue:
            x, y, z, sx, sy, sz, color = item
            draw_cube(self.screen, x, y, z, sx * TILE, sy * TILE, sz * TILE,
                      color, cam_x, cam_y, cam_z, self.cam_yaw, self.cam_pitch)

        self.hud()
        pygame.display.flip()


if __name__ == "__main__":
    g = Game25D()
    g.run()
    pygame.quit()
    sys.exit()
