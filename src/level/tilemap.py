import json
import pygame
from settings import TILE_SIZE


class Tile:
    def __init__(self, x, y, tile_type=0):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.type = tile_type
        self.solid = tile_type != 0

        self.colors = {
            0: None,
            1: (100, 60, 30),
            2: (80, 50, 20),
            3: (120, 100, 60),
            4: (60, 120, 60),
            5: (200, 180, 120),
        }
        self.color = self.colors.get(tile_type, (100, 100, 100))


class TileMap:
    def __init__(self):
        self.tiles = []
        self.width = 0
        self.height = 0
        self.pixel_width = 0
        self.pixel_height = 0

    def load(self, filename):
        with open(filename, "r") as f:
            data = json.load(f)

        self.width = data["width"]
        self.height = data["height"]
        self.tile_data = data["layers"][0]["data"]
        self.pixel_width = self.width * TILE_SIZE
        self.pixel_height = self.height * TILE_SIZE

        self.tiles = []
        for y in range(self.height):
            for x in range(self.width):
                idx = y * self.width + x
                tile_type = self.tile_data[idx]
                if tile_type != 0:
                    self.tiles.append(Tile(x * TILE_SIZE, y * TILE_SIZE, tile_type))

    def get_solid_tiles(self):
        return [t for t in self.tiles if t.solid]

    def draw(self, surface, camera):
        for tile in self.tiles:
            if tile.color is None:
                continue
            screen_rect = camera.apply(tile.rect)
            if screen_rect.right < -TILE_SIZE or screen_rect.left > 800 + TILE_SIZE:
                continue
            if screen_rect.bottom < -TILE_SIZE or screen_rect.top > 600 + TILE_SIZE:
                continue
            pygame.draw.rect(surface, tile.color, screen_rect)
            if tile.type == 2:
                pygame.draw.rect(surface, (60, 40, 15), screen_rect, 1)
