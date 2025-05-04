import pygame
import os

class ResourceManager:
    def __init__(self):
        self.assets = {
            'image': {}
        }
        
    def load_image(self, name, path, convert_alpha=True):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Image file {path} not found.")
        
        img = pygame.image.load(path)
        if convert_alpha:
            img = img.convert_alpha()
            
        self.assets['image'][name] = img
        return img
    
    def get(self, category, name):
        return self.assets.get(category, {}).get(name)
    
    def has(self, category, name):
        return name in self.assets.get(category, {})
    
    def unload(self, category, name):
        if self.has(category, name):
            del self.assets[category][name]
            
    def clear(self):
        for category in self.assets:
            # make list to avoid modifying dict during iteration
            for name in list(self.assets[category].keys()): 
                self.unload(category, name)