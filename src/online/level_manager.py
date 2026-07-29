import json
import os
import requests
from src.online.manifest import Manifest, compute_hash

LEVELS_DIR = os.path.join("levels", "online")
BUNDLED_DIR = "levels"
MANIFEST_URL = "https://raw.githubusercontent.com/DEADTUNA4/bread-army-levels/main/manifest.json"
LEVEL_BASE_URL = "https://raw.githubusercontent.com/DEADTUNA4/bread-army-levels/main/levels/"


class LevelManager:
    def __init__(self):
        self.manifest = Manifest()
        os.makedirs(LEVELS_DIR, exist_ok=True)

    def fetch_manifest(self):
        try:
            resp = requests.get(MANIFEST_URL, timeout=5)
            if resp.status_code == 200:
                self.manifest = Manifest(resp.json())
                return True
        except requests.RequestException:
            pass
        return False

    def get_level_path(self, level_name):
        local_path = os.path.join(LEVELS_DIR, f"{level_name}.json")
        bundled_path = os.path.join(BUNDLED_DIR, f"{level_name}.json")

        if os.path.exists(local_path):
            return local_path

        if self.fetch_manifest():
            entry = self.manifest.levels.get(level_name)
            if entry:
                try:
                    url = LEVEL_BASE_URL + f"{level_name}.json"
                    resp = requests.get(url, timeout=5)
                    if resp.status_code == 200:
                        with open(local_path, "w") as f:
                            f.write(resp.text)
                        return local_path
                except requests.RequestException:
                    pass

        if os.path.exists(bundled_path):
            return bundled_path

        return None
