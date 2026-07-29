import pygame
import sys
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, TITLE, FPS


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 1.0
        from src.engine.state import StateMachine
        self.state_machine = StateMachine()

    def change_state(self, name):
        self.state_machine.set_state(name)

    def run(self):
        while self.running:
            self.dt = self.clock.tick(FPS) / 16.667
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.state_machine.handle_event(event)
            self.state_machine.update(self.dt)
            self.state_machine.render(self.screen)
            pygame.display.flip()
        pygame.quit()
        sys.exit()
