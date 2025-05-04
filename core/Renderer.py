import pygame
from pygame import Surface
from core.LayerSystem import LayerStack

BLACK = (0, 0, 0)


class Renderer:
    def __init__(self, screen: Surface):
        self.screen = screen

    def clear(self):
        self.screen.fill(BLACK)

    def create_surface(self, width, height):
        return pygame.Surface((width, height), pygame.SRCALPHA, 32)

    def submit_surface(self, surface: Surface, x=0, y=0):
        self.screen.blit(surface, (x, y))

    def show(self):
        pygame.display.flip()
