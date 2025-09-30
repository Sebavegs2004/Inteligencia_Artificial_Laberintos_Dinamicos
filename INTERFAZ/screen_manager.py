
from main_menu import MainMenu
from gamemode import GameMode
from simulation import Simulation
from resource_manager import ResourceManager
import pygame
import sys

class ScreenManager:
    def __init__(self):
        self.screens = {
            'main_menu': MainMenu(),
            'selection' : GameMode(),
            'simulation' : Simulation()
        }
        self.loading_title = ResourceManager.image_load('loading.png').convert_alpha()
        ResourceManager.music_load('tvtime.mp3')
        self.current_screen = 'main_menu'

    def handle_events(self, events, surface):
        result = self.screens[self.current_screen].handle_events(events)
        if result:
            if result[0] == 'simulation' and isinstance(result, tuple):
                if result[2] == 'dstar':
                    ResourceManager.stop_music()
                    self.screens[result[0]].load_DStarlite(result[1], surface)
                    self.current_screen = result[0]
                if result[2] == 'genetic':
                    ResourceManager.stop_music()
                    self.screens[result[0]].load_GeneticAlgorithm(result[1], surface)
                    self.current_screen = result[0]
            else:
                self.current_screen = result

    def draw(self, surface):
        self.screens[self.current_screen].draw(surface)
        pygame.display.flip()

