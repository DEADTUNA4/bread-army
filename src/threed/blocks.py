from ursina import *
from src.threed.settings import *
import math, random


class MovingPlatform(Entity):
    def __init__(self, pos, axis="x", range=4, speed=0.03):
        super().__init__(
            model="cube",
            color=color.hex("#A0A0A0"),
            position=pos,
            scale=(2, 0.5, 2),
            collider="box",
        )
        self.home = Vec3(pos.x, pos.y, pos.z)
        self.axis = axis
        self.range = range
        self.speed = speed
        self.phase = random.random() * 360

    def update(self):
        t = math.sin(time.time * self.speed * 100 + self.phase)
        offset = t * self.range
        if self.axis == "x":
            self.x = self.home.x + offset
        elif self.axis == "z":
            self.z = self.home.z + offset
        elif self.axis == "y":
            self.y = self.home.y + offset + self.range


class CrumblingBlock(Entity):
    def __init__(self, pos):
        super().__init__(
            model="cube",
            color=color.hex("#8B7355"),
            position=pos,
            scale=(1, 0.5, 1),
            collider="box",
        )
        self.home = Vec3(pos.x, pos.y, pos.z)
        self.shaking = False
        self.shake_timer = 0
        self.crumble_timer = 0
        self.respawn_timer = 0

    def on_step(self, player):
        if not self.shaking and self.shake_timer == 0 and self.crumble_timer == 0:
            self.shaking = True
            self.shake_timer = 30

    def update(self):
        if self.shaking and self.shake_timer > 0:
            self.shake_timer -= 1
            self.x = self.home.x + random.uniform(-0.1, 0.1)
            self.z = self.home.z + random.uniform(-0.1, 0.1)
            if self.shake_timer <= 0:
                self.crumble_timer = 120
                self.collider.enabled = False

        if self.crumble_timer > 0:
            self.crumble_timer -= 1
            self.y -= 0.05
            if self.crumble_timer <= 0:
                self.visible = False
                self.respawn_timer = 180

        if self.respawn_timer > 0:
            self.respawn_timer -= 1
            if self.respawn_timer <= 0:
                self.position = self.home
                self.shaking = False
                self.shake_timer = 0
                self.crumble_timer = 0
                self.respawn_timer = 0
                self.visible = True
                self.collider.enabled = True


class DisappearingBlock(Entity):
    def __init__(self, pos, interval=60):
        super().__init__(
            model="cube",
            color=color.hex("#FFD700"),
            position=pos,
            scale=(1, 0.5, 1),
            collider="box",
        )
        self.interval = interval
        self.timer = 0
        self.visible_state = True

    def update(self):
        self.timer += 1
        if self.timer >= self.interval:
            self.timer = 0
            self.visible_state = not self.visible_state
            self.visible = self.visible_state
            self.collider.enabled = self.visible_state


class FakeBlock(Entity):
    def __init__(self, pos):
        super().__init__(
            model="cube",
            color=color.hex("#A0522D"),
            position=pos,
            scale=(1, 0.5, 1),
            collider="box",
        )
        self.activated = False
        self.fall_speed = 0

    def on_step(self, player):
        if not self.activated:
            self.activated = True
            self.color = color.hex("#8B0000")

    def update(self):
        if self.activated:
            self.fall_speed -= 20 * time.dt
            self.y += self.fall_speed * time.dt
            if self.y < -20:
                destroy(self)
