import json
from settings import TILE_SIZE
from src.entities.enemy import Enemy
from src.entities.powerup import PowerUp
from src.entities.blocks import MovingPlatform, CrumblingBlock, DisappearingBlock, FakeBlock


class Spawner:
    def __init__(self, level_file):
        self.entities = []
        self.blocks = []
        self.player_start = (100, 0)
        self.load(level_file)

    def load(self, filename):
        with open(filename, "r") as f:
            data = json.load(f)

        if "player_start" in data:
            self.player_start = tuple(data["player_start"])

        for layer in data.get("layers", []):
            if layer.get("name") == "entities":
                for obj in layer.get("objects", []):
                    entity_type = obj.get("type", "mold_slime")
                    x = obj["x"]
                    y = obj["y"]
                    w = obj.get("width", TILE_SIZE)

                    if entity_type == "player_start":
                        self.player_start = (x, y)
                    elif entity_type in ("mold_slime", "stale_cracker", "evil_crouton", "bread_golem", "mold_king", "crumb_fly"):
                        self.entities.append(Enemy(x, y, entity_type))
                    elif entity_type in ("toast", "croissant", "bagel", "sourdough"):
                        self.entities.append(PowerUp(x, y, entity_type))
                    elif entity_type == "moving_platform":
                        move_x = obj.get("move_x", 0)
                        move_y = obj.get("move_y", 96)
                        speed = obj.get("speed", 0.03)
                        self.blocks.append(MovingPlatform(x, y, w, move_x, move_y, speed))
                    elif entity_type == "crumbling_block":
                        self.blocks.append(CrumblingBlock(x, y))
                    elif entity_type == "disappearing_block":
                        self.blocks.append(DisappearingBlock(x, y))
                    elif entity_type == "fake_block":
                        self.blocks.append(FakeBlock(x, y))

    def get_entities(self):
        return self.entities

    def get_blocks(self):
        return self.blocks
