import pygame
from button import Button
import input_event
from INTERFAZ.resource_manager import ResourceManager
import Color


class GameMode:
    def __init__(self):
        self.dstar_button = Button(334, 328, 'dstar')
        self.genetic_button = Button(334 + 256 + 100, 328, 'genetico')
        self.exit_button = Button(1080, 600, 'exit_button')
        self.screamer = ResourceManager.image_load('vidal.jpg')
        self.screamer_on = 0
        self.text = "INGRESE TAMAÑO"
        self.input_active = False
        self.alpha = 255
        self.input_box = pygame.Rect(100, 80, 600, 50)
        self.font = pygame.font.Font(None, 48)
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.color = self.color_inactive
        self.prompt_text = "Ingrese tamaño (5 <= x <= 50)"

    def draw(self, surface, transition=0):
        self.dstar_button.draw(surface)
        self.genetic_button.draw(surface)
        self.exit_button.draw(surface)
        pygame.draw.rect(surface, pygame.Color('white'), self.input_box)
        pygame.draw.rect(surface, self.color, self.input_box, 2)
        txt_surface = self.font.render(self.text, True, pygame.Color('black'))
        surface.blit(txt_surface, (self.input_box.x + 5, self.input_box.y + 5))
        prompt_surface = self.font.render(self.prompt_text, True, Color.BLANCO)
        surface.blit(prompt_surface, (self.input_box.x + self.input_box.width + 10, self.input_box.y + 10))

    def handle_events(self, events):
        if input_event.left_click(events):
            if self.input_box.collidepoint(pygame.mouse.get_pos()):
                self.text = ""
                self.input_active = True
            else:
                self.input_active = False
            self.color = self.color_active if self.input_active else self.color_inactive

        if self.input_active:
            tecla = input_event.key_press(events)
            if tecla is not None:
                if tecla == 'backspace':
                    self.text = self.text[:-1]
                else:
                    self.text += tecla

        if self.dstar_button.click_event(events):
            if self.text.isdigit():  # validar input numérico
                value = int(self.text)
                if 5 <= value <= 50:
                    self.text = "INGRESE TAMAÑO"
                    return ('simulation', value, 'dstar')
                else:
                    self.text = "[ERROR]: FUERA DE RANGO"
                    self.input_active = False
            else:
                self.text = "[ERROR]: NO DIGITO "
                self.input_active = False
        if self.genetic_button.click_event(events):
            if self.text.isdigit():
                value = int(self.text)
                if 5 <= value <= 50:
                    self.text = "INGRESE TAMAÑO"
                    return ('simulation', value, 'genetic')
                else:
                    self.text = "[ERROR]: FUERA DE RANGO"
                    self.input_active = False
            else:
                self.text = "[ERROR]: NO DIGITO "
                self.input_active = False
        if self.exit_button.click_event(events):
            return 'main_menu'

        return None