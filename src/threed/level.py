from ursina import *
from src.threed.settings import *


class Level:
    def __init__(self, index):
        self.index = index
        self.entities = []
        self.player_start = Vec3(0, 1, 0)
        self.goal = Vec3(0, 0, 0)
        self.enemy_data = []
        self.powerup_data = []
        self.block_data = []
        self._build_data()

    def _build_data(self):
        levels = [
            self._level_01,
            self._level_02,
            self._level_03,
            self._level_04,
            self._level_05,
        ]
        if self.index < len(levels):
            levels[self.index]()

    def _add_platform(self, x, y, z, sx, sy, sz, color_name="ground"):
        colors = {
            "ground": color.hex("#8B7355"),
            "grass": color.hex("#6B8E23"),
            "stone": color.hex("#808080"),
            "brick": color.hex("#B22222"),
            "ice": color.hex("#ADD8E6"),
            "lava": color.hex("#FF4500"),
            "gold": color.hex("#FFD700"),
            "goal": color.hex("#FFD700"),
        }
        c = colors.get(color_name, colors["ground"])
        e = Entity(
            model="cube",
            color=c,
            position=(x, y, z),
            scale=(sx, sy, sz),
            collider="box",
            texture="white_cube",
        )
        self.entities.append(e)
        return e

    def _add_terrain(self, width, depth, y=0):
        spacing = 4
        for x in range(-width // 2, width // 2, spacing):
            for z in range(-depth // 2, depth // 2, spacing):
                self._add_platform(x, y - 1, z, spacing, 1, spacing, "ground")

    def build(self):
        pass

    def destroy(self):
        for e in self.entities:
            destroy(e)
        self.entities.clear()

    def _level_01(self):
        self.player_start = Vec3(-12, 1, -8)
        self.goal = Vec3(12, 1, -8)

        self._add_platform(0, -1, 0, 40, 1, 12, "ground")
        self._add_platform(0, 0, 0, 40, 0.5, 12)

        self._add_platform(0, 2, -8, 8, 1, 4, "ground")
        self._add_platform(-6, 4, -4, 4, 1, 4, "stone")
        self._add_platform(6, 4, -4, 4, 1, 4, "stone")
        self._add_platform(0, 6, 0, 4, 1, 4, "gold")

        self.enemy_data = [
            {"type": "slime", "pos": Vec3(-4, 1, -2), "patrol": 4},
            {"type": "slime", "pos": Vec3(4, 1, -2), "patrol": 4},
            {"type": "crouton", "pos": Vec3(8, 1, -4), "patrol": 6},
        ]
        self.powerup_data = [
            {"type": "toast", "pos": Vec3(-2, 3, 0)},
            {"type": "croissant", "pos": Vec3(2, 5, 0)},
        ]
        self.block_data = [
            {"type": "moving", "pos": Vec3(0, 3, -4), "axis": "x", "range": 6, "speed": 0.03},
        ]

    def _level_02(self):
        self.player_start = Vec3(-14, 1, -8)
        self.goal = Vec3(14, 1, -8)

        self._add_platform(0, -1, 0, 44, 1, 16, "ground")
        self._add_platform(-10, 2, -4, 4, 1, 4, "stone")
        self._add_platform(-4, 4, -6, 4, 1, 4, "stone")
        self._add_platform(2, 6, -4, 4, 1, 4, "stone")
        self._add_platform(8, 4, -2, 4, 1, 4, "stone")

        self.enemy_data = [
            {"type": "slime", "pos": Vec3(-8, 1, 0), "patrol": 6},
            {"type": "crouton", "pos": Vec3(0, 1, 2), "patrol": 8},
            {"type": "cracker", "pos": Vec3(6, 1, -4), "patrol": 4},
        ]
        self.powerup_data = [
            {"type": "toast", "pos": Vec3(-3, 3, 0)},
        ]
        self.block_data = []

    def _level_03(self):
        self.player_start = Vec3(-16, 1, -8)
        self.goal = Vec3(16, 1, -8)

        self._add_platform(0, -1, 0, 48, 1, 16, "ground")
        self._add_platform(-12, 2, -4, 4, 1, 4, "ice")
        self._add_platform(-6, 4, -6, 4, 1, 4, "ice")
        self._add_platform(0, 6, -4, 4, 1, 4, "ice")
        self._add_platform(6, 4, -2, 4, 1, 4, "ice")

        self.enemy_data = [
            {"type": "slime", "pos": Vec3(-10, 1, 0), "patrol": 4},
            {"type": "crouton", "pos": Vec3(-2, 1, 2), "patrol": 6},
            {"type": "cracker", "pos": Vec3(4, 1, -4), "patrol": 4},
            {"type": "golem", "pos": Vec3(10, 1, 0), "patrol": 6},
        ]
        self.powerup_data = [
            {"type": "bagel", "pos": Vec3(0, 5, 0)},
        ]
        self.block_data = [
            {"type": "crumbling", "pos": Vec3(-8, 3, -2)},
            {"type": "crumbling", "pos": Vec3(-8, 3, 0)},
        ]

    def _level_04(self):
        self.player_start = Vec3(-18, 1, -8)
        self.goal = Vec3(18, 1, -8)

        self._add_platform(0, -1, 0, 52, 1, 16, "ground")
        self._add_platform(-14, 2, -4, 4, 1, 4, "brick")
        self._add_platform(-8, 4, -6, 4, 1, 4, "brick")
        self._add_platform(-2, 6, -4, 4, 1, 4, "brick")
        self._add_platform(4, 4, -2, 4, 1, 4, "brick")
        self._add_platform(10, 2, 0, 4, 1, 4, "brick")

        self.enemy_data = [
            {"type": "slime", "pos": Vec3(-12, 1, 0), "patrol": 4},
            {"type": "crouton", "pos": Vec3(-6, 1, 2), "patrol": 6},
            {"type": "cracker", "pos": Vec3(2, 1, -4), "patrol": 4},
            {"type": "golem", "pos": Vec3(8, 1, 4), "patrol": 8},
            {"type": "fly", "pos": Vec3(14, 4, 0), "patrol": 4},
        ]
        self.powerup_data = [
            {"type": "sourdough", "pos": Vec3(-2, 5, 0)},
        ]
        self.block_data = [
            {"type": "disappearing", "pos": Vec3(-8, 5, -2), "interval": 60},
            {"type": "disappearing", "pos": Vec3(-8, 5, 2), "interval": 60},
        ]

    def _level_05(self):
        self.player_start = Vec3(-20, 1, -8)
        self.goal = Vec3(20, 1, -8)

        self._add_platform(0, -1, 0, 56, 1, 16, "ground")
        self._add_platform(-16, 2, -4, 4, 1, 4, "stone")
        self._add_platform(-10, 4, -6, 4, 1, 4, "stone")
        self._add_platform(-4, 6, -4, 4, 1, 4, "stone")
        self._add_platform(2, 4, -2, 4, 1, 4, "stone")
        self._add_platform(8, 6, 0, 4, 1, 4, "stone")
        self._add_platform(14, 4, -4, 4, 1, 4, "stone")

        self.enemy_data = [
            {"type": "slime", "pos": Vec3(-14, 1, 0), "patrol": 4},
            {"type": "crouton", "pos": Vec3(-8, 1, 2), "patrol": 6},
            {"type": "cracker", "pos": Vec3(-2, 1, -4), "patrol": 4},
            {"type": "golem", "pos": Vec3(4, 1, 4), "patrol": 8},
            {"type": "fly", "pos": Vec3(10, 4, -2), "patrol": 6},
            {"type": "king", "pos": Vec3(16, 1, 0), "patrol": 10},
        ]
        self.powerup_data = [
            {"type": "toast", "pos": Vec3(-10, 3, 0)},
            {"type": "bagel", "pos": Vec3(2, 5, 0)},
            {"type": "sourdough", "pos": Vec3(14, 0, 2)},
        ]
        self.block_data = [
            {"type": "moving", "pos": Vec3(-6, 5, -2), "axis": "z", "range": 4, "speed": 0.04},
            {"type": "crumbling", "pos": Vec3(0, 3, 0)},
            {"type": "disappearing", "pos": Vec3(6, 5, -4), "interval": 45},
            {"type": "fake", "pos": Vec3(12, 3, -2)},
        ]
