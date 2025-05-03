from abc import ABC, abstractmethod


class Layer(ABC):
    next_layer_id = 0

    def __init__(self, name):
        self.id = Layer.next_layer_id
        self.name = name
        self.is_active = False

        Layer.next_layer_id += 1

    def __eq__(self, value):
        if isinstance(value, Layer):
            return self.id == value.id
        return False

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False

    @abstractmethod
    def on_attach(self):
        pass

    @abstractmethod
    def on_detach(self):
        pass

    @abstractmethod
    def on_update(self, dt):
        pass  # dt = delta time in seconds

    @abstractmethod
    def on_event(self, event):
        pass

    @abstractmethod
    def on_render(self, renderer):
        pass


class LayerStack:
    def __init__(self):
        self.layers = []

    def __iter__(self):
        yield from self.layers

    def __reversed__(self):
        yield from reversed(self.layers)

    def __len__(self):
        return len(self.layers)

    def __getitem__(self, index):
        return self.layers[index]

    def push_layer(self, layer):
        self.layers.append(layer)
        layer.on_attach()
        layer.activate()

    def pop_layer(self, layer):
        if layer in self.layers:
            if layer.is_active:
                layer.deactivate()
            layer.on_detach()
            self.layers.remove(layer)
            return True

        return False

    def get_layer(self, layer_id):
        for layer in self.layers:
            if layer.id == layer_id:
                return layer
        return None

    def update(self, dt):
        for layer in self.layers:  # ordering doesn't matter in update
            if layer.is_active:
                layer.on_update(dt)

    def render(self, renderer):
        for layer in self.layers:  # bottom-up rendering
            if layer.is_active:
                layer.on_render(renderer)

    def handle_event(self, event):
        for layer in reversed(self.layers):  # top-down event handling
            if layer.is_active:
                layer.on_event(event)
                if event.handled:
                    break

    def clear(self):
        for layer in self.layers:
            layer.deactivate()
            layer.on_detach()
        self.layers.clear()
