import pygame
from button import Button
import sys
from INTERFAZ.resource_manager import ResourceManager
import input_event
import Color


class MainMenu:
    def __init__(self):
        self.start_button = Button(576, 380, 'genericstart')
        self.exit_button = Button(585, 480, 'genericexit')
        self.menu_title = ResourceManager.image_load('title_mortadelasimulator.png').convert_alpha()
        self.screamer = pygame.transform.scale(ResourceManager.image_load('vidal.jpg'), (1280, 720)).convert()
        self.alpha = 255
        self.screamer.set_alpha(255)
        self.activate = 0
        self.trans = ResourceManager.image_load('trans.png').convert_alpha()
        self.pos = (10, 200)
        self.rect = pygame.Rect(268, 309, 11, 11)


    def draw(self, surface, transition = 0):
        surface.blit(self.menu_title, (329.5 , -100))
        self.start_button.draw(surface)
        self.exit_button.draw(surface)
        surface.blit(self.trans, self.pos)
        if self.activate == 1:
            surface.blit(self.screamer, (0,0))
            self.alpha -= 4
            if self.alpha >= 0:
                self.screamer.set_alpha(self.alpha)
            else:
                self.activate = 0
                ResourceManager.music_load('tvtime.mp3')

    def handle_events(self, events):
        if self.start_button.click_event(events):
            return 'selection'
        if self.exit_button.click_event(events):
            pygame.quit()
            sys.exit()
        if input_event.left_click(events):
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.activate = 1
                self.alpha = 255
                ResourceManager.stop_music()
                ResourceManager.sound_load('ahh.mp3').play()

                self.screamer.set_alpha(self.alpha)



        return None

