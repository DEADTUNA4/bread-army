import json
from src.entities.enemy import Enemy
from src.entities.powerup import PowerUp


class Spawner:
    def __init__(self, level_file):
        self.entities = []
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

                    if entity_type == "player_start":
                        self.player_start = (x, y)
                    elif entity_type in ("mold_slime", "stale_cracker", "evil_crouton", "bread_golem"):
                        self.entities.append(Enemy(x, y, entity_type))
                    elif entity_type in ("toast", "croissant", "bagel", "sourdough"):
                        from src.entities.powerup import PowerUp
                        self.entities.append(PowerUp(x, y, entity_type))

    def get_entities(self):
        return self.entities
