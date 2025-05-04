from abc import ABC, abstractmethod
import pygame
from core.EventManager import Event, EventBuffer
from core.LayerSystem import Layer, LayerStack
from core.Renderer import Renderer
import core.EventManager as em


class Application(ABC):
    instance = None
    
    def __init__(self, config: dict):
        if Application.instance is not None:
            raise Exception("Application instance already exists.")
        Application.instance = self
        
        pygame.init()

        self.config = config
        self.working_directory = config.get("working_directory", ".")
        self.size = config.get("size", (800, 600))
        self.title = config.get("title", "Application")

        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption(self.title)

        self.fps = config.get("fps", 60)

        self.clock = pygame.time.Clock()
        self.layer_stack = LayerStack()
        self.event_buffer = EventBuffer()
        self.renderer = Renderer(self.screen)

        self.running = False
        
    @classmethod
    def get(cls):
        if cls.instance is None:
            raise Exception("Application instance not created yet.")
        return cls.instance


    @abstractmethod
    def on_start(self):
        """Abstract method to be implemented by subclasses for initialization."""
        pass

    def run(self):
        self.running = True

        while self.running:
            dt = self.clock.tick(self.fps) / 1000.0

            self.renderer.clear()
            self.layer_stack.update(dt)
            self.layer_stack.render(self.renderer)
            self.renderer.show()
            
            for event in pygame.event.get():
                mapped_event = self.map_events(event)
                if mapped_event:
                    self.on_event(mapped_event)
            self.event_buffer.propogate_events(self.layer_stack)

        self.layer_stack.clear()
        pygame.quit()

    def on_event(self, event: Event):
        if event.type == "WINDOW_CLOSE":
            self.on_close()
            return

        self.event_buffer.add_event(event)

    def on_close(self):
        self.running = False

    def map_events(self, event: pygame.event.Event):
        if event.type == pygame.QUIT:
            return em.WindowCloseEvent()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return em.WindowCloseEvent()
            else:
                return em.KeyPressEvent(event.key)
        elif event.type == pygame.KEYUP:
            return em.KeyReleaseEvent(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            return em.MouseClickEvent(event.button, event.pos)
        elif event.type == pygame.VIDEORESIZE:
            return em.WindowResizeEvent(event.w, event.h)

        return None
