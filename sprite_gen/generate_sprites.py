from PIL import Image, ImageDraw
import os

SPRITE_DIR = os.path.join("assets", "sprites")
TILE_SIZE = 32


def save_sprite(name, img):
    path = os.path.join(SPRITE_DIR, f"{name}.png")
    img.save(path)


def generate_player():
    for frame in range(4):
        img = Image.new("RGBA", (TILE_SIZE * 2, TILE_SIZE * 2), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        body_color = (220, 190, 150)
        crust = (170, 130, 80)
        offset = 0 if frame < 2 else (2 if frame == 2 else -2)

        draw.ellipse([6, 10 + offset, TILE_SIZE * 2 - 6, TILE_SIZE * 2 - 6], fill=body_color)
        draw.rectangle([8, 22, TILE_SIZE * 2 - 8, TILE_SIZE * 2 - 10], fill=body_color)

        draw.ellipse([8, 6, TILE_SIZE * 2 - 8, 18], fill=(40, 40, 140))
        draw.rectangle([10, 14, TILE_SIZE * 2 - 10, 18], fill=(40, 40, 140))

        draw.polygon([(6, 14), (0, 22), (8, 22)], fill=crust)

        eye_x = TILE_SIZE + 2
        eye_y = 20
        draw.ellipse([eye_x, eye_y, eye_x + 6, eye_y + 6], fill=(255, 255, 255))
        draw.ellipse([eye_x + 2, eye_y + 1, eye_x + 5, eye_y + 5], fill=(0, 0, 0))

        leg_y = TILE_SIZE * 2 - 10 + (3 if frame % 2 == 0 else -1)
        draw.rectangle([14, TILE_SIZE * 2 - 14, 20, leg_y], fill=crust)
        draw.rectangle([TILE_SIZE * 2 - 20, TILE_SIZE * 2 - 14, TILE_SIZE * 2 - 14, leg_y], fill=crust)

        draw.rectangle([TILE_SIZE * 2 - 8, 24, TILE_SIZE * 2 + 8, 28], fill=(180, 180, 180))
        draw.rectangle([TILE_SIZE * 2 + 6, 22, TILE_SIZE * 2 + 12, 30], fill=(200, 200, 200))

        save_sprite(f"player_{frame}", img)
    save_sprite("player", Image.open(os.path.join(SPRITE_DIR, "player_0.png")))


def generate_mold_slime():
    for frame in range(4):
        img = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        squash = 2 if frame % 2 == 0 else 0
        draw.ellipse([2, 8 + squash, TILE_SIZE - 2, TILE_SIZE - 2], fill=(50, 180, 50))
        draw.ellipse([4, 4 + squash, TILE_SIZE - 4, 16], fill=(60, 200, 60))
        draw.ellipse([8, 12, 12, 16], fill=(255, 255, 255))
        draw.ellipse([9, 13, 11, 15], fill=(0, 0, 0))
        draw.ellipse([TILE_SIZE - 12, 12, TILE_SIZE - 8, 16], fill=(255, 255, 255))
        draw.ellipse([TILE_SIZE - 11, 13, TILE_SIZE - 9, 15], fill=(0, 0, 0))
        for i in range(3):
            sx = 6 + i * 8
            draw.ellipse([sx, 4, sx + 3, 7], fill=(40, 140, 40))
        save_sprite(f"mold_slime_{frame}", img)
    save_sprite("mold_slime", Image.open(os.path.join(SPRITE_DIR, "mold_slime_0.png")))


def generate_stale_cracker():
    img = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([2, 2, TILE_SIZE - 2, TILE_SIZE - 2], fill=(190, 160, 110))
    draw.rectangle([4, 4, TILE_SIZE - 4, TILE_SIZE - 4], fill=(170, 140, 90))
    draw.rectangle([3, 3, TILE_SIZE - 3, TILE_SIZE - 3], outline=(140, 110, 70), width=1)
    draw.line([6, 6, TILE_SIZE - 8, TILE_SIZE - 8], fill=(100, 80, 50), width=2)
    draw.line([TILE_SIZE - 8, 8, 8, TILE_SIZE - 8], fill=(100, 80, 50), width=1)
    draw.ellipse([10, 10, 14, 14], fill=(255, 255, 255))
    draw.ellipse([11, 11, 13, 13], fill=(0, 0, 0))
    draw.ellipse([TILE_SIZE - 14, 10, TILE_SIZE - 10, 14], fill=(255, 255, 255))
    draw.ellipse([TILE_SIZE - 13, 11, TILE_SIZE - 11, 13], fill=(0, 0, 0))
    save_sprite("stale_cracker", img)


def generate_evil_crouton():
    for frame in range(4):
        img = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rectangle([4, 4, TILE_SIZE - 4, TILE_SIZE - 4], fill=(170, 110, 45))
        draw.rectangle([3, 3, TILE_SIZE - 3, TILE_SIZE - 3], outline=(130, 80, 30), width=1)
        eye_y = 10 + (1 if frame % 2 == 0 else 0)
        draw.ellipse([8, eye_y, 14, eye_y + 6], fill=(255, 30, 30))
        draw.ellipse([9, eye_y + 1, 13, eye_y + 5], fill=(255, 0, 0))
        draw.ellipse([TILE_SIZE - 14, eye_y, TILE_SIZE - 8, eye_y + 6], fill=(255, 30, 30))
        draw.ellipse([TILE_SIZE - 13, eye_y + 1, TILE_SIZE - 9, eye_y + 5], fill=(255, 0, 0))
        save_sprite(f"evil_crouton_{frame}", img)
    save_sprite("evil_crouton", Image.open(os.path.join(SPRITE_DIR, "evil_crouton_0.png")))


def generate_bread_golem():
    for frame in range(2):
        img = Image.new("RGBA", (TILE_SIZE * 2, TILE_SIZE * 2), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        wobble = 2 if frame == 1 else 0
        draw.rectangle([8, 8 + wobble, TILE_SIZE * 2 - 8, TILE_SIZE * 2 - 8], fill=(130, 90, 45))
        draw.rectangle([6, 6 + wobble, TILE_SIZE * 2 - 6, TILE_SIZE * 2 - 6], outline=(100, 65, 30), width=2)
        draw.rectangle([0, 20, 12, TILE_SIZE + 10], fill=(130, 90, 45))
        draw.rectangle([TILE_SIZE * 2 - 12, 20, TILE_SIZE * 2, TILE_SIZE + 10], fill=(130, 90, 45))
        draw.ellipse([14, 18, 30, 30], fill=(255, 40, 40))
        draw.ellipse([16, 20, 28, 28], fill=(200, 0, 0))
        draw.ellipse([TILE_SIZE * 2 - 30, 18, TILE_SIZE * 2 - 14, 30], fill=(255, 40, 40))
        draw.ellipse([TILE_SIZE * 2 - 28, 20, TILE_SIZE * 2 - 16, 28], fill=(200, 0, 0))
        for i in range(5):
            cx = 16 + i * 12
            draw.line([cx, TILE_SIZE * 2 - 14, cx + 4, TILE_SIZE * 2 - 8], fill=(100, 65, 30), width=1)
        save_sprite(f"bread_golem_{frame}", img)
    save_sprite("bread_golem", Image.open(os.path.join(SPRITE_DIR, "bread_golem_0.png")))


def generate_mold_king():
    for frame in range(2):
        img = Image.new("RGBA", (TILE_SIZE * 2, TILE_SIZE * 2), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        wobble = 2 if frame == 1 else 0
        draw.rectangle([6, 6 + wobble, TILE_SIZE * 2 - 6, TILE_SIZE * 2 - 6], fill=(30, 130, 30))
        draw.rectangle([4, 4 + wobble, TILE_SIZE * 2 - 4, TILE_SIZE * 2 - 4], outline=(20, 90, 20), width=2)
        draw.rectangle([0, 18, 10, TILE_SIZE + 8], fill=(30, 130, 30))
        draw.rectangle([TILE_SIZE * 2 - 10, 18, TILE_SIZE * 2, TILE_SIZE + 8], fill=(30, 130, 30))
        draw.rectangle([12, 4, TILE_SIZE * 2 - 12, 12], fill=(255, 215, 0))
        draw.polygon([(TILE_SIZE - 4, 0), (TILE_SIZE, 8), (TILE_SIZE + 4, 0)], fill=(255, 215, 0))
        draw.polygon([(TILE_SIZE - 12, 2), (TILE_SIZE - 8, 10), (TILE_SIZE - 4, 2)], fill=(255, 215, 0))
        draw.polygon([(TILE_SIZE + 4, 2), (TILE_SIZE + 8, 10), (TILE_SIZE + 12, 2)], fill=(255, 215, 0))
        draw.ellipse([14, 16, 28, 28], fill=(255, 30, 30))
        draw.ellipse([TILE_SIZE * 2 - 28, 16, TILE_SIZE * 2 - 14, 28], fill=(255, 30, 30))
        save_sprite(f"mold_king_{frame}", img)
    save_sprite("mold_king", Image.open(os.path.join(SPRITE_DIR, "mold_king_0.png")))


def generate_crumb_fly():
    for frame in range(4):
        img = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        body_x, body_y = TILE_SIZE // 2, TILE_SIZE // 2
        draw.ellipse([body_x - 6, body_y - 4, body_x + 6, body_y + 4], fill=(110, 85, 60))
        wing_y = body_y - 4 + (-4 if frame % 2 == 0 else 2)
        draw.ellipse([body_x - 12, wing_y - 4, body_x - 2, wing_y + 4], fill=(200, 200, 220, 160))
        draw.ellipse([body_x + 2, wing_y - 4, body_x + 12, wing_y + 4], fill=(200, 200, 220, 160))
        draw.ellipse([body_x - 3, body_y - 3, body_x - 1, body_y - 1], fill=(255, 50, 50))
        draw.ellipse([body_x + 1, body_y - 3, body_x + 3, body_y - 1], fill=(255, 50, 50))
        save_sprite(f"crumb_fly_{frame}", img)
    save_sprite("crumb_fly", Image.open(os.path.join(SPRITE_DIR, "crumb_fly_0.png")))


def generate_powerup(name, color, label):
    for frame in range(4):
        img = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        bob = int(frame % 2) * 2
        draw.ellipse([4, 4 + bob, TILE_SIZE - 4, TILE_SIZE - 4 + bob], fill=color)
        highlight = tuple(min(255, c + 60) for c in color)
        draw.ellipse([8, 6 + bob, 16, 14 + bob], fill=highlight)
        save_sprite(f"powerup_{name}_{frame}", img)
    save_sprite(f"powerup_{name}", Image.open(os.path.join(SPRITE_DIR, f"powerup_{name}_0.png")))


def generate_tiles():
    # Ground tile with gradient
    img = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, TILE_SIZE, TILE_SIZE], fill=(100, 65, 35))
    draw.rectangle([0, 0, TILE_SIZE, 6], fill=(80, 120, 50))
    draw.rectangle([0, 6, TILE_SIZE, 8], fill=(60, 100, 40))
    for i in range(4):
        x = 4 + i * 8
        draw.rectangle([x, 10, x + 4, TILE_SIZE - 4], fill=(90, 55, 28))
    draw.rectangle([0, 0, TILE_SIZE - 1, TILE_SIZE - 1], outline=(70, 45, 22), width=1)
    save_sprite("tile_ground_1", img)

    img2 = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
    draw2 = ImageDraw.Draw(img2)
    draw2.rectangle([0, 0, TILE_SIZE, TILE_SIZE], fill=(85, 55, 30))
    draw2.rectangle([0, 0, TILE_SIZE - 1, TILE_SIZE - 1], outline=(65, 40, 20), width=1)
    save_sprite("tile_ground_2", img2)

    # Spikes
    img3 = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
    draw3 = ImageDraw.Draw(img3)
    for i in range(4):
        x = i * 8
        draw3.polygon([(x, TILE_SIZE), (x + 4, 4), (x + 8, TILE_SIZE)], fill=(200, 200, 210))
        draw3.polygon([(x + 2, TILE_SIZE), (x + 4, 8), (x + 6, TILE_SIZE)], fill=(230, 230, 240))
    save_sprite("tile_spikes", img3)

    # Lava
    img4 = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
    draw4 = ImageDraw.Draw(img4)
    draw4.rectangle([0, 0, TILE_SIZE, TILE_SIZE], fill=(200, 80, 0))
    draw4.rectangle([0, 0, TILE_SIZE, 8], fill=(255, 120, 20))
    draw4.rectangle([0, 8, TILE_SIZE, 16], fill=(255, 160, 40))
    draw4.rectangle([0, 0, TILE_SIZE - 1, TILE_SIZE - 1], outline=(180, 60, 0), width=1)
    save_sprite("tile_lava", img4)

    # Ice
    img5 = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
    draw5 = ImageDraw.Draw(img5)
    draw5.rectangle([0, 0, TILE_SIZE, TILE_SIZE], fill=(160, 210, 255))
    draw5.rectangle([0, 0, TILE_SIZE - 1, TILE_SIZE - 1], outline=(120, 180, 230), width=1)
    draw5.line([4, 4, 12, 12], fill=(200, 230, 255), width=1)
    draw5.line([20, 8, 28, 16], fill=(200, 230, 255), width=1)
    draw5.line([8, 20, 16, 28], fill=(200, 230, 255), width=1)
    save_sprite("tile_ice", img5)


def main():
    os.makedirs(SPRITE_DIR, exist_ok=True)
    print("Generating enhanced sprites...")
    generate_player()
    generate_mold_slime()
    generate_stale_cracker()
    generate_evil_crouton()
    generate_bread_golem()
    generate_mold_king()
    generate_crumb_fly()
    generate_powerup("toast", (190, 130, 65), "T")
    generate_powerup("croissant", (225, 195, 145), "C")
    generate_powerup("bagel", (205, 165, 105), "B")
    generate_powerup("sourdough", (165, 145, 105), "S")
    generate_tiles()
    print("Done!")


if __name__ == "__main__":
    main()
