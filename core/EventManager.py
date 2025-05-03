from typing import Callable
from core.LayerSystem import LayerStack


class EventCategory:
    Application = 0x01
    Input = 0x02
    Keyboard = 0x04
    Mouse = 0x08
    Window = 0x10
    Game = 0x20


class Event:
    def __init__(self, type, category_flags):
        self.type = type
        self.category_flags = category_flags
        self.handled = False

    def is_in_category(self, category):
        return (self.category_flags & category) != 0

    def __str__(self):
        return f"Event(type={self.type}, category_flags={self.category_flags}, handled={self.handled})"


class KeyPressEvent(Event):
    def __init__(self, key):
        Event.__init__(self, "KEY_PRESS", EventCategory.Keyboard | EventCategory.Input)
        self.key = key


class KeyReleaseEvent(Event):
    def __init__(self, key):
        Event.__init__(
            self, "KEY_RELEASE", EventCategory.Keyboard | EventCategory.Input
        )
        self.key = key


class MouseClickEvent(Event):
    def __init__(self, button: int, pos: tuple):
        # button: 1 for left, 2 for middle, 3 for right
        Event.__init__(self, "MOUSE_CLICK", EventCategory.Mouse | EventCategory.Input)
        self.button = button
        self.pos = pos  # tuple (i, j) for y, x position


class WindowCloseEvent(Event):
    def __init__(self):
        Event.__init__(
            self, "WINDOW_CLOSE", EventCategory.Application | EventCategory.Window
        )


class WindowResizeEvent(Event):
    def __init__(self, new_size):
        Event.__init__(
            self, "WINDOW_RESIZE", EventCategory.Application | EventCategory.Window
        )
        self.new_size = new_size  # tuple (width, height)


class EventDispatcher:
    def __init__(self, event):
        self.event: Event = event

    def dispatch(self, event_type, func: Callable[[Event], bool]):
        if self.event.type == event_type and self.event.handled is False:
            self.event.handled |= func(self.event)
            return True

        return False


class EventBuffer:
    def __init__(self):
        self.events = []

    def __iter__(self):
        yield from self.events

    def add_event(self, event):
        self.events.append(event)

    def clear(self):
        self.events.clear()

    def propogate_events(self, layer_stack: LayerStack):
        for event in self.events:
            layer_stack.handle_event(event)
