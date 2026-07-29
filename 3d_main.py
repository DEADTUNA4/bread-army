from ursina import *
from src.threed.game import GameManager
from src.threed.settings import VERSION

app = Ursina(borderless=False, development_mode=False)
window.title = f"Bread Army 3D - {VERSION}"
window.size = (1024, 768)
window.color = color.hex("#1a0f0a")

game = GameManager()

app.run()
