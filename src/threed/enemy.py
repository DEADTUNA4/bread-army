from ursina import *
from src.threed.settings import *
import math


class Enemy(Entity):
    def __init__(self, data):
        self._etype = data["type"]
        pos = data["pos"]
        cfg = ENEMY_CONFIG[self._etype]

        super().__init__(
            model=cfg["model"],
            color=cfg["color"],
            position=pos,
            scale=cfg["scale"],
            collider="box",
        )

        self.hp = cfg["hp"]
        self.damage = cfg["damage"]
        self.speed = cfg["speed"]
        self.alive = True
        self.patrol_range = data.get("patrol", 4)
        self.home_x = pos.x
        self.home_z = pos.z
        self.dir = 1
        self.attack_cooldown = 0

    def update(self):
        if not self.alive:
            return

        # Patrol back and forth in x direction
        self.x += self.dir * self.speed * time.dt
        if abs(self.x - self.home_x) > self.patrol_range:
            self.dir *= -1
        self.look_at(Vec3(self.x + self.dir, self.y, self.z))

        self.attack_cooldown += 1

    def can_attack(self, player):
        if not self.alive or self.attack_cooldown < 60:
            return False
        if distance(self.world_position, player.world_position) < 2.5:
            self.attack_cooldown = 0
            return True
        return False

    def take_damage(self, amount=1):
        if not self.alive:
            return
        self.hp -= amount
        self.flash_red()
        if self.hp <= 0:
            self.die()

    def flash_red(self):
        original = self.color
        self.color = color.red
        invoke(lambda: setattr(self, "color", original), delay=0.1)

    def die(self):
        self.alive = False
        self.animate("scale_y", 0, duration=0.3)
        invoke(destroy, self, delay=0.3)


ENEMY_CONFIG = {
    "slime": {
        "model": "sphere",
        "color": color.hex("#556B2F"),
        "scale": 0.8,
        "hp": 1,
        "damage": 1,
        "speed": 2,
    },
    "crouton": {
        "model": "cube",
        "color": color.hex("#D2691E"),
        "scale": 0.7,
        "hp": 2,
        "damage": 1,
        "speed": 2.5,
    },
    "cracker": {
        "model": "cube",
        "color": color.hex("#DEB887"),
        "scale": (0.6, 0.2, 0.8),
        "hp": 3,
        "damage": 1,
        "speed": 3,
    },
    "golem": {
        "model": "cube",
        "color": color.hex("#8B4513"),
        "scale": (1.2, 1.5, 1.2),
        "hp": 5,
        "damage": 2,
        "speed": 1.5,
    },
    "fly": {
        "model": "cube",
        "color": color.hex("#4A4A4A"),
        "scale": 0.5,
        "hp": 1,
        "damage": 1,
        "speed": 4,
    },
    "king": {
        "model": "cube",
        "color": color.hex("#800020"),
        "scale": (1.5, 2, 1.5),
        "hp": 10,
        "damage": 3,
        "speed": 2,
    },
}
