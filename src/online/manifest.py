import json
import hashlib
import os


LEVELS_DIR = os.path.join("levels", "online")


class Manifest:
    def __init__(self, data=None):
        self.levels = {}
        if data:
            self.parse(data)

    def parse(self, data):
        for level_name, info in data.get("levels", {}).items():
            self.levels[level_name] = {
                "version": info.get("version", ""),
                "url": info.get("url", ""),
            }

    def get_version(self, level_name):
        entry = self.levels.get(level_name)
        return entry["version"] if entry else None

    def needs_update(self, level_name, local_version):
        remote = self.get_version(level_name)
        if remote is None:
            return False
        return remote != local_version


def compute_hash(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()[:8]
