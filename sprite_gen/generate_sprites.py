from PIL import Image, ImageDraw
import os

SPRITE_DIR = os.path.join("assets", "sprites")
TILE_SIZE = 32


def save_sprite(name, img):
    path = os.path.join(SPRITE_DIR, f"{name}.png")
    img.save(path)
    print(f"  Saved: {path}")


def generate_player():
    img = Image.new("RGBA", (TILE_SIZE * 2, TILE_SIZE * 2), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    body_color = (210, 180, 140)
    crust_color = (160, 120, 70)

    draw.ellipse([4, 8, TILE_SIZE * 2 - 4, TILE_SIZE * 2 - 8], fill=body_color)
    draw.rectangle([6, 20, TILE_SIZE * 2 - 6, TILE_SIZE * 2 - 12], fill=body_color)
    draw.ellipse([6, 4, TILE_SIZE * 2 - 6, 14], fill=(50, 50, 150))

    draw.polygon([(4, 12), (0, 20), (6, 20)], fill=crust_color)
    draw.ellipse([TILE_SIZE - 4, 16, TILE_SIZE + 4, 24], fill=(0, 0, 0))
    save_sprite("player", img)


def generate_mold_slime():
    img = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([2, 8, TILE_SIZE - 2, TILE_SIZE - 2], fill=(50, 180, 50))
    draw.ellipse([4, 4, TILE_SIZE - 4, 14], fill=(60, 200, 60))
    draw.ellipse([8, 10, 12, 14], fill=(0, 0, 0))
    draw.ellipse([TILE_SIZE - 12, 10, TILE_SIZE - 8, 14], fill=(0, 0, 0))
    save_sprite("mold_slime", img)


def generate_stale_cracker():
    img = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([2, 2, TILE_SIZE - 2, TILE_SIZE - 2], fill=(180, 150, 100))
    draw.rectangle([4, 4, TILE_SIZE - 4, TILE_SIZE - 4], fill=(160, 130, 80))
    draw.line([6, 6, TILE_SIZE - 6, TILE_SIZE - 6], fill=(100, 80, 50), width=2)
    draw.line([TILE_SIZE - 6, 6, 6, TILE_SIZE - 6], fill=(100, 80, 50), width=2)
    save_sprite("stale_cracker", img)


def generate_evil_crouton():
    img = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([4, 4, TILE_SIZE - 4, TILE_SIZE - 4], fill=(160, 100, 40))
    draw.ellipse([8, 10, 12, 14], fill=(255, 0, 0))
    draw.ellipse([TILE_SIZE - 12, 10, TILE_SIZE - 8, 14], fill=(255, 0, 0))
    save_sprite("evil_crouton", img)


def generate_bread_golem():
    img = Image.new("RGBA", (TILE_SIZE * 2, TILE_SIZE * 2), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([8, 8, TILE_SIZE * 2 - 8, TILE_SIZE * 2 - 8], fill=(120, 80, 40))
    draw.rectangle([0, 20, 8, TILE_SIZE], fill=(120, 80, 40))
    draw.rectangle([TILE_SIZE * 2 - 8, 20, TILE_SIZE * 2, TILE_SIZE], fill=(120, 80, 40))
    draw.rectangle([12, 16, 28, 28], fill=(255, 0, 0))
    draw.rectangle([TILE_SIZE * 2 - 28, 16, TILE_SIZE * 2 - 12, 28], fill=(255, 0, 0))
    save_sprite("bread_golem", img)


def generate_powerup(name, color, label):
    img = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([4, 4, TILE_SIZE - 4, TILE_SIZE - 4], fill=color)
    draw.ellipse([6, 6, TILE_SIZE - 6, TILE_SIZE - 6], fill=(255, 255, 255, 60))
    save_sprite(f"powerup_{name}", img)


def generate_tiles():
    tile_colors = {
        "ground_1": (100, 60, 30),
        "ground_2": (80, 50, 20),
        "platform": (120, 100, 60),
        "grass": (60, 120, 60),
    }
    for name, color in tile_colors.items():
        img = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (*color, 255))
        save_sprite(f"tile_{name}", img)


def main():
    os.makedirs(SPRITE_DIR, exist_ok=True)
    print("Generating sprites...")
    generate_player()
    generate_mold_slime()
    generate_stale_cracker()
    generate_evil_crouton()
    generate_bread_golem()
    generate_powerup("toast", (180, 120, 60), "T")
    generate_powerup("croissant", (220, 190, 140), "C")
    generate_powerup("bagel", (200, 160, 100), "B")
    generate_powerup("sourdough", (160, 140, 100), "S")
    generate_tiles()
    print("Done!")


if __name__ == "__main__":
    main()
