import pygame
import os


class AssetManager:
    def __init__(self):
        self.sprites = {}
        self.sounds = {}
        self.fonts = {}

    def load_sprite(self, name, path):
        full_path = os.path.join("assets", "sprites", path)
        if os.path.exists(full_path):
            self.sprites[name] = pygame.image.load(full_path).convert_alpha()
        else:
            self.sprites[name] = None

    def load_sound(self, name, path):
        full_path = os.path.join("assets", "sounds", path)
        if os.path.exists(full_path):
            self.sounds[name] = pygame.mixer.Sound(full_path)

    def get_sprite(self, name):
        return self.sprites.get(name)

    def get_sound(self, name):
        return self.sounds.get(name)

    def play_sound(self, name):
        sound = self.get_sound(name)
        if sound:
            sound.play()
