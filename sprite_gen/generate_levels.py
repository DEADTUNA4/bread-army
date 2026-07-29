import json
import os

LEVELS_DIR = "levels"

def make_terrain(width, height, ground_y=None, platforms=None):
    if ground_y is None:
        ground_y = height - 2
    data = [0] * (width * height)
    for y in range(ground_y, height):
        for x in range(width):
            data[y * width + x] = 1
    if platforms:
        for px, py, pw in platforms:
            for x in range(px, px + pw):
                data[py * width + x] = 1
    return data


def make_level(name, width, height, terrain_func, entities, player_start):
    terrain = terrain_func(width, height)
    data = {
        "width": width,
        "height": height,
        "tile_size": 32,
        "player_start": player_start,
        "layers": [
            {"name": "terrain", "data": terrain},
            {"name": "entities", "objects": entities},
        ],
    }
    path = os.path.join(LEVELS_DIR, f"{name}.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  Created: {path}")


# Level 02 - The Crumb Factory
def terrain_02(w, h):
    return make_terrain(w, h, ground_y=18, platforms=[
        (10, 15, 5), (18, 12, 4), (25, 14, 6), (35, 10, 3),
        (40, 13, 5), (50, 11, 4), (55, 15, 5), (65, 9, 3),
        (70, 12, 6), (80, 14, 4), (90, 10, 5), (100, 13, 4),
    ])

make_level("level_02", 120, 20, terrain_02, [
    {"type": "player_start", "x": 100, "y": 300},
    {"type": "mold_slime", "x": 400, "y": 500},
    {"type": "mold_slime", "x": 500, "y": 500},
    {"type": "evil_crouton", "x": 700, "y": 400},
    {"type": "mold_slime", "x": 900, "y": 500},
    {"type": "evil_crouton", "x": 1200, "y": 400},
    {"type": "stale_cracker", "x": 1500, "y": 480},
    {"type": "stale_cracker", "x": 1700, "y": 480},
    {"type": "toast", "x": 600, "y": 350},
    {"type": "evil_crouton", "x": 2000, "y": 400},
    {"type": "mold_slime", "x": 2300, "y": 500},
    {"type": "croissant", "x": 2600, "y": 300},
    {"type": "stale_cracker", "x": 2900, "y": 480},
    {"type": "evil_crouton", "x": 3200, "y": 400},
    {"type": "mold_slime", "x": 3400, "y": 500},
    {"type": "bread_golem", "x": 3600, "y": 400},
], [100, 300])


# Level 03 - The Oven of Doom
def terrain_03(w, h):
    return make_terrain(w, h, ground_y=18, platforms=[
        (5, 16, 4), (12, 13, 3), (18, 10, 5), (25, 7, 3),
        (30, 12, 4), (38, 8, 3), (42, 14, 5), (50, 6, 3),
        (55, 10, 4), (60, 15, 5), (68, 8, 3), (72, 12, 4),
        (78, 6, 3), (82, 10, 5), (88, 14, 3), (92, 8, 4),
        (98, 12, 3), (102, 6, 5), (108, 10, 3), (112, 14, 4),
    ])

make_level("level_03", 120, 20, terrain_03, [
    {"type": "player_start", "x": 100, "y": 300},
    {"type": "mold_slime", "x": 350, "y": 400},
    {"type": "mold_slime", "x": 450, "y": 300},
    {"type": "evil_crouton", "x": 600, "y": 500},
    {"type": "mold_slime", "x": 750, "y": 400},
    {"type": "stale_cracker", "x": 900, "y": 450},
    {"type": "evil_crouton", "x": 1050, "y": 500},
    {"type": "mold_slime", "x": 1200, "y": 350},
    {"type": "stale_cracker", "x": 1350, "y": 450},
    {"type": "toast", "x": 500, "y": 200},
    {"type": "evil_crouton", "x": 1500, "y": 500},
    {"type": "mold_slime", "x": 1650, "y": 400},
    {"type": "evil_crouton", "x": 1800, "y": 500},
    {"type": "stale_cracker", "x": 1950, "y": 450},
    {"type": "bagel", "x": 2000, "y": 250},
    {"type": "mold_slime", "x": 2100, "y": 300},
    {"type": "evil_crouton", "x": 2250, "y": 500},
    {"type": "stale_cracker", "x": 2400, "y": 450},
    {"type": "mold_slime", "x": 2550, "y": 350},
    {"type": "evil_crouton", "x": 2700, "y": 500},
    {"type": "bread_golem", "x": 3000, "y": 400},
    {"type": "bread_golem", "x": 3400, "y": 300},
], [100, 300])


# Level 04 - The Bakery's Heart (Final)
def terrain_04(w, h):
    return make_terrain(w, h, ground_y=18, platforms=[
        (5, 15, 6), (15, 12, 4), (22, 9, 5), (30, 6, 3),
        (35, 11, 4), (42, 7, 3), (45, 13, 5), (52, 8, 4),
        (58, 12, 3), (62, 6, 5), (68, 10, 4), (72, 14, 3),
        (78, 8, 4), (82, 12, 5), (88, 6, 3),
    ])

make_level("level_04", 100, 20, terrain_04, [
    {"type": "player_start", "x": 100, "y": 300},
    {"type": "mold_slime", "x": 400, "y": 400},
    {"type": "evil_crouton", "x": 550, "y": 500},
    {"type": "stale_cracker", "x": 700, "y": 450},
    {"type": "mold_slime", "x": 850, "y": 400},
    {"type": "evil_crouton", "x": 1000, "y": 500},
    {"type": "toast", "x": 600, "y": 300},
    {"type": "stale_cracker", "x": 1150, "y": 450},
    {"type": "evil_crouton", "x": 1300, "y": 500},
    {"type": "mold_slime", "x": 1450, "y": 350},
    {"type": "sourdough", "x": 1500, "y": 250},
    {"type": "evil_crouton", "x": 1600, "y": 500},
    {"type": "stale_cracker", "x": 1750, "y": 450},
    {"type": "mold_slime", "x": 1900, "y": 400},
    {"type": "evil_crouton", "x": 2050, "y": 500},
    {"type": "stale_cracker", "x": 2200, "y": 450},
    {"type": "mold_slime", "x": 2350, "y": 350},
    {"type": "bread_golem", "x": 2600, "y": 400},
    {"type": "bread_golem", "x": 2800, "y": 350},
    {"type": "bread_golem", "x": 3000, "y": 400},
], [100, 300])


# Level 05 - Bread Golem Citadel (Boss Rush)
def terrain_05(w, h):
    return make_terrain(w, h, ground_y=18, platforms=[
        (8, 15, 4), (16, 11, 5), (25, 7, 3), (30, 13, 4),
        (38, 8, 3), (42, 14, 5), (50, 6, 4), (55, 10, 3),
        (60, 15, 4), (68, 8, 3), (72, 12, 5), (78, 6, 3),
    ])

make_level("level_05", 100, 20, terrain_05, [
    {"type": "player_start", "x": 100, "y": 300},
    {"type": "evil_crouton", "x": 500, "y": 500},
    {"type": "evil_crouton", "x": 700, "y": 400},
    {"type": "mold_slime", "x": 900, "y": 450},
    {"type": "stale_cracker", "x": 1100, "y": 450},
    {"type": "toast", "x": 800, "y": 300},
    {"type": "croissant", "x": 1200, "y": 250},
    {"type": "bagel", "x": 1500, "y": 200},
    {"type": "sourdough", "x": 1800, "y": 250},
    {"type": "bread_golem", "x": 2000, "y": 400},
    {"type": "bread_golem", "x": 2300, "y": 350},
    {"type": "bread_golem", "x": 2600, "y": 400},
    {"type": "mold_slime", "x": 2800, "y": 300},
    {"type": "evil_crouton", "x": 2900, "y": 350},
    {"type": "stale_cracker", "x": 3000, "y": 400},
], [100, 300])

print("Levels generated:")
