from ursina import *
from src.threed.settings import *


class HUD:
    def __init__(self):
        self.health_text = Text(
            text="HP: 1/1",
            position=(-0.85, 0.45),
            scale=1.5,
            color=color.red,
        )
        self.score_text = Text(
            text="Score: 0",
            position=(0.85, 0.45, 0),
            origin=(1, 0),
            scale=1.2,
            color=color.white,
        )
        self.death_text = Text(
            text="",
            position=(0.85, 0.4, 0),
            origin=(1, 0),
            scale=1,
            color=color.hex("#FF6464"),
        )
        self.level_text = Text(
            text="Level 1",
            position=(0.85, 0.35, 0),
            origin=(1, 0),
            scale=1,
            color=color.gray,
        )
        self.powerup_text = Text(
            text="",
            position=(-0.85, 0.4, 0),
            scale=1,
            color=GOLD,
        )
        self.rage_text = Text(
            text="",
            position=(0, 0.2, 0),
            origin=(0, 0),
            scale=2,
            color=color.red,
        )
        self.hide()

    def update(self, score=0, deaths=0, level=0, health=1, powerup=None, rage="", rage_timer=0):
        self.health_text.text = f"HP: {'♥' * health}{'♡' * (1 - health)}"
        self.score_text.text = f"Score: {score}"
        self.death_text.text = f"Deaths: {deaths}" if deaths > 0 else ""
        self.level_text.text = f"Level {level + 1}"
        self.powerup_text.text = f"{powerup.upper()}" if powerup else ""
        if rage_timer > 0 and rage:
            self.rage_text.text = rage
        else:
            self.rage_text.text = ""

    def show(self):
        for attr in ["health_text", "score_text", "death_text", "level_text", "powerup_text", "rage_text"]:
            getattr(self, attr).visible = True

    def hide(self):
        for attr in ["health_text", "score_text", "death_text", "level_text", "powerup_text", "rage_text"]:
            getattr(self, attr).visible = False


menu_buttons = []
menu_texts = []
menu_active = False


def clear_menu():
    global menu_buttons, menu_texts
    for b in menu_buttons:
        destroy(b)
    for t in menu_texts:
        destroy(t)
    menu_buttons.clear()
    menu_texts.clear()


def show_main_menu():
    global menu_active
    clear_menu()
    menu_active = True

    title = Text(
        text="BREAD ARMY 3D",
        position=(0, 0.3, 0),
        origin=(0, 0),
        scale=5,
        color=GOLD,
    )
    menu_texts.append(title)

    subtitle = Text(
        text="Prepare to suffer.",
        position=(0, 0.2, 0),
        origin=(0, 0),
        scale=2,
        color=DARK_RED,
    )
    menu_texts.append(subtitle)

    version = Text(
        text=VERSION,
        position=(0, -0.4, 0),
        origin=(0, 0),
        scale=1,
        color=color.gray,
    )
    menu_texts.append(version)

    def start_game():
        clear_menu()
        menu_active = False
        from src.threed.game import game_manager
        game_manager.start_game()

    def quit_game():
        application.quit()

    btn_start = Button(
        text="Start Game",
        position=(0, 0.05, 0),
        scale=(0.3, 0.08),
        color=color.hex("#8B6914"),
        text_color=color.white,
        on_click=start_game,
    )
    menu_buttons.append(btn_start)

    btn_quit = Button(
        text="Quit",
        position=(0, -0.05, 0),
        scale=(0.3, 0.08),
        color=color.hex("#8B0000"),
        text_color=color.white,
        on_click=quit_game,
    )
    menu_buttons.append(btn_quit)


def show_game_over(score, deaths, quote=""):
    clear_menu()

    title = Text(
        text="YOU DIED",
        position=(0, 0.3, 0),
        origin=(0, 0),
        scale=4,
        color=DARK_RED,
    )
    menu_texts.append(title)

    if quote:
        qt = Text(
            text=quote,
            position=(0, 0.2, 0),
            origin=(0, 0),
            scale=2,
            color=color.red,
        )
        menu_texts.append(qt)

    score_t = Text(
        text=f"Score: {score}",
        position=(0, 0.1, 0),
        origin=(0, 0),
        scale=1.5,
        color=GOLD,
    )
    menu_texts.append(score_t)

    death_t = Text(
        text=f"Deaths: {deaths}",
        position=(0, 0.05, 0),
        origin=(0, 0),
        scale=1.5,
        color=color.hex("#FF6464"),
    )
    menu_texts.append(death_t)

    def retry():
        clear_menu()
        from src.threed.game import game_manager
        game_manager.restart_level()

    def to_menu():
        clear_menu()
        from src.threed.game import game_manager
        show_main_menu()

    btn_retry = Button(
        text="Try Again",
        position=(0, -0.05, 0),
        scale=(0.3, 0.08),
        color=color.hex("#8B6914"),
        text_color=color.white,
        on_click=retry,
    )
    menu_buttons.append(btn_retry)

    btn_menu = Button(
        text="Main Menu",
        position=(0, -0.15, 0),
        scale=(0.3, 0.08),
        color=color.hex("#555555"),
        text_color=color.white,
        on_click=to_menu,
    )
    menu_buttons.append(btn_menu)


def show_win_screen(score, deaths):
    clear_menu()

    title = Text(
        text="YOU SURVIVED",
        position=(0, 0.3, 0),
        origin=(0, 0),
        scale=4,
        color=GOLD,
    )
    menu_texts.append(title)

    score_t = Text(
        text=f"Final Score: {score}",
        position=(0, 0.15, 0),
        origin=(0, 0),
        scale=1.5,
        color=GOLD,
    )
    menu_texts.append(score_t)

    death_t = Text(
        text=f"Deaths: {deaths}",
        position=(0, 0.1, 0),
        origin=(0, 0),
        scale=1.5,
        color=color.hex("#FF6464"),
    )
    menu_texts.append(death_t)

    comment = ""
    if deaths == 0:
        comment = "IMPOSSIBLE. You didn't die once?"
    elif deaths < 5:
        comment = f"Not bad... only {deaths} deaths."
    elif deaths < 20:
        comment = f"You suffered {deaths} times. Worth it?"
    else:
        comment = f"{deaths} deaths. You are a masochist."

    comment_t = Text(
        text=comment,
        position=(0, 0, 0),
        origin=(0, 0),
        scale=1.2,
        color=color.white,
    )
    menu_texts.append(comment_t)

    def play_again():
        clear_menu()
        from src.threed.game import game_manager
        game_manager.start_game()

    def to_menu():
        clear_menu()
        show_main_menu()

    btn_play = Button(
        text="Play Again",
        position=(0, -0.08, 0),
        scale=(0.3, 0.08),
        color=color.hex("#8B6914"),
        text_color=color.white,
        on_click=play_again,
    )
    menu_buttons.append(btn_play)

    btn_menu = Button(
        text="Main Menu",
        position=(0, -0.18, 0),
        scale=(0.3, 0.08),
        color=color.hex("#555555"),
        text_color=color.white,
        on_click=to_menu,
    )
    menu_buttons.append(btn_menu)
