import pygame
import json
import os
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, TAN, GOLD, RED, WHITE, GRAY
from src.engine.state import State

CONTROLS_FILE = "controls.json"

ACTION_NAMES = {
    "left": "Move Left",
    "right": "Move Right",
    "jump": "Jump",
    "attack": "Attack",
    "pause": "Pause",
}

KEY_NAMES = {
    "K_LEFT": "Left",
    "K_RIGHT": "Right",
    "K_UP": "Up",
    "K_DOWN": "Down",
    "K_SPACE": "Space",
    "K_a": "A",
    "K_b": "B",
    "K_c": "C",
    "K_d": "D",
    "K_e": "E",
    "K_f": "F",
    "K_g": "G",
    "K_h": "H",
    "K_i": "I",
    "K_j": "J",
    "K_k": "K",
    "K_l": "L",
    "K_m": "M",
    "K_n": "N",
    "K_o": "O",
    "K_p": "P",
    "K_q": "Q",
    "K_r": "R",
    "K_s": "S",
    "K_t": "T",
    "K_u": "U",
    "K_v": "V",
    "K_w": "W",
    "K_x": "X",
    "K_y": "Y",
    "K_z": "Z",
    "K_RETURN": "Enter",
    "K_BACKSPACE": "Back",
    "K_TAB": "Tab",
    "K_LSHIFT": "LShift",
    "K_RSHIFT": "RShift",
    "K_1": "1",
    "K_2": "2",
    "K_3": "3",
    "K_4": "4",
    "K_5": "5",
    "K_6": "6",
    "K_7": "7",
    "K_8": "8",
    "K_9": "9",
    "K_0": "0",
}


def load_controls():
    defaults = {
        "left": ["K_LEFT", "K_a"],
        "right": ["K_RIGHT", "K_d"],
        "jump": ["K_SPACE", "K_UP", "K_w"],
        "attack": ["K_f", "K_e"],
        "pause": ["K_ESCAPE"],
    }
    if os.path.exists(CONTROLS_FILE):
        try:
            with open(CONTROLS_FILE, "r") as f:
                data = json.load(f)
            for key in defaults:
                if key not in data:
                    data[key] = defaults[key]
            return data
        except Exception:
            pass
    return defaults


def save_controls(controls):
    with open(CONTROLS_FILE, "w") as f:
        json.dump(controls, f, indent=2)


class SettingsMenu(State):
    def __init__(self, game):
        super().__init__(game)
        self.controls = load_controls()
        self.selected_action = 0
        self.rebinding = False
        self.rebind_action = None
        self.rebind_index = 0
        self.actions = ["left", "right", "jump", "attack", "pause"]
        self.return_to = "main_menu"
        self.flash_timer = 0

    def set_return(self, state_name):
        self.return_to = state_name

    def enter(self):
        self.controls = load_controls()
        self.rebinding = False
        self.flash_timer = 0

    def exit(self):
        pass

    def handle_event(self, event):
        if self.flash_timer > 0:
            self.flash_timer -= 1
            return

        if event.type == pygame.KEYDOWN:
            if self.rebinding:
                key_name = pygame.key.name(event.key).upper()
                key_name = "K_" + key_name if not key_name.startswith("K_") else key_name
                if event.key == pygame.K_ESCAPE:
                    self.rebinding = False
                    return
                action = self.actions[self.selected_action]
                self.controls[action][self.rebind_index] = key_name
                save_controls(self.controls)
                self.rebinding = False
                self.flash_timer = 15
                return

            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected_action = (self.selected_action - 1) % (len(self.actions) + 1)
                self.rebind_index = 0
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected_action = (self.selected_action + 1) % (len(self.actions) + 1)
                self.rebind_index = 0
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                action = self.actions[self.selected_action]
                self.rebind_index = max(0, self.rebind_index - 1)
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                action = self.actions[self.selected_action]
                self.rebind_index = min(len(self.controls[action]) - 1, self.rebind_index + 1)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.selected_action == len(self.actions):
                    self.game.change_state(self.return_to)
                else:
                    action = self.actions[self.selected_action]
                    if len(self.controls[action]) < 3:
                        self.controls[action].append("K_SPACE")
                        save_controls(self.controls)
                    self.rebinding = True
            elif event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                if self.selected_action < len(self.actions):
                    action = self.actions[self.selected_action]
                    if len(self.controls[action]) > 1:
                        self.controls[action].pop(self.rebind_index)
                        self.rebind_index = min(self.rebind_index, len(self.controls[action]) - 1)
                        save_controls(self.controls)

    def update(self, dt):
        pass

    def render(self, surface):
        surface.fill((25, 15, 10))

        title_font = pygame.font.Font(None, 56)
        title = title_font.render("SETTINGS", True, GOLD)
        surface.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 50)))

        ctrl_title = pygame.font.Font(None, 28)
        surface.blit(ctrl_title.render("CONTROLS", True, TAN), ctrl_title.get_rect(center=(WINDOW_WIDTH // 2, 100)))

        action_font = pygame.font.Font(None, 28)
        key_font = pygame.font.Font(None, 24)

        y = 150
        for i, action in enumerate(self.actions):
            is_selected = (i == self.selected_action)
            prefix = "> " if is_selected else "  "
            name_text = prefix + ACTION_NAMES[action]
            color = GOLD if is_selected else TAN
            surface.blit(action_font.render(name_text, True, color), (100, y))

            keys = self.controls.get(action, [])
            key_str = " + ".join([KEY_NAMES.get(k, k) for k in keys])
            key_color = RED if (is_selected and self.rebinding) else GRAY
            surface.blit(key_font.render(key_str, True, key_color), (450, y + 4))
            y += 40

        y += 20
        is_back = (self.selected_action == len(self.actions))
        back_prefix = "> " if is_back else "  "
        back_color = GOLD if is_back else TAN
        surface.blit(action_font.render(back_prefix + "Back", True, back_color), (100, y))

        if self.rebinding:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            surface.blit(overlay, (0, 0))

            prompt_font = pygame.font.Font(None, 40)
            prompt = prompt_font.render("Press a key...", True, GOLD)
            surface.blit(prompt, prompt.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)))

            hint_font = pygame.font.Font(None, 24)
            hint = hint_font.render("Press ESC to cancel", True, GRAY)
            surface.blit(hint, hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40)))

        tip_font = pygame.font.Font(None, 18)
        tip1 = tip_font.render("UP/DOWN: navigate  |  ENTER: rebind  |  BACKSPACE: remove key", True, (100, 100, 100))
        surface.blit(tip1, tip1.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30)))
