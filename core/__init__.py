import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

from core.Application import Application
from core.LayerSystem import Layer, LayerStack
from core.EventManager import Event, EventDispatcher, EventBuffer
from core.Renderer import Renderer
from core.ResourceManager import ResourceManager
from core.EntryPoint import main