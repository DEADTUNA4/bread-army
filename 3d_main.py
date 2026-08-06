import pygame
import math
import sys
import os
import random

sys.path.insert(0, os.path.dirname(__file__))
from src.threed.settings import *

WIDTH, HEIGHT = 1024, 768
CAM_DIST = 8
CAM_HEIGHT = 4
FOV = 600
NEAR = 0.3


def project_point(dx, dy, dz, yaw, pitch):
    """Project a point relative to camera. Returns (screen_x, screen_y, depth) or None if behind camera."""
    cos_y, sin_y = math.cos(yaw), math.sin(yaw)
    rx = dx * cos_y - dz * sin_y
    rz = dx * sin_y + dz * cos_y
    cos_p, sin_p = math.cos(pitch), math.sin(pitch)
    ry = dy * cos_p - rz * sin_p
    rz = dy * sin_p + rz * cos_p
    if rz < NEAR:
        return None
    sx = WIDTH / 2 + (rx / rz) * FOV
    sy = HEIGHT / 2 - (ry / rz) * FOV
    return (sx, sy, rz)


def project_cube(cx, cy, cz, sx, sy, sz, cam_pos, yaw, pitch):
    """Project all 8 corners of a cube. Returns list of 8 projected points or None if any behind camera."""
    dx = cx - cam_pos[0]
    dy = cy - cam_pos[1]
    dz = cz - cam_pos[2]
    corners = [
        (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5),
        (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5),
    ]
    proj = []
    for c in corners:
        p = project_point(
            dx + c[0] * sx, dy + c[1] * sy, dz + c[2] * sz,
            yaw, pitch
        )
        if p is None:
            return None
        proj.append(p)
    return proj


def draw_cube_faces(surf, proj, color):
    """Draw 6 faces of a cube given 8 projected corners. Returns average depth."""
    faces = [
        (0, 1, 2, 3, 0.0),   # south
        (4, 5, 6, 7, -0.05), # north
        (1, 5, 6, 2, -0.15), # east
        (0, 4, 7, 3, -0.15), # west
        (3, 2, 6, 7, 0.15),  # top
        (0, 1, 5, 4, -0.25), # bottom
    ]
    for i0, i1, i2, i3, shade in faces:
        pts = [proj[i0], proj[i1], proj[i2], proj[i3]]
        c = (
            max(0, min(1, color[0] + shade)),
            max(0, min(1, color[1] + shade)),
            max(0, min(1, color[2] + shade)),
        )
        pygame.draw.polygon(surf, (int(c[0]*255), int(c[1]*255), int(c[2]*255)),
                           [(p[0], p[1]) for p in pts])
    return sum(p[2] for p in proj) / 8


class Game3D:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(f"Bread Army 3D - {VERSION}")
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 1.0

        self.state = "menu"
        self.px, self.py, self.pz = 0, 1, 0
        self.p_vy = 0
        self.p_health = 1
        self.p_max_health = 1
        self.p_alive = True
        self.p_dying = False
        self.p_death_timer = 0
        self.p_powerup = None
        self.p_attack_cooldown = 0
        self.p_grounded = False
        self.p_facing = 0
        self.yaw = 0
        self.pitch = -0.3
        self.score = 0
        self.total_deaths = 0
        self.level_index = 0
        self.goal_pos = None
        self.platforms = []
        self.enemies = []
        self.powerups = []
        self.rage_quote = ""
        self.rage_timer = 0
        self.frame_count = 0
        self.cam_shake = 0

    def font(self, size=24):
        return pygame.font.Font(None, size)

    def text(self, text, x, y, color=(255, 255, 255), size=24, center=False):
        f = self.font(size)
        s = f.render(text, True, color)
        r = s.get_rect()
        if center:
            r.center = (x, y)
        else:
            r.topleft = (x, y)
        self.screen.blit(s, r)
        return r

    def hud(self):
        # Background bar
        bar = pygame.Surface((WIDTH, 70), pygame.SRCALPHA)
        bar.fill((0, 0, 0, 120))
        self.screen.blit(bar, (0, 0))

        hearts = "♥" * self.p_health + "♡" * (self.p_max_health - self.p_health)
        self.text(hearts, 20, 12, (255, 50, 50), 32)
        if self.p_powerup:
            self.text(f"Power: {self.p_powerup.upper()}", 20, 48, (255, 215, 0), 20)

        score_surf = self.font(24).render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_surf, (WIDTH - score_surf.get_width() - 20, 12))

        level_surf = self.font(20).render(f"Level {self.level_index + 1}/5", True, (180, 180, 180))
        self.screen.blit(level_surf, (WIDTH - level_surf.get_width() - 20, 42))

        if self.total_deaths > 0:
            death_surf = self.font(20).render(f"Deaths: {self.total_deaths}", True, (255, 120, 120))
            self.screen.blit(death_surf, (WIDTH - death_surf.get_width() - 20, 62))

        # Crosshair
        cx, cy = WIDTH // 2, HEIGHT // 2
        pygame.draw.line(self.screen, (255, 255, 255), (cx - 10, cy), (cx + 10, cy), 1)
        pygame.draw.line(self.screen, (255, 255, 255), (cx, cy - 10), (cx, cy + 10), 1)

        # Rage quote
        if self.rage_timer > 0 and self.rage_quote:
            self.text(self.rage_quote, WIDTH // 2, HEIGHT // 2 - 80, (255, 50, 50), 36, center=True)

    def menu_screen(self):
        self.screen.fill((26, 15, 10))
        for y in range(0, HEIGHT, 4):
            ratio = y / HEIGHT
            pygame.draw.line(self.screen, (26 + ratio * 20, 15 + ratio * 10, 10 + ratio * 8), (0, y), (WIDTH, y))

        self.text("BREAD ARMY 3D", WIDTH // 2, 160, (255, 215, 0), 80, center=True)
        self.text("Prepare to suffer.", WIDTH // 2, 230, (150, 20, 20), 28, center=True)
        self.text("WASD - Move  |  Mouse - Look  |  Space - Jump  |  Click - Attack", WIDTH // 2, 330, (180, 180, 180), 18, center=True)
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
            comment = "IMPOSSIBLE. You didn't die once?"
        elif self.total_deaths < 5:
            comment = f"Not bad... only {self.total_deaths} deaths."
        elif self.total_deaths < 20:
            comment = f"You suffered {self.total_deaths} times. Worth it?"
        else:
            comment = f"{self.total_deaths} deaths. You are a masochist."
        self.text(comment, WIDTH // 2, 380, (200, 200, 200), 24, center=True)
        self.text("Press ENTER to play again", WIDTH // 2, 470, (255, 255, 255), 28, center=True)
        self.text("Press ESC for menu", WIDTH // 2, 515, (128, 128, 128), 20, center=True)

    def load_level(self, idx):
        self.platforms.clear()
        self.enemies.clear()
        self.powerups.clear()
        self.px, self.py, self.pz = 0, 1, 0
        self.p_vy = 0
        self.p_health = 1
        self.p_alive = True
        self.p_dying = False
        self.p_death_timer = 0
        self.p_attack_cooldown = 0
        self.p_grounded = False
        self.p_powerup = None
        self.rage_quote = ""
        self.rage_timer = 0
        self.goal_pos = None
        self.cam_shake = 0

        levels = [self.l1, self.l2, self.l3, self.l4, self.l5]
        if idx < len(levels):
            levels[idx]()

    def plat(self, x, y, z, sx, sy, sz, color):
        self.platforms.append({"pos": (x, y, z), "scale": (sx, sy, sz), "color": color})

    def enemy(self, etype, x, z, patrol=4):
        cfg = {
            "slime": {"color": (0.33, 0.42, 0.18), "scale": 0.8, "hp": 1, "speed": 2, "damage": 1},
            "crouton": {"color": (0.82, 0.41, 0.12), "scale": 0.7, "hp": 2, "speed": 2.5, "damage": 1},
            "cracker": {"color": (0.87, 0.72, 0.53), "scale": (0.6, 0.2, 0.8), "hp": 3, "speed": 3, "damage": 1},
            "golem": {"color": (0.55, 0.27, 0.07), "scale": (1.2, 1.5, 1.2), "hp": 5, "speed": 1.5, "damage": 2},
            "fly": {"color": (0.29, 0.29, 0.29), "scale": 0.5, "hp": 1, "speed": 4, "damage": 1},
            "king": {"color": (0.5, 0.0, 0.13), "scale": (1.5, 2, 1.5), "hp": 10, "speed": 2, "damage": 3},
        }
        c = cfg[etype]
        sc = c["scale"]
        sc_list = [sc, sc, sc] if isinstance(sc, (int, float)) else list(sc)
        self.enemies.append({
            "pos": [x, sc_list[1] * 0.5, z], "home_x": x, "home_z": z,
            "scale": sc_list, "color": c["color"], "hp": c["hp"],
            "speed": c["speed"], "damage": c["damage"],
            "alive": True, "dir": 1, "attack_timer": 0, "patrol": patrol,
        })

    def powerup(self, ptype, x, y, z):
        cfg = {
            "toast": (0.71, 0.47, 0.24), "croissant": (0.86, 0.75, 0.55),
            "bagel": (0.78, 0.63, 0.39), "sourdough": (0.63, 0.55, 0.39),
        }
        self.powerups.append({
            "type": ptype, "pos": [x, y, z], "color": cfg[ptype],
            "alive": True, "bob": random.random() * 6.28, "base_y": y,
        })

    def l1(self):
        self.px, self.pz = 0, 8
        self.goal_pos = (0, 1, -16)
        self.plat(0, -1, 0, 8, 1, 24, (0.55, 0.45, 0.33))
        self.plat(0, 0, -8, 4, 1, 4, (0.5, 0.5, 0.5))
        self.plat(0, 1, -16, 3, 1, 3, (0.5, 0.5, 0.5))
        self.enemy("slime", -2, -2)
        self.enemy("slime", 2, -4)
        self.enemy("crouton", 0, -10)
        self.powerup("toast", 0, 1.5, -6)
        self.powerup("croissant", 0, 2.5, -16)

    def l2(self):
        self.px, self.pz = 0, 10
        self.goal_pos = (0, 1, -20)
        self.plat(0, -1, 0, 10, 1, 30, (0.55, 0.45, 0.33))
        self.plat(-4, 1, -8, 3, 1, 3, (0.5, 0.5, 0.5))
        self.plat(4, 2, -12, 3, 1, 3, (0.5, 0.5, 0.5))
        self.plat(-2, 3, -16, 3, 1, 3, (0.5, 0.5, 0.5))
        self.plat(0, 4, -20, 3, 1, 3, (0.5, 0.5, 0.5))
        self.enemy("slime", 0, -2)
        self.enemy("crouton", -3, -10)
        self.enemy("cracker", 3, -14)
        self.enemy("slime", 0, -18)
        self.powerup("toast", -4, 2.5, -8)

    def l3(self):
        self.px, self.pz = 0, 12
        self.goal_pos = (0, 1, -24)
        self.plat(0, -1, 0, 12, 1, 36, (0.55, 0.45, 0.33))
        self.plat(-4, 1, -8, 3, 1, 3, (0.68, 0.85, 0.9))
        self.plat(4, 2, -14, 3, 1, 3, (0.68, 0.85, 0.9))
        self.plat(-4, 3, -20, 3, 1, 3, (0.68, 0.85, 0.9))
        self.plat(0, 4, -24, 3, 1, 3, (0.68, 0.85, 0.9))
        self.enemy("slime", 0, -2)
        self.enemy("crouton", -3, -10)
        self.enemy("cracker", 3, -16)
        self.enemy("golem", 0, -22)
        self.powerup("bagel", 4, 3.5, -14)

    def l4(self):
        self.px, self.pz = 0, 14
        self.goal_pos = (0, 1, -28)
        self.plat(0, -1, 0, 14, 1, 42, (0.55, 0.45, 0.33))
        self.plat(-5, 1, -8, 3, 1, 3, (0.7, 0.13, 0.13))
        self.plat(5, 2, -14, 3, 1, 3, (0.7, 0.13, 0.13))
        self.plat(-5, 3, -20, 3, 1, 3, (0.7, 0.13, 0.13))
        self.plat(5, 4, -26, 3, 1, 3, (0.7, 0.13, 0.13))
        self.plat(0, 5, -28, 3, 1, 3, (0.7, 0.13, 0.13))
        self.enemy("slime", 0, -2)
        self.enemy("crouton", -4, -10)
        self.enemy("cracker", 4, -16)
        self.enemy("golem", -4, -22)
        self.enemy("fly", 0, -26)
        self.powerup("sourdough", -5, 4.5, -20)

    def l5(self):
        self.px, self.pz = 0, 16
        self.goal_pos = (0, 1, -32)
        self.plat(0, -1, 0, 16, 1, 48, (0.55, 0.45, 0.33))
        self.plat(-5, 1, -8, 3, 1, 3, (0.5, 0.5, 0.5))
        self.plat(5, 2, -14, 3, 1, 3, (0.5, 0.5, 0.5))
        self.plat(-5, 3, -20, 3, 1, 3, (0.5, 0.5, 0.5))
        self.plat(5, 4, -26, 3, 1, 3, (0.5, 0.5, 0.5))
        self.plat(-5, 5, -30, 3, 1, 3, (0.5, 0.5, 0.5))
        self.plat(0, 6, -32, 4, 1, 4, (0.5, 0.5, 0.5))
        self.enemy("slime", 0, -2)
        self.enemy("crouton", -4, -10)
        self.enemy("cracker", 4, -16)
        self.enemy("golem", -4, -22)
        self.enemy("fly", 4, -28)
        self.enemy("king", 0, -32)
        self.powerup("toast", -5, 2.5, -8)
        self.powerup("bagel", 5, 5.5, -26)
        self.powerup("sourdough", -5, 6.5, -30)

    def get_ground(self, x, z):
        highest = -999
        for p in self.platforms:
            pp = p["pos"]
            ps = p["scale"]
            if (x + 0.4 > pp[0] - ps[0] / 2 and x - 0.4 < pp[0] + ps[0] / 2 and
                z + 0.4 > pp[2] - ps[2] / 2 and z - 0.4 < pp[2] + ps[2] / 2):
                top = pp[1] + ps[1] / 2
                if top > highest:
                    highest = top
        return highest

    def collides(self, x, y, z, r=0.4):
        for p in self.platforms:
            pp = p["pos"]
            ps = p["scale"]
            if (x + r > pp[0] - ps[0] / 2 and x - r < pp[0] + ps[0] / 2 and
                z + r > pp[2] - ps[2] / 2 and z - r < pp[2] + ps[2] / 2 and
                y - r < pp[1] + ps[1] / 2 and y + r > pp[1] - ps[1] / 2):
                return True
        return False

    def run(self):
        while self.running:
            self.dt = min(self.clock.tick(60) / 16.667, 3.0)
            self.frame_count += 1
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
                        pygame.mouse.set_visible(True)
                    elif self.state == "menu":
                        self.running = False
                elif event.key == pygame.K_RETURN:
                    if self.state == "menu":
                        self.score = 0
                        self.total_deaths = 0
                        self.level_index = 0
                        self.load_level(0)
                        self.state = "playing"
                        pygame.mouse.set_visible(False)
                    elif self.state == "game_over":
                        self.total_deaths += 1
                        self.load_level(self.level_index)
                        self.state = "playing"
                        pygame.mouse.set_visible(False)
                    elif self.state == "win":
                        self.score = 0
                        self.total_deaths = 0
                        self.level_index = 0
                        self.load_level(0)
                        self.state = "playing"
                        pygame.mouse.set_visible(False)
            elif event.type == pygame.MOUSEMOTION and self.state == "playing":
                self.yaw += event.rel[0] * 0.003
                self.pitch = max(-1.2, min(1.2, self.pitch + event.rel[1] * 0.003))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and self.state == "playing":
                    self.try_attack()

    def try_attack(self):
        if self.p_attack_cooldown > 0 or self.p_dying:
            return
        self.p_attack_cooldown = 20
        self.cam_shake = 5
        # Hit enemies in front of player within range
        fx = math.sin(self.yaw)
        fz = math.cos(self.yaw)
        for e in self.enemies:
            if not e["alive"]:
                continue
            dx = e["pos"][0] - self.px
            dz = e["pos"][2] - self.pz
            dist = math.hypot(dx, dz)
            if dist < 4:
                # Check if enemy is in front (dot product with forward)
                dot = (dx * fx + dz * fz) / max(dist, 0.01)
                if dot > 0.3:  # within ~70 degrees of forward
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

        # Camera-relative movement
        forward_x = math.sin(self.yaw)
        forward_z = math.cos(self.yaw)
        right_x = math.cos(self.yaw)
        right_z = -math.sin(self.yaw)

        mx, mz = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            mx += forward_x
            mz += forward_z
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            mx -= forward_x
            mz -= forward_z
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            mx -= right_x
            mz -= right_z
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            mx += right_x
            mz += right_z

        if mx != 0 or mz != 0:
            length = math.hypot(mx, mz)
            mx /= length
            mz /= length
            speed = 5 * dt
            nx = self.px + mx * speed
            nz = self.pz + mz * speed
            if not self.collides(nx, self.py, nz):
                self.px, self.pz = nx, nz
            else:
                if not self.collides(nx, self.py, self.pz):
                    self.px = nx
                elif not self.collides(self.px, self.py, nz):
                    self.pz = nz
            self.p_facing = math.atan2(mx, mz)

        # Ground check
        gnd = self.get_ground(self.px, self.pz)
        feet_y = self.py - 0.5
        if gnd > -999 and feet_y <= gnd + 0.1 and self.p_vy <= 0:
            self.p_grounded = True
            self.py = gnd + 0.5
            self.p_vy = 0
        else:
            self.p_grounded = False

        if keys[pygame.K_SPACE] and self.p_grounded:
            self.p_vy = 10
            self.p_grounded = False

        # Apply gravity with capped fall speed to prevent tunneling
        self.p_vy -= 30 * dt
        self.p_vy = max(self.p_vy, -15)
        self.py += self.p_vy * dt

        # Anti-tunneling: snap to ground if we passed through it
        gnd = self.get_ground(self.px, self.pz)
        if gnd > -999 and self.py - 0.5 <= gnd and self.p_vy <= 0:
            self.py = gnd + 0.5
            self.p_vy = 0
            self.p_grounded = True

        if self.py < -20 and not self.p_dying:
            self.start_death()

        if self.p_attack_cooldown > 0:
            self.p_attack_cooldown -= 1

        if self.p_dying:
            self.p_death_timer -= 1
            self.p_vy -= 20 * dt
            self.py += self.p_vy * dt
            if self.p_death_timer <= 0:
                self.confirm_death()

        if self.rage_timer > 0:
            self.rage_timer -= 1

        if self.cam_shake > 0:
            self.cam_shake -= 1

        # Enemies
        for e in self.enemies:
            if not e["alive"]:
                continue
            e["pos"][0] += e["dir"] * e["speed"] * dt
            if abs(e["pos"][0] - e["home_x"]) > e["patrol"]:
                e["dir"] *= -1
            e["attack_timer"] += 1
            if e.get("flash", 0) > 0:
                e["flash"] -= 1
            if e["attack_timer"] >= 60:
                dx = e["pos"][0] - self.px
                dz = e["pos"][2] - self.pz
                if math.hypot(dx, dz) < 2.5:
                    e["attack_timer"] = 0
                    if not self.p_dying:
                        self.p_health -= e["damage"]
                        if self.p_health <= 0:
                            self.start_death()

        # Powerups
        for pu in self.powerups:
            if not pu["alive"]:
                continue
            pu["bob"] += dt * 2
            pu["pos"][1] = pu["base_y"] + math.sin(pu["bob"]) * 0.3
            dx = pu["pos"][0] - self.px
            dy = pu["pos"][1] - self.py
            dz = pu["pos"][2] - self.pz
            if dx * dx + dy * dy + dz * dz < 2.25:
                pu["alive"] = False
                self.p_powerup = pu["type"]
                self.score += 50
                if pu["type"] == "toast":
                    self.p_health = min(self.p_health + 1, self.p_max_health)

        # Goal
        if self.goal_pos:
            dx = self.goal_pos[0] - self.px
            dz = self.goal_pos[2] - self.pz
            if dx * dx + dz * dz < 4:
                self.level_index += 1
                if self.level_index >= 5:
                    self.state = "win"
                    pygame.mouse.set_visible(True)
                else:
                    self.load_level(self.level_index)

    def start_death(self):
        if self.p_dying:
            return
        self.p_dying = True
        self.p_death_timer = 90
        self.p_vy = 8
        self.rage_quote = random.choice(RAGE_QUOTES)
        self.rage_timer = 90

    def confirm_death(self):
        self.total_deaths += 1
        self.state = "game_over"
        pygame.mouse.set_visible(True)

    def render(self):
        self.screen.fill((26, 15, 10))

        if self.state != "playing":
            if self.state == "menu":
                self.menu_screen()
            elif self.state == "game_over":
                self.game_over_screen()
            elif self.state == "win":
                self.win_screen()
            pygame.display.flip()
            return

        # Third-person camera behind player
        forward_x = math.sin(self.yaw)
        forward_z = math.cos(self.yaw)
        cam_x = self.px - forward_x * CAM_DIST
        cam_z = self.pz - forward_z * CAM_DIST
        cam_y = self.py + CAM_HEIGHT

        # Camera shake
        if self.cam_shake > 0:
            cam_x += random.uniform(-0.3, 0.3)
            cam_y += random.uniform(-0.2, 0.2)

        cam_pos = (cam_x, cam_y, cam_z)

        # Collect all drawables
        draw_queue = []

        # Player
        p_color = (0.82, 0.71, 0.55)
        if self.p_powerup:
            pc = {"toast": (0.71, 0.47, 0.24), "croissant": (0.86, 0.75, 0.55),
                  "bagel": (0.78, 0.63, 0.39), "sourdough": (0.63, 0.55, 0.39)}
            p_color = pc.get(self.p_powerup, p_color)
        if self.p_dying:
            p_color = (1, 0.4, 0.4)
        draw_queue.append(((self.px, self.py, self.pz), (0.6, 1.0, 0.6), p_color, (0, self.p_facing, 0)))
        draw_queue.append(((self.px, self.py + 0.7, self.pz), (0.8, 0.25, 0.8), (0.2, 0.2, 0.6), (0, self.p_facing, 0)))

        # Goal
        if self.goal_pos:
            bob = math.sin(self.frame_count * 0.05) * 0.2
            draw_queue.append(((self.goal_pos[0], self.goal_pos[1] + bob, self.goal_pos[2]), (1, 0.3, 1), (1, 0.84, 0), (0, 0, 0)))

        # Platforms
        for p in self.platforms:
            draw_queue.append((p["pos"], p["scale"], p["color"], (0, 0, 0)))

        # Enemies
        for e in self.enemies:
            if e["alive"]:
                color = (1, 0.3, 0.3) if e.get("flash", 0) > 0 else e["color"]
                draw_queue.append((tuple(e["pos"]), e["scale"], color, (0, 0, 0)))

        # Powerups
        for pu in self.powerups:
            if pu["alive"]:
                s = 0.35 + math.sin(pu["bob"]) * 0.05
                draw_queue.append((tuple(pu["pos"]), [s, s, s], pu["color"], (0, pu["bob"] * 3, 0)))

        # Sort by depth (far to near)
        def depth_key(item):
            pos = item[0]
            dx = pos[0] - cam_x
            dy = pos[1] - cam_y
            dz = pos[2] - cam_z
            # Rotate to camera space
            cos_y, sin_y = math.cos(self.yaw), math.sin(self.yaw)
            rz = dx * sin_y + dz * cos_y
            return -rz

        draw_queue.sort(key=depth_key)

        # Render all cubes
        for pos, scale, color, rot in draw_queue:
            proj = project_cube(pos[0], pos[1], pos[2], scale[0], scale[1], scale[2], cam_pos, self.yaw, self.pitch)
            if proj is not None:
                draw_cube_faces(self.screen, proj, color)

        self.hud()
        pygame.display.flip()


if __name__ == "__main__":
    g = Game3D()
    g.run()
    pygame.quit()
    sys.exit()
