from ursina import *
from src.threed.settings import VERSION, RAGE_QUOTES
from src.threed.ui import HUD, show_main_menu, menu_active
import random

game_manager = None


class GameManager:
    def __init__(self):
        global game_manager
        game_manager = self
        self.state = "menu"
        self.player = None
        self.level = None
        self.enemies = []
        self.powerups = []
        self.blocks = []
        self.score = 0
        self.total_deaths = 0
        self.level_index = 0
        self.goal = None
        self.hud = HUD()
        self.rage_quote = ""
        self.rage_timer = 0
        self.cam_orbit = 0
        self.cam_height = 4
        self.cam_dist = 8
        show_main_menu()

    def start_game(self):
        self.score = 0
        self.total_deaths = 0
        self.level_index = 0
        self.rage_quote = ""
        self.rage_timer = 0
        self.load_level(0)
        self.hud.show()

    def load_level(self, idx):
        self.clear_level()
        from src.threed.level import Level
        from src.threed.player import Player
        from src.threed.enemy import Enemy
        from src.threed.powerup import PowerUp
        from src.threed.blocks import MovingPlatform, CrumblingBlock, DisappearingBlock, FakeBlock

        self.state = "playing"
        self.level = Level(idx)
        self.level.build()
        self.player = Player(self.level.player_start)
        self.enemies = [Enemy(e) for e in self.level.enemy_data]
        self.powerups = [PowerUp(p) for p in self.level.powerup_data]
        self.blocks = []
        for b in self.level.block_data:
            t = b["type"]
            pos = b["pos"]
            if t == "moving":
                self.blocks.append(MovingPlatform(pos, b.get("axis", "x"), b.get("range", 4), b.get("speed", 0.03)))
            elif t == "crumbling":
                self.blocks.append(CrumblingBlock(pos))
            elif t == "disappearing":
                self.blocks.append(DisappearingBlock(pos, b.get("interval", 60)))
            elif t == "fake":
                self.blocks.append(FakeBlock(pos))
        self.goal = self.level.goal
        Sky()

    def clear_level(self):
        self.enemies.clear()
        self.powerups.clear()
        self.blocks.clear()
        if self.player:
            destroy(self.player)
            self.player = None
        if self.level:
            self.level.destroy()
            self.level = None

    def next_level(self):
        self.level_index += 1
        if self.level_index >= 5:
            self.state = "win"
            self.hud.hide()
            from src.threed.ui import show_win_screen
            show_win_screen(self.score, self.total_deaths)
        else:
            self.load_level(self.level_index)

    def restart_level(self):
        self.total_deaths += 1
        self.load_level(self.level_index)

    def game_over(self):
        self.state = "game_over"
        self.hud.hide()
        from src.threed.ui import show_game_over
        show_game_over(self.score, self.total_deaths, self.rage_quote)


def update():
    gm = game_manager
    if not gm:
        return

    if gm.state == "playing" and gm.player:
        dt = time.dt
        p = gm.player

        p.handle_input()
        p.update()

        # Camera orbit with mouse
        if mouse.velocity.length() > 0:
            gm.cam_orbit += mouse.velocity.x * 50 * dt
        target_pos = p.world_position + Vec3(
            math.sin(gm.cam_orbit) * gm.cam_dist,
            gm.cam_height,
            math.cos(gm.cam_orbit) * gm.cam_dist,
        )
        camera.position = lerp(camera.position, target_pos, dt * 10)
        camera.look_at(p.world_position + Vec3(0, 1.5, 0))

        # Enemies
        for e in gm.enemies[:]:
            e.update()
            if not e.alive:
                gm.score += 100
                gm.enemies.remove(e)

        # Blocks
        for b in gm.blocks:
            b.update()

        # Powerups
        for pu in gm.powerups[:]:
            pu.update()
            if distance(p.world_position, pu.world_position) < 1.5:
                pu.apply(p)
                gm.powerups.remove(pu)
                gm.score += 50

        # Enemy attacks
        for e in gm.enemies:
            if e.alive and e.can_attack(p):
                if p.take_damage(e.damage):
                    gm.rage_quote = random.choice(RAGE_QUOTES)
                    gm.rage_timer = 90
                    if p.death_timer <= 0:
                        gm.total_deaths += 1
                        gm.game_over()
                    return

        # Goal
        if gm.goal and distance(p.world_position, gm.goal) < 2:
            gm.next_level()
            return

        # Rage timer
        if gm.rage_timer > 0:
            gm.rage_timer -= 1

        # HUD
        gm.hud.update(
            score=gm.score,
            deaths=gm.total_deaths,
            level=gm.level_index,
            health=p.health,
            powerup=p.powerup,
            rage=gm.rage_quote,
            rage_timer=gm.rage_timer,
        )
