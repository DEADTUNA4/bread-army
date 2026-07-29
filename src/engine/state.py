import pygame
from abc import ABC, abstractmethod


class State(ABC):
    def __init__(self, game):
        self.game = game

    @abstractmethod
    def handle_event(self, event):
        pass

    @abstractmethod
    def update(self, dt):
        pass

    @abstractmethod
    def render(self, surface):
        pass

    def enter(self):
        pass

    def exit(self):
        pass


class StateMachine:
    def __init__(self):
        self.states = {}
        self.current_state = None

    def add_state(self, name, state):
        self.states[name] = state

    def set_state(self, name):
        if self.current_state:
            self.current_state.exit()
        self.current_state = self.states.get(name)
        if self.current_state:
            self.current_state.enter()
        return self.current_state is not None

    def handle_event(self, event):
        if self.current_state:
            self.current_state.handle_event(event)

    def update(self, dt):
        if self.current_state:
            self.current_state.update(dt)

    def render(self, surface):
        if self.current_state:
            self.current_state.render(surface)
