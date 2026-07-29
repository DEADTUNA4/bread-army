import json
import pygame
from settings import TILE_SIZE


class Tile:
    def __init__(self, x, y, tile_type=0):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.type = tile_type
        self.solid = tile_type in (1, 2)
        self.hazard = tile_type in (3, 4, 8)
        self.fake = tile_type == 5
        self.ice = tile_type == 6
        self.conveyor = tile_type == 7
        self.passable = tile_type == 9

        self.colors = {
            0: None,
            1: (100, 60, 30),
            2: (80, 50, 20),
            3: (200, 200, 200),
            4: (200, 80, 0),
            5: (100, 60, 30),
            6: (150, 200, 255),
            7: (120, 120, 120),
            8: (180, 30, 30),
            9: None,
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

    def get_hazard_tiles(self):
        return [t for t in self.tiles if t.hazard]

    def get_fake_tiles(self):
        return [t for t in self.tiles if t.fake]

    def draw(self, surface, camera, frame=0):
        for tile in self.tiles:
            if tile.color is None:
                continue
            screen_rect = camera.apply(tile.rect)
            if screen_rect.right < -TILE_SIZE or screen_rect.left > 800 + TILE_SIZE:
                continue
            if screen_rect.bottom < -TILE_SIZE or screen_rect.top > 600 + TILE_SIZE:
                continue

            if tile.type == 3:
                wobble = int((frame * 0.1) % 4)
                pygame.draw.rect(surface, (160, 160, 160), screen_rect)
                for i in range(4):
                    sx = screen_rect.x + i * 8
                    points = [(sx, screen_rect.bottom), (sx + 4, screen_rect.y + 4), (sx + 8, screen_rect.bottom)]
                    pygame.draw.polygon(surface, (220, 220, 220), points)
            elif tile.type == 4:
                flicker = 20 if int(frame * 0.3) % 3 == 0 else 0
                lava_color = (min(255, 200 + flicker), 80 + flicker, 0)
                pygame.draw.rect(surface, lava_color, screen_rect)
                pygame.draw.rect(surface, (255, 200, 0), screen_rect, 2)
            elif tile.type == 6:
                pygame.draw.rect(surface, tile.color, screen_rect)
                pygame.draw.rect(surface, (200, 230, 255), screen_rect, 1)
            elif tile.type == 8:
                pulse = abs(int(frame * 0.2)) % 40
                pygame.draw.rect(surface, (180 + pulse, 30, 30), screen_rect)
            else:
                pygame.draw.rect(surface, tile.color, screen_rect)
                if tile.type == 2:
                    pygame.draw.rect(surface, (60, 40, 15), screen_rect, 1)
                if tile.type == 7:
                    arrow_dir = 1 if int(frame * 0.2) % 2 == 0 else -1
                    for i in range(0, TILE_SIZE, 8):
                        ax = screen_rect.x + (i if arrow_dir > 0 else TILE_SIZE - i)
                        pygame.draw.circle(surface, (180, 180, 180), (ax, screen_rect.centery), 1)
