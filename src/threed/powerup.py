from ursina import *
from src.threed.settings import *


class PowerUp(Entity):
    def __init__(self, data):
        self._type = data["type"]
        cfg = POWERUP_CONFIG[self._type]

        super().__init__(
            model=cfg["model"],
            color=cfg["color"],
            position=data["pos"],
            scale=0.5,
            collider="box",
        )

        self.powerup_type = self._type
        self.bob_offset = data["pos"].y

        label = Text(
            parent=self,
            text=cfg["label"],
            position=(0, 0.6, 0),
            scale=10,
            origin=(0, 0),
            color=color.white,
        )

    def update(self):
        self.y = self.bob_offset + math.sin(time.time * 2) * 0.3
        self.rotation_y += 1

    def apply(self, player):
        player.set_powerup(self.powerup_type)
        if self.powerup_type == "toast":
            player.heal(1)
        destroy(self)


POWERUP_CONFIG = {
    "toast": {
        "model": "cube",
        "color": color.hex("#b4783c"),
        "label": "T",
    },
    "croissant": {
        "model": "sphere",
        "color": color.hex("#dcbe8c"),
        "label": "C",
    },
    "bagel": {
        "model": "cylinder",
        "color": color.hex("#c8a064"),
        "label": "B",
    },
    "sourdough": {
        "model": "cube",
        "color": color.hex("#a08c64"),
        "label": "S",
    },
}
