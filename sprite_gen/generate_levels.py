import json
import os

LEVELS_DIR = "levels"

TILE_EMPTY = 0
TILE_GROUND = 1
TILE_GROUND2 = 2
TILE_SPIKES = 3
TILE_LAVA = 4
TILE_FAKE = 5
TILE_ICE = 6
TILE_CONVEYOR = 7
TILE_RED_SPIKES = 8
TILE_INVISIBLE = 9

W = 120
H = 30
GROUND_Y = 28


def make_empty(w, h):
    return [TILE_EMPTY] * (w * h)


def set_tile(data, w, x, y, t):
    if 0 <= x < w and 0 <= y < H:
        data[y * w + x] = t


def set_rect(data, w, x, y, rw, rh, t):
    for dy in range(rh):
        for dx in range(rw):
            set_tile(data, w, x + dx, y + dy, t)


def make_ground(data, w):
    for x in range(w):
        set_tile(data, w, x, GROUND_Y, TILE_GROUND)
        set_tile(data, w, x, GROUND_Y + 1, TILE_GROUND2)


def make_level(name, terrain_func, entities, player_start):
    w, h = W, H
    data = make_empty(w, h)
    terrain_func(data, w)

    level_data = {
        "width": w,
        "height": h,
        "tile_size": 32,
        "player_start": player_start,
        "layers": [
            {"name": "terrain", "data": data},
            {"name": "entities", "objects": entities},
        ],
    }
    path = os.path.join(LEVELS_DIR, f"{name}.json")
    with open(path, "w") as f:
        json.dump(level_data, f)
    print(f"  Created: {path} ({len(data)} tiles, {w}x{h})")


def terrain_01(data, w):
    make_ground(data, w)
    # Start area - simple platforms
    set_rect(data, w, 5, 24, 4, 1, TILE_GROUND)
    set_rect(data, w, 12, 21, 5, 1, TILE_GROUND)
    set_rect(data, w, 20, 18, 4, 1, TILE_GROUND)
    # Troll: spikes hidden below a normal-looking platform
    set_rect(data, w, 28, 18, 6, 1, TILE_GROUND)
    set_rect(data, w, 30, 27, 2, 1, TILE_SPIKES)  # hidden spikes under the platform edge
    # Gap with fake floor
    set_rect(data, w, 38, 22, 5, 1, TILE_GROUND)
    set_rect(data, w, 45, 22, 5, 1, TILE_FAKE)  # looks real, you fall
    set_rect(data, w, 45, 27, 5, 1, TILE_SPIKES)  # spikes below fake floor
    # More platforms
    set_rect(data, w, 52, 19, 4, 1, TILE_GROUND)
    set_rect(data, w, 58, 16, 3, 1, TILE_GROUND)
    # Troll: invisible wall sends you into spikes
    set_rect(data, w, 64, 14, 1, 14, TILE_INVISIBLE)  # invisible wall
    set_rect(data, w, 62, 27, 2, 1, TILE_SPIKES)  # spikes at the base
    # Bridge section
    set_rect(data, w, 68, 20, 8, 1, TILE_GROUND)
    # After bridge: lava pit disguised as safe ground
    set_rect(data, w, 78, 27, 4, 1, TILE_LAVA)
    set_rect(data, w, 78, 20, 4, 1, TILE_FAKE)  # fake floor over lava
    # Final stretch with ice
    set_rect(data, w, 85, 22, 6, 1, TILE_GROUND)
    set_rect(data, w, 93, 20, 5, 1, TILE_ICE)
    set_rect(data, w, 100, 18, 4, 1, TILE_GROUND)
    set_rect(data, w, 106, 15, 4, 1, TILE_GROUND)
    # Victory platform
    set_rect(data, w, 112, 12, 6, 1, TILE_GROUND)
    # Troll: spikes right before goal
    set_rect(data, w, 111, 27, 1, 1, TILE_RED_SPIKES)


def terrain_02(data, w):
    make_ground(data, w)
    # Narrow jumping section
    set_rect(data, w, 4, 24, 2, 1, TILE_GROUND)
    set_rect(data, w, 9, 22, 2, 1, TILE_GROUND)
    set_rect(data, w, 14, 20, 2, 1, TILE_GROUND)
    # Falling section - floor disappears
    set_rect(data, w, 20, 18, 8, 1, TILE_GROUND)
    set_rect(data, w, 20, 24, 8, 1, TILE_FAKE)  # fake floor below (you think it's safe)
    set_rect(data, w, 20, 27, 8, 1, TILE_LAVA)  # lava underneath
    # Spike gauntlet
    set_rect(data, w, 32, 27, 2, 1, TILE_SPIKES)
    set_rect(data, w, 36, 27, 2, 1, TILE_SPIKES)
    set_rect(data, w, 40, 27, 2, 1, TILE_SPIKES)
    set_rect(data, w, 44, 27, 2, 1, TILE_SPIKES)
    set_rect(data, w, 32, 20, 4, 1, TILE_GROUND)
    set_rect(data, w, 38, 18, 4, 1, TILE_GROUND)
    set_rect(data, w, 44, 16, 4, 1, TILE_GROUND)
    # Conveyor belt section
    set_rect(data, w, 52, 22, 8, 1, TILE_CONVEYOR)
    set_rect(data, w, 52, 27, 1, 1, TILE_RED_SPIKES)  # end of conveyor
    # Ice section on narrow platform
    set_rect(data, w, 62, 20, 3, 1, TILE_ICE)
    set_rect(data, w, 67, 18, 3, 1, TILE_ICE)
    set_rect(data, w, 72, 16, 3, 1, TILE_ICE)
    # Troll: safe-looking area that has a crushing drop
    set_rect(data, w, 78, 14, 6, 1, TILE_GROUND)
    set_rect(data, w, 80, 27, 2, 1, TILE_SPIKES)  # spikes in the "safe" gap
    # Vertical climb
    set_rect(data, w, 86, 22, 3, 1, TILE_GROUND)
    set_rect(data, w, 84, 18, 3, 1, TILE_GROUND)
    set_rect(data, w, 88, 14, 3, 1, TILE_GROUND)
    set_rect(data, w, 84, 10, 3, 1, TILE_GROUND)
    # Drop to victory
    set_rect(data, w, 92, 10, 1, 18, TILE_INVISIBLE)  # wall
    set_rect(data, w, 95, 12, 5, 1, TILE_GROUND)
    set_rect(data, w, 102, 14, 5, 1, TILE_GROUND)
    set_rect(data, w, 110, 16, 8, 1, TILE_GROUND)


def terrain_03(data, w):
    make_ground(data, w)
    # Spike maze
    for x in range(2, 20, 3):
        set_tile(data, w, x, 27, TILE_SPIKES)
    set_rect(data, w, 2, 22, 3, 1, TILE_GROUND)
    set_rect(data, w, 8, 20, 3, 1, TILE_GROUND)
    set_rect(data, w, 14, 18, 3, 1, TILE_GROUND)
    # Troll: fake platform over massive spike pit
    set_rect(data, w, 22, 16, 4, 1, TILE_FAKE)
    set_rect(data, w, 22, 27, 6, 1, TILE_RED_SPIKES)
    set_rect(data, w, 24, 27, 2, 1, TILE_LAVA)
    # Bouncy section (no actual bounce, just trolls)
    set_rect(data, w, 30, 20, 3, 1, TILE_GROUND)
    set_rect(data, w, 35, 18, 2, 1, TILE_GROUND)
    set_rect(data, w, 39, 16, 2, 1, TILE_GROUND)
    set_rect(data, w, 43, 27, 3, 1, TILE_SPIKES)  # punish missing
    # Conveyor to spikes
    set_rect(data, w, 48, 22, 10, 1, TILE_CONVEYOR)
    set_rect(data, w, 58, 22, 1, 1, TILE_SPIKES)  # end of conveyor
    # Lava floor section
    set_rect(data, w, 62, 27, 15, 1, TILE_LAVA)
    set_rect(data, w, 62, 20, 3, 1, TILE_GROUND)
    set_rect(data, w, 67, 18, 3, 1, TILE_GROUND)
    set_rect(data, w, 72, 16, 3, 1, TILE_GROUND)
    # Troll: double back
    set_rect(data, w, 80, 14, 4, 1, TILE_GROUND)
    set_rect(data, w, 78, 27, 4, 1, TILE_SPIKES)
    set_rect(data, w, 85, 20, 3, 1, TILE_GROUND)
    # Ice bridge over nothing
    set_rect(data, w, 90, 16, 12, 1, TILE_ICE)
    set_rect(data, w, 90, 27, 12, 1, TILE_LAVA)
    # Victory
    set_rect(data, w, 104, 14, 6, 1, TILE_GROUND)
    set_rect(data, w, 112, 12, 6, 1, TILE_GROUND)
    set_rect(data, w, 111, 27, 1, 1, TILE_RED_SPIKES)


def terrain_04(data, w):
    make_ground(data, w)
    # Immediate troll: spikes right at spawn
    set_rect(data, w, 2, 27, 3, 1, TILE_SPIKES)
    # Safe path
    set_rect(data, w, 6, 24, 3, 1, TILE_GROUND)
    set_rect(data, w, 11, 21, 3, 1, TILE_GROUND)
    # Section: everything looks normal but floor is fake
    set_rect(data, w, 16, 18, 10, 1, TILE_GROUND)
    set_rect(data, w, 16, 24, 3, 1, TILE_GROUND)  # safe start
    set_rect(data, w, 20, 24, 6, 1, TILE_FAKE)  # fake!
    set_rect(data, w, 20, 27, 6, 1, TILE_RED_SPIKES)
    # Spike corridor
    set_rect(data, w, 30, 27, 20, 1, TILE_SPIKES)
    set_rect(data, w, 30, 22, 20, 1, TILE_EMPTY)  # clear above
    set_rect(data, w, 30, 20, 2, 1, TILE_GROUND)
    set_rect(data, w, 34, 18, 2, 1, TILE_GROUND)
    set_rect(data, w, 38, 16, 2, 1, TILE_GROUND)
    set_rect(data, w, 42, 14, 2, 1, TILE_GROUND)
    set_rect(data, w, 46, 12, 2, 1, TILE_GROUND)
    # Ice death slide
    set_rect(data, w, 52, 14, 10, 1, TILE_ICE)
    set_rect(data, w, 52, 27, 10, 1, TILE_LAVA)
    # Conveyor gauntlet
    set_rect(data, w, 64, 20, 8, 1, TILE_CONVEYOR)
    set_rect(data, w, 72, 27, 3, 1, TILE_RED_SPIKES)
    # Fake goal (troll)
    set_rect(data, w, 76, 16, 4, 1, TILE_GROUND)
    set_rect(data, w, 82, 27, 5, 1, TILE_SPIKES)
    set_rect(data, w, 82, 20, 5, 1, TILE_GROUND)
    # Final gauntlet
    set_rect(data, w, 90, 22, 2, 1, TILE_GROUND)
    set_rect(data, w, 94, 20, 2, 1, TILE_GROUND)
    set_rect(data, w, 98, 18, 2, 1, TILE_GROUND)
    set_rect(data, w, 102, 27, 3, 1, TILE_LAVA)
    set_rect(data, w, 102, 16, 6, 1, TILE_GROUND)
    # Victory
    set_rect(data, w, 110, 14, 8, 1, TILE_GROUND)


def terrain_05(data, w):
    make_ground(data, w)
    # Boss arena - open space with traps
    # Spike pillars
    set_rect(data, w, 15, 20, 1, 8, TILE_SPIKES)
    set_rect(data, w, 35, 20, 1, 8, TILE_SPIKES)
    set_rect(data, w, 55, 20, 1, 8, TILE_SPIKES)
    set_rect(data, w, 75, 20, 1, 8, TILE_SPIKES)
    set_rect(data, w, 95, 20, 1, 8, TILE_SPIKES)
    # Safe zones between pillars
    set_rect(data, w, 8, 22, 5, 1, TILE_GROUND)
    set_rect(data, w, 22, 22, 5, 1, TILE_GROUND)
    set_rect(data, w, 42, 22, 5, 1, TILE_GROUND)
    set_rect(data, w, 62, 22, 5, 1, TILE_GROUND)
    set_rect(data, w, 82, 22, 5, 1, TILE_GROUND)
    # Elevated platforms
    set_rect(data, w, 12, 16, 4, 1, TILE_GROUND)
    set_rect(data, w, 30, 14, 4, 1, TILE_GROUND)
    set_rect(data, w, 50, 12, 4, 1, TILE_GROUND)
    set_rect(data, w, 70, 10, 4, 1, TILE_GROUND)
    # Fake victory platform
    set_rect(data, w, 100, 16, 6, 1, TILE_FAKE)
    set_rect(data, w, 100, 27, 6, 1, TILE_RED_SPIKES)
    # Real victory (hidden path)
    set_rect(data, w, 108, 22, 4, 1, TILE_GROUND)
    set_rect(data, w, 112, 20, 6, 1, TILE_GROUND)


enemies_01 = [
    {"type": "player_start", "x": 96, "y": 832},
    {"type": "mold_slime", "x": 400, "y": 800},
    {"type": "mold_slime", "x": 550, "y": 800},
    {"type": "evil_crouton", "x": 900, "y": 800},
    {"type": "crumb_fly", "x": 1200, "y": 600},
    {"type": "stale_cracker", "x": 1600, "y": 800},
    {"type": "evil_crouton", "x": 2000, "y": 800},
    {"type": "mold_slime", "x": 2400, "y": 800},
    {"type": "crumb_fly", "x": 2800, "y": 500},
    {"type": "evil_crouton", "x": 3200, "y": 800},
    {"type": "mold_slime", "x": 3500, "y": 800},
    {"type": "bread_golem", "x": 3600, "y": 700},
    {"type": "toast", "x": 600, "y": 550},
    {"type": "moving_platform", "x": 700, "y": 500, "move_x": 128, "move_y": 0, "speed": 0.03, "width": 96},
    {"type": "crumbling_block", "x": 1440, "y": 576},
    {"type": "crumbling_block", "x": 1472, "y": 576},
    {"type": "crumbling_block", "x": 1504, "y": 576},
    {"type": "disappearing_block", "x": 2600, "y": 640, "appear_time": 90, "disappear_time": 60},
    {"type": "disappearing_block", "x": 2632, "y": 640, "appear_time": 90, "disappear_time": 60},
    {"type": "moving_platform", "x": 3000, "y": 480, "move_x": 0, "move_y": 96, "speed": 0.025, "width": 64},
    {"type": "fake_block", "x": 960, "y": 576},
    {"type": "fake_block", "x": 992, "y": 576},
]

enemies_02 = [
    {"type": "player_start", "x": 96, "y": 832},
    {"type": "evil_crouton", "x": 300, "y": 650},
    {"type": "mold_slime", "x": 500, "y": 800},
    {"type": "crumb_fly", "x": 800, "y": 500},
    {"type": "stale_cracker", "x": 1100, "y": 600},
    {"type": "evil_crouton", "x": 1400, "y": 600},
    {"type": "mold_slime", "x": 1700, "y": 600},
    {"type": "crumb_fly", "x": 2000, "y": 450},
    {"type": "evil_crouton", "x": 2400, "y": 600},
    {"type": "stale_cracker", "x": 2800, "y": 600},
    {"type": "bread_golem", "x": 3200, "y": 600},
    {"type": "croissant", "x": 900, "y": 450},
    {"type": "mold_king", "x": 3500, "y": 600},
    {"type": "moving_platform", "x": 600, "y": 500, "move_x": 160, "move_y": 0, "speed": 0.035, "width": 96},
    {"type": "moving_platform", "x": 1500, "y": 400, "move_x": 0, "move_y": 128, "speed": 0.03, "width": 64},
    {"type": "crumbling_block", "x": 2100, "y": 640},
    {"type": "crumbling_block", "x": 2132, "y": 640},
    {"type": "crumbling_block", "x": 2164, "y": 640},
    {"type": "disappearing_block", "x": 2600, "y": 576, "appear_time": 80, "disappear_time": 50},
    {"type": "disappearing_block", "x": 2632, "y": 576, "appear_time": 80, "disappear_time": 50},
    {"type": "disappearing_block", "x": 2664, "y": 576, "appear_time": 80, "disappear_time": 50},
    {"type": "moving_platform", "x": 3000, "y": 350, "move_x": 128, "move_y": 0, "speed": 0.04, "width": 96},
    {"type": "fake_block", "x": 1000, "y": 700},
    {"type": "fake_block", "x": 1032, "y": 700},
    {"type": "fake_block", "x": 1064, "y": 700},
]

enemies_03 = [
    {"type": "player_start", "x": 96, "y": 832},
    {"type": "evil_crouton", "x": 200, "y": 600},
    {"type": "crumb_fly", "x": 500, "y": 400},
    {"type": "mold_slime", "x": 700, "y": 800},
    {"type": "evil_crouton", "x": 1000, "y": 600},
    {"type": "stale_cracker", "x": 1300, "y": 500},
    {"type": "crumb_fly", "x": 1600, "y": 400},
    {"type": "mold_slime", "x": 1900, "y": 600},
    {"type": "evil_crouton", "x": 2200, "y": 600},
    {"type": "crumb_fly", "x": 2500, "y": 350},
    {"type": "stale_cracker", "x": 2800, "y": 500},
    {"type": "bread_golem", "x": 3100, "y": 600},
    {"type": "mold_king", "x": 3400, "y": 500},
    {"type": "toast", "x": 500, "y": 550},
    {"type": "bagel", "x": 2200, "y": 400},
    {"type": "moving_platform", "x": 400, "y": 500, "move_x": 96, "move_y": 0, "speed": 0.04, "width": 64},
    {"type": "moving_platform", "x": 1800, "y": 400, "move_x": 0, "move_y": 96, "speed": 0.035, "width": 64},
    {"type": "moving_platform", "x": 2700, "y": 350, "move_x": 128, "move_y": 0, "speed": 0.03, "width": 96},
    {"type": "crumbling_block", "x": 1100, "y": 576},
    {"type": "crumbling_block", "x": 1132, "y": 576},
    {"type": "disappearing_block", "x": 2400, "y": 500, "appear_time": 70, "disappear_time": 45},
    {"type": "disappearing_block", "x": 2432, "y": 500, "appear_time": 70, "disappear_time": 45},
    {"type": "fake_block", "x": 1700, "y": 500},
    {"type": "fake_block", "x": 1732, "y": 500},
]

enemies_04 = [
    {"type": "player_start", "x": 96, "y": 832},
    {"type": "crumb_fly", "x": 200, "y": 600},
    {"type": "evil_crouton", "x": 400, "y": 700},
    {"type": "mold_slime", "x": 700, "y": 800},
    {"type": "evil_crouton", "x": 1000, "y": 600},
    {"type": "crumb_fly", "x": 1300, "y": 400},
    {"type": "stale_cracker", "x": 1600, "y": 600},
    {"type": "evil_crouton", "x": 1900, "y": 600},
    {"type": "crumb_fly", "x": 2200, "y": 350},
    {"type": "mold_slime", "x": 2500, "y": 600},
    {"type": "evil_crouton", "x": 2800, "y": 600},
    {"type": "stale_cracker", "x": 3100, "y": 500},
    {"type": "bread_golem", "x": 3400, "y": 500},
    {"type": "mold_king", "x": 3600, "y": 500},
    {"type": "sourdough", "x": 2400, "y": 450},
    {"type": "moving_platform", "x": 500, "y": 450, "move_x": 0, "move_y": 128, "speed": 0.03, "width": 64},
    {"type": "moving_platform", "x": 1200, "y": 350, "move_x": 128, "move_y": 0, "speed": 0.035, "width": 96},
    {"type": "moving_platform", "x": 2000, "y": 400, "move_x": 0, "move_y": 96, "speed": 0.04, "width": 64},
    {"type": "moving_platform", "x": 2900, "y": 300, "move_x": 96, "move_y": 0, "speed": 0.03, "width": 96},
    {"type": "crumbling_block", "x": 1500, "y": 640},
    {"type": "crumbling_block", "x": 1532, "y": 640},
    {"type": "crumbling_block", "x": 1564, "y": 640},
    {"type": "disappearing_block", "x": 2600, "y": 500, "appear_time": 60, "disappear_time": 40},
    {"type": "disappearing_block", "x": 2632, "y": 500, "appear_time": 60, "disappear_time": 40},
    {"type": "disappearing_block", "x": 2664, "y": 500, "appear_time": 60, "disappear_time": 40},
    {"type": "fake_block", "x": 800, "y": 700},
    {"type": "fake_block", "x": 832, "y": 700},
]

enemies_05 = [
    {"type": "player_start", "x": 96, "y": 832},
    {"type": "bread_golem", "x": 500, "y": 800},
    {"type": "evil_crouton", "x": 700, "y": 800},
    {"type": "crumb_fly", "x": 900, "y": 500},
    {"type": "bread_golem", "x": 1200, "y": 800},
    {"type": "mold_slime", "x": 1500, "y": 700},
    {"type": "evil_crouton", "x": 1800, "y": 800},
    {"type": "bread_golem", "x": 2200, "y": 700},
    {"type": "crumb_fly", "x": 2500, "y": 400},
    {"type": "mold_king", "x": 2800, "y": 800},
    {"type": "bread_golem", "x": 3200, "y": 700},
    {"type": "mold_king", "x": 3500, "y": 700},
    {"type": "toast", "x": 300, "y": 650},
    {"type": "croissant", "x": 1100, "y": 550},
    {"type": "bagel", "x": 2000, "y": 400},
    {"type": "sourdough", "x": 2900, "y": 500},
    {"type": "moving_platform", "x": 400, "y": 500, "move_x": 128, "move_y": 0, "speed": 0.04, "width": 96},
    {"type": "moving_platform", "x": 1000, "y": 400, "move_x": 0, "move_y": 96, "speed": 0.035, "width": 64},
    {"type": "moving_platform", "x": 1600, "y": 350, "move_x": 128, "move_y": 0, "speed": 0.03, "width": 96},
    {"type": "moving_platform", "x": 2400, "y": 300, "move_x": 0, "move_y": 128, "speed": 0.04, "width": 64},
    {"type": "moving_platform", "x": 3100, "y": 400, "move_x": 96, "move_y": 0, "speed": 0.045, "width": 96},
    {"type": "crumbling_block", "x": 800, "y": 700},
    {"type": "crumbling_block", "x": 832, "y": 700},
    {"type": "crumbling_block", "x": 2600, "y": 640},
    {"type": "crumbling_block", "x": 2632, "y": 640},
    {"type": "disappearing_block", "x": 1400, "y": 500, "appear_time": 50, "disappear_time": 35},
    {"type": "disappearing_block", "x": 1432, "y": 500, "appear_time": 50, "disappear_time": 35},
    {"type": "disappearing_block", "x": 3000, "y": 400, "appear_time": 60, "disappear_time": 40},
    {"type": "disappearing_block", "x": 3032, "y": 400, "appear_time": 60, "disappear_time": 40},
    {"type": "fake_block", "x": 600, "y": 700},
    {"type": "fake_block", "x": 2300, "y": 600},
    {"type": "fake_block", "x": 2332, "y": 600},
]


print("Generating rage-bait levels...")
make_level("level_01", terrain_01, enemies_01, [96, 832])
make_level("level_02", terrain_02, enemies_02, [96, 832])
make_level("level_03", terrain_03, enemies_03, [96, 832])
make_level("level_04", terrain_04, enemies_04, [96, 832])
make_level("level_05", terrain_05, enemies_05, [96, 832])
print("Done!")
