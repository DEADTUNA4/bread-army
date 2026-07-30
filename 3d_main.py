import pygame
import math
import sys
import os
import random

sys.path.insert(0, os.path.dirname(__file__))
from src.threed.settings import *

WIDTH, HEIGHT = 1024, 768


def project(x, y, z, pitch, yaw, cam_x, cam_y, cam_z):
    # Translate relative to camera
    dx = x - cam_x
    dy = y - cam_y
    dz = z - cam_z
    # Rotate by yaw (around Y)
    cos_y, sin_y = math.cos(yaw), math.sin(yaw)
    rx = dx * cos_y - dz * sin_y
    rz = dx * sin_y + dz * cos_y
    # Rotate by pitch (around X)
    cos_p, sin_p = math.cos(pitch), math.sin(pitch)
    ry = dy * cos_p - rz * sin_p
    rz = dy * sin_p + rz * cos_p
    if rz < 0.5:
        return None
    fov = 800
    sx = WIDTH / 2 + (rx / rz) * fov
    sy = HEIGHT / 2 - (ry / rz) * fov
    return (sx, sy, rz)


def draw_cube(surf, x, y, z, sx, sy, sz, color, pitch, yaw, cam_x, cam_y, cam_z):
    corners = [
        (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5),
        (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5),
    ]
    proj = []
    for c in corners:
        wx = x + c[0] * sx
        wy = y + c[1] * sy
        wz = z + c[2] * sz
        p = project(wx, wy, wz, pitch, yaw, cam_x, cam_y, cam_z)
        if p is None:
            return None
        proj.append(p)
    return proj


def draw_cube_faces(surf, proj, color, shade=0):
    faces = [
        (0, 1, 2, 3),  # front
        (4, 5, 6, 7),  # back
        (1, 5, 6, 2),  # right
        (0, 4, 7, 3),  # left
        (3, 2, 6, 7),  # top
        (0, 1, 5, 4),  # bottom
    ]
    shade_amount = shade * 0.3
    for fi, face in enumerate(faces):
        pts = [proj[i] for i in face]
        z_avg = sum(p[2] for p in pts) / 4
        shade_i = [0, 0, 0, -0.15, 0.15, -0.25][fi]
        c = (
            max(0, min(1, color[0] + shade_amount + shade_i)),
            max(0, min(1, color[1] + shade_amount + shade_i)),
            max(0, min(1, color[2] + shade_amount + shade_i)),
        )
        pts_2d = [(p[0], p[1]) for p in pts]
        pygame.draw.polygon(surf, (int(c[0]*255), int(c[1]*255), int(c[2]*255)), pts_2d)
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
        self.p_rot = 0
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
        self.mouse_locked = False
        self.frame_count = 0

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

    def hud(self):
        hearts = "♥" * self.p_health + "♡" * (self.p_max_health - self.p_health)
        self.text(hearts, 20, 16, (255, 50, 50), 28)
        self.text(f"Score: {self.score}", WIDTH - 20, 16, (255, 255, 255), 22)
        r = self.font(22).render(f"Score: {self.score}", True, (0, 0, 0)).get_rect()
        self.text(f"Level {self.level_index + 1}", WIDTH - 20, 16 + r.height + 4, (180, 180, 180), 18)
        if self.total_deaths > 0:
            self.text(f"Deaths: {self.total_deaths}", WIDTH - 20, 16 + r.height * 2 + 4, (255, 100, 100), 18)
        if self.p_powerup:
            self.text(f"Power: {self.p_powerup.upper()}", 20, 50, (255, 215, 0), 20)
        if self.rage_timer > 0 and self.rage_quote:
            self.text(self.rage_quote, WIDTH // 2, HEIGHT // 2 - 60, (255, 50, 50), 36, center=True)

    def menu_screen(self):
        self.screen.fill((26, 15, 10))
        self.text("BREAD ARMY 3D", WIDTH // 2, 180, (255, 215, 0), 72, center=True)
        self.text("Prepare to suffer.", WIDTH // 2, 250, (150, 20, 20), 28, center=True)
        self.text("WASD - Move  |  Mouse - Look  |  Space - Jump  |  Click - Attack", WIDTH // 2, 350, (180, 180, 180), 18, center=True)
        self.text("Press ENTER to start", WIDTH // 2, 420, (255, 255, 255), 32, center=True)
        self.text("Press ESC to quit", WIDTH // 2, 460, (128, 128, 128), 20, center=True)
        self.text(VERSION, WIDTH // 2, HEIGHT - 30, (100, 100, 100), 16, center=True)

    def game_over_screen(self):
        self.screen.fill((15, 0, 0))
        self.text("YOU DIED", WIDTH // 2, 180, (150, 20, 20), 72, center=True)
        if self.rage_quote:
            self.text(self.rage_quote, WIDTH // 2, 260, (255, 50, 50), 36, center=True)
        self.text(f"Score: {self.score}", WIDTH // 2, 330, (255, 215, 0), 32, center=True)
        self.text(f"Deaths: {self.total_deaths}", WIDTH // 2, 370, (255, 100, 100), 32, center=True)
        self.text("Press ENTER to retry", WIDTH // 2, 450, (255, 255, 255), 28, center=True)
        self.text("Press ESC for menu", WIDTH // 2, 490, (128, 128, 128), 20, center=True)

    def win_screen(self):
        self.screen.fill((5, 15, 5))
        self.text("YOU SURVIVED", WIDTH // 2, 180, (255, 215, 0), 72, center=True)
        self.text(f"Final Score: {self.score}", WIDTH // 2, 280, (255, 215, 0), 32, center=True)
        self.text(f"Deaths: {self.total_deaths}", WIDTH // 2, 320, (255, 100, 100), 32, center=True)
        if self.total_deaths == 0:
            comment = "IMPOSSIBLE. You didn't die once?"
        elif self.total_deaths < 5:
            comment = f"Not bad... only {self.total_deaths} deaths."
        elif self.total_deaths < 20:
            comment = f"You suffered {self.total_deaths} times. Worth it?"
        else:
            comment = f"{self.total_deaths} deaths. You are a masochist."
        self.text(comment, WIDTH // 2, 370, (200, 200, 200), 24, center=True)
        self.text("Press ENTER to play again", WIDTH // 2, 450, (255, 255, 255), 28, center=True)
        self.text("Press ESC for menu", WIDTH // 2, 490, (128, 128, 128), 20, center=True)

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
            "alive": True, "bob": random.random() * 6.28,
        })

    def l1(self):
        self.px, self.pz = -12, -8
        self.goal_pos = (12, 1, -8)
        self.plat(0, -1, 0, 40, 1, 12, (0.55, 0.45, 0.33))
        self.plat(0, 2, -8, 8, 1, 4, (0.55, 0.45, 0.33))
        self.plat(-6, 4, -4, 4, 1, 4, (0.5, 0.5, 0.5))
        self.plat(6, 4, -4, 4, 1, 4, (0.5, 0.5, 0.5))
        self.plat(0, 6, 0, 4, 1, 4, (1, 0.84, 0))
        self.enemy("slime", -4, -2)
        self.enemy("slime", 4, -2)
        self.enemy("crouton", 8, -4, 6)
        self.powerup("toast", -2, 4, 0)
        self.powerup("croissant", 2, 7, 0)

    def l2(self):
        self.px, self.pz = -14, -8
        self.goal_pos = (14, 1, -8)
        self.plat(0, -1, 0, 44, 1, 16, (0.55, 0.45, 0.33))
        self.plat(-10, 2, -4, 4, 1, 4, (0.5, 0.5, 0.5))
        self.plat(-4, 4, -6, 4, 1, 4, (0.5, 0.5, 0.5))
        self.plat(2, 6, -4, 4, 1, 4, (0.5, 0.5, 0.5))
        self.plat(8, 4, -2, 4, 1, 4, (0.5, 0.5, 0.5))
        self.enemy("slime", -8, 0, 6)
        self.enemy("crouton", 0, 2, 8)
        self.enemy("cracker", 6, -4, 4)
        self.powerup("toast", -3, 4, 0)

    def l3(self):
        self.px, self.pz = -16, -8
        self.goal_pos = (16, 1, -8)
        self.plat(0, -1, 0, 48, 1, 16, (0.55, 0.45, 0.33))
        self.plat(-12, 2, -4, 4, 1, 4, (0.68, 0.85, 0.9))
        self.plat(-6, 4, -6, 4, 1, 4, (0.68, 0.85, 0.9))
        self.plat(0, 6, -4, 4, 1, 4, (0.68, 0.85, 0.9))
        self.plat(6, 4, -2, 4, 1, 4, (0.68, 0.85, 0.9))
        self.enemy("slime", -10, 0, 4)
        self.enemy("crouton", -2, 2, 6)
        self.enemy("cracker", 4, -4, 4)
        self.enemy("golem", 10, 0, 6)
        self.powerup("bagel", 0, 7, 0)

    def l4(self):
        self.px, self.pz = -18, -8
        self.goal_pos = (18, 1, -8)
        self.plat(0, -1, 0, 52, 1, 16, (0.55, 0.45, 0.33))
        self.plat(-14, 2, -4, 4, 1, 4, (0.7, 0.13, 0.13))
        self.plat(-8, 4, -6, 4, 1, 4, (0.7, 0.13, 0.13))
        self.plat(-2, 6, -4, 4, 1, 4, (0.7, 0.13, 0.13))
        self.plat(4, 4, -2, 4, 1, 4, (0.7, 0.13, 0.13))
        self.plat(10, 2, 0, 4, 1, 4, (0.7, 0.13, 0.13))
        self.enemy("slime", -12, 0, 4)
        self.enemy("crouton", -6, 2, 6)
        self.enemy("cracker", 2, -4, 4)
        self.enemy("golem", 8, 4, 8)
        self.enemy("fly", 14, 0, 4)
        self.powerup("sourdough", -2, 7, 0)

    def l5(self):
        self.px, self.pz = -20, -8
        self.goal_pos = (20, 1, -8)
        self.plat(0, -1, 0, 56, 1, 16, (0.55, 0.45, 0.33))
        self.plat(-16, 2, -4, 4, 1, 4, (0.5, 0.5, 0.5))
        self.plat(-10, 4, -6, 4, 1, 4, (0.5, 0.5, 0.5))
        self.plat(-4, 6, -4, 4, 1, 4, (0.5, 0.5, 0.5))
        self.plat(2, 4, -2, 4, 1, 4, (0.5, 0.5, 0.5))
        self.plat(8, 6, 0, 4, 1, 4, (0.5, 0.5, 0.5))
        self.plat(14, 4, -4, 4, 1, 4, (0.5, 0.5, 0.5))
        self.enemy("slime", -14, 0, 4)
        self.enemy("crouton", -8, 2, 6)
        self.enemy("cracker", -2, -4, 4)
        self.enemy("golem", 4, 4, 8)
        self.enemy("fly", 10, -2, 6)
        self.enemy("king", 16, 0, 10)
        self.powerup("toast", -10, 4, 0)
        self.powerup("bagel", 2, 7, 0)
        self.powerup("sourdough", 14, 2, 2)

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
                    elif self.state == "menu":
                        self.running = False
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
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
                    if self.p_attack_cooldown <= 0 and not self.p_dying:
                        self.p_attack_cooldown = 15

    def update(self):
        if self.state != "playing":
            return

        dt = self.dt
        keys = pygame.key.get_pressed()

        mx, mz = 0, 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            mx -= math.cos(self.yaw)
            mz -= math.sin(self.yaw)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            mx += math.cos(self.yaw)
            mz += math.sin(self.yaw)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            mx += math.sin(self.yaw)
            mz -= math.cos(self.yaw)
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            mx -= math.sin(self.yaw)
            mz += math.cos(self.yaw)

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

        # Ground / gravity
        gnd = self.get_ground(self.px, self.pz)
        if gnd > -999 and self.py <= gnd + 0.5 and self.p_vy <= 0:
            self.p_grounded = True
            self.py = gnd + 0.5
            self.p_vy = 0
        else:
            self.p_grounded = False

        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.p_grounded:
            self.p_vy = 10
            self.p_grounded = False

        self.p_vy -= 30 * dt
        self.py += self.p_vy * dt

        if self.py < -20:
            self.die()

        if self.p_attack_cooldown > 0:
            self.p_attack_cooldown -= 1

        if self.p_dying:
            self.p_death_timer -= 1
            self.p_vy -= 20 * dt
            self.py += self.p_vy * dt
            if self.p_death_timer <= 0:
                self.die()

        if self.rage_timer > 0:
            self.rage_timer -= 1

        # Enemies
        for e in self.enemies:
            if not e["alive"]:
                continue
            e["pos"][0] += e["dir"] * e["speed"] * dt
            if abs(e["pos"][0] - e["home_x"]) > e["patrol"]:
                e["dir"] *= -1
            e["attack_timer"] += 1
            if e["attack_timer"] >= 60:
                dx = e["pos"][0] - self.px
                dz = e["pos"][2] - self.pz
                if math.hypot(dx, dz) < 2.5:
                    e["attack_timer"] = 0
                    if not self.p_dying:
                        self.p_health -= e["damage"]
                        if self.p_health <= 0:
                            self.rage_quote = random.choice(RAGE_QUOTES)
                            self.rage_timer = 90
                            self.p_dying = True
                            self.p_death_timer = 90
                            self.p_vy = 8

        # Powerups
        for pu in self.powerups:
            if not pu["alive"]:
                continue
            pu["bob"] += dt * 2
            if "base_y" not in pu:
                pu["base_y"] = pu["pos"][1]
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

    def die(self):
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

        # 3D render
        cam_x = self.px + math.sin(self.yaw) * 0
        cam_y = self.py + 3
        cam_z = self.pz + math.cos(self.yaw) * 0

        cam_x = self.px
        cam_z = self.pz

        # Sort all drawable objects by depth
        draw_queue = []

        # Player
        p_color = (0.82, 0.71, 0.55)
        if self.p_powerup:
            pc = {"toast": (0.71, 0.47, 0.24), "croissant": (0.86, 0.75, 0.55),
                  "bagel": (0.78, 0.63, 0.39), "sourdough": (0.63, 0.55, 0.39)}
            p_color = pc.get(self.p_powerup, p_color)
        if self.p_dying:
            p_color = (1, 0.4, 0.4)
        draw_queue.append(((self.px, self.py, self.pz), (0.6, 1.0, 0.6), p_color))
        draw_queue.append(((self.px, self.py + 0.7, self.pz), (0.8, 0.25, 0.8), (0.2, 0.2, 0.6)))

        # Goal
        if self.goal_pos:
            draw_queue.append((self.goal_pos, (1, 0.3, 1), (1, 0.84, 0)))

        # Platforms
        for p in self.platforms:
            draw_queue.append((p["pos"], p["scale"], p["color"]))

        # Enemies
        for e in self.enemies:
            if e["alive"]:
                draw_queue.append((tuple(e["pos"]), e["scale"], e["color"]))

        # Powerups
        for pu in self.powerups:
            if pu["alive"]:
                s = 0.35 + math.sin(pu["bob"]) * 0.05
                draw_queue.append((tuple(pu["pos"]), [s, s, s], pu["color"]))

        # Depth sort
        def depth_key(item):
            pos = item[0]
            dx = pos[0] - cam_x
            dy = pos[1] - cam_y
            dz = pos[2] - cam_z
            return -(dx * dx + dy * dy + dz * dz)

        draw_queue.sort(key=depth_key)

        for pos, scale, color in draw_queue:
            cx, cy, cz = pos
            sx, sy, sz = scale
            corners = [
                (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5),
                (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5),
            ]
            proj = []
            valid = True
            for c in corners:
                wx = cx + c[0] * sx
                wy = cy + c[1] * sy
                wz = cz + c[2] * sz
                dx = wx - cam_x
                dy = wy - cam_y
                dz = wz - cam_z
                # Rotate by yaw
                cos_y, sin_y = math.cos(self.yaw), math.sin(self.yaw)
                rx = dx * cos_y - dz * sin_y
                rz = dx * sin_y + dz * cos_y
                # Rotate by pitch
                cos_p, sin_p = math.cos(self.pitch), math.sin(self.pitch)
                ry = dy * cos_p - rz * sin_p
                rz = dy * sin_p + rz * cos_p
                if rz < 0.3:
                    valid = False
                    break
                fov = 600
                sx2 = WIDTH / 2 + (rx / rz) * fov
                sy2 = HEIGHT / 2 - (ry / rz) * fov
                proj.append((sx2, sy2, rz))

            if not valid:
                continue

            # Draw faces
            faces = [
                (0, 1, 2, 3, 0), (4, 5, 6, 7, 1), (1, 5, 6, 2, 2),
                (0, 4, 7, 3, 3), (3, 2, 6, 7, 4), (0, 1, 5, 4, 5),
            ]
            shade_offsets = [0, 0, -0.15, -0.15, 0.15, -0.25]
            for idxs in faces:
                fi = idxs[4]
                pts = [proj[i] for i in idxs[:4]]
                shade = shade_offsets[fi]
                c = (max(0, min(1, color[0] + shade)),
                     max(0, min(1, color[1] + shade)),
                     max(0, min(1, color[2] + shade)))
                pygame.draw.polygon(self.screen, (int(c[0]*255), int(c[1]*255), int(c[2]*255)),
                                   [(p[0], p[1]) for p in pts])

        self.hud()
        pygame.display.flip()


if __name__ == "__main__":
    g = Game3D()
    g.run()
    pygame.quit()
    sys.exit()
