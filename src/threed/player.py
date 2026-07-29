from ursina import *
from src.threed.settings import *

POWERUP_COLORS = {
    "toast": color.hex("#b4783c"),
    "croissant": color.hex("#dcbe8c"),
    "bagel": color.hex("#c8a064"),
    "sourdough": color.hex("#a08c64"),
}


class Player(Entity):
    def __init__(self, spawn):
        super().__init__(
            model="cube",
            color=TAN,
            position=spawn,
            scale=(0.8, 1.2, 0.8),
            collider="box",
        )
        self.speed = 5
        self.jump_height = 10
        self.health = 1
        self.max_health = 1
        self.alive = True
        self.dying = False
        self.death_timer = 0
        self.grounded = False
        self.vy = 0
        self.attack_cooldown = 0
        self.powerup = None
        self.facing = 1

        hat = Entity(
            parent=self,
            model="cube",
            color=color.hex("#323296"),
            scale=(1.1, 0.3, 1.1),
            position=(0, 0.8, 0),
        )
        Entity(
            parent=self,
            model="cube",
            color=color.hex("#323296"),
            scale=(1.4, 0.1, 1.4),
            position=(0, 0.65, 0),
        )

    def handle_input(self):
        if self.dying or not self.alive:
            return

        move = Vec3(0, 0, 0)
        if held_keys["a"] or held_keys["left"]:
            move.x -= 1
            self.facing = -1
        if held_keys["d"] or held_keys["right"]:
            move.x += 1
            self.facing = 1

        if move.length() > 0:
            move = move.normalized()
            cam_right = camera.right * move.x
            self.x += cam_right.x * self.speed * time.dt
            self.z += cam_right.z * self.speed * time.dt
            self.look_at(self.world_position + Vec3(cam_right.x, 0, cam_right.z))

        if (held_keys["space"] or held_keys["w"] or held_keys["up"]) and self.grounded:
            self.vy = self.jump_height
            self.grounded = False

        if mouse.left and self.attack_cooldown <= 0:
            self.attack_cooldown = 15

    def update(self):
        if self.dying:
            self.death_timer -= 1
            self.vy -= 20 * time.dt
            self.y += self.vy * time.dt
            self.rotation_x += 5
            self.rotation_z += 3
            if self.death_timer <= 0:
                self.alive = False
            return

        # Gravity
        self.vy -= 30 * time.dt
        self.y += self.vy * time.dt

        # Ground check via raycast
        hit = raycast(
            self.world_position + Vec3(0, 0.1, 0),
            Vec3(0, -1, 0),
            distance=0.5,
        )
        self.grounded = hit.hit and self.vy <= 0
        if self.grounded:
            self.vy = 0
            self.y = hit.world_point.y + 0.5

        # Attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def attack(self):
        self.attack_cooldown = 15

    def take_damage(self, amount=1):
        if self.dying or not self.alive:
            return False
        self.health -= amount
        self.flash_red()
        if self.health <= 0:
            self.die()
        return True

    def flash_red(self):
        self.color = color.red
        invoke(lambda: self._restore_color(), delay=0.1)

    def _restore_color(self):
        if not self.dying:
            self.color = POWERUP_COLORS.get(self.powerup, TAN)

    def die(self):
        self.dying = True
        self.death_timer = 90
        self.vy = 8

    def set_powerup(self, powerup_type):
        self.powerup = powerup_type
        self.color = POWERUP_COLORS.get(powerup_type, TAN)

    def heal(self, amount=1):
        self.health = min(self.health + amount, self.max_health)
