import pygame
import input_event
from INTERFAZ.resource_manager import ResourceManager
from abc import ABC, abstractmethod

class ButtonAbstract(ABC):
    """
    Clase abstracta que define el funcionamiento bascio para todos los botones.

    Atributos:
        image: Imagen normal del botón.
        image_mouse_hold: Imagen cuando el mouse está sobre el botón.
        image_hitbox: Rect basado en las dimensiones de la imagen para usar como hitbox.
        y: Posición vertical (útil para scroll).
    """

    def __init__(self, x, y, image):
        self.image = ResourceManager.image_load(image + '.png').convert_alpha()
        self.image_mouse_hold = ResourceManager.image_load(image + '_hold.png').convert_alpha()
        self.image_hitbox = self.image.get_rect()
        self.image_hitbox.topleft = (x, y)
        self.y = y

    @abstractmethod
    def click_event(self, events):
        """Maneja el evento de click del botón."""
        pass

    @abstractmethod
    def draw(self, surface, scroll_y=0):
        """Dibuja el botón en la pantalla."""
        pass


class Button(ButtonAbstract):
    """
    Botón simple con un solo estado visual: normal y hover.
    """

    def __init__(self, x, y, image):
        super().__init__(x, y, image)

    def draw(self, surface, scroll_y=0):
        """
        Dibuja el botón en pantalla.
        Cambia la imagen si el mouse está sobre el botón.
        """
        if self.image_hitbox.collidepoint(pygame.mouse.get_pos()):
            surface.blit(self.image_mouse_hold, self.image_hitbox.topleft)
        else:
            surface.blit(self.image, self.image_hitbox.topleft)

    def click_event(self, events):
        """
        Detecta si el botón fue clickeado con el botón izquierdo del mouse.
        Retorna True si fue clickeado, False en caso contrario.
        """
        if input_event.left_click(events):
            if self.image_hitbox.collidepoint(pygame.mouse.get_pos()):
                return True
        return False


class ScrollButton(ButtonAbstract):
    """
    Botón que permite desplazamiento vertical (scroll).
    """

    def __init__(self, x, y, image):
        super().__init__(x, y, image)

    def draw(self, surface, scroll_y=0):
        """
        Dibuja el botón aplicando un desplazamiento vertical.
        Actualiza la posicion de la hitbox para que las colisiones sigan funcionando correctamente.
        """
        # Actualiza posición vertical del rect según scroll
        self.image_hitbox.topleft = (self.image_hitbox.topleft[0], self.y + scroll_y)

        # Dibuja la imagen correspondiente según si el mouse está sobre el botón
        if self.image_hitbox.collidepoint(pygame.mouse.get_pos()):
            surface.blit(self.image_mouse_hold, (self.image_hitbox.topleft[0], self.y + scroll_y))
        else:
            surface.blit(self.image, (self.image_hitbox.topleft[0], self.y + scroll_y))

    def click_event(self, events):
        """
        Detecta si el botón fue clickeado con el mouse.
        Devuelve True si fue clickeado.
        """
        if input_event.left_click(events):
            if self.image_hitbox.collidepoint(pygame.mouse.get_pos()):
                return True
        return False


class ToggleButton(ButtonAbstract):
    """
    Botón que alterna entre dos estados visuales.
    state 0 -> imagen normal
    state 1 -> imagen alternativa
    """
# pene0
# pene0_hold
# pene1
# pene1_hold
    def __init__(self, x, y, image):
        self.state = 0  # estado inicial
        super().__init__(x, y, image + '0')  # carga la primera imagen
        self.image_alt = ResourceManager.image_load(image + '1.png').convert_alpha() # segunda imagen
        self.image_alt_mouse_hold = ResourceManager.image_load(image + '1_hold.png').convert_alpha()  # segunda imagen hover

    def draw(self, surface, scroll_y=0):
        """
        Dibuja el botón según su estado actual.
        Cambia la imagen al pasar el mouse sobre él.
        """
        if self.state == 0:
            if self.image_hitbox.collidepoint(pygame.mouse.get_pos()):
                surface.blit(self.image_mouse_hold, self.image_hitbox.topleft)
            else:
                surface.blit(self.image, self.image_hitbox.topleft)
        elif self.state == 1:
            if self.image_hitbox.collidepoint(pygame.mouse.get_pos()):
                surface.blit(self.image_alt_mouse_hold, self.image_hitbox.topleft)
            else:
                surface.blit(self.image_alt, self.image_hitbox.topleft)

    def click_event(self, events):
        """
        Alterna el estado del botón al hacer click sobre él.
        Devuelve True si el click fue registrado.
        """
        if input_event.left_click(events):
            if self.image_hitbox.collidepoint(pygame.mouse.get_pos()):
                if self.state == 0:
                    self.state = 1
                elif self.state == 1:
                    self.state = 0 # alterna entre 0 y 1
                return True
        return False















