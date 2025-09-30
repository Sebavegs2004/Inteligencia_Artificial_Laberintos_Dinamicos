import pygame
import os
from screen_manager import ScreenManager
from INTERFAZ.resource_manager import ResourceManager


def main():
    pygame.init()
    x = 0
    y = 0
    screen_size = (1280, 720)
    screen = pygame.display.set_mode(screen_size)
    background = ResourceManager.image_load('menu_mortadela.png').convert()
    imagen1 = ResourceManager.image_load('insano.png')
    pygame.display.set_caption("Simulador Laberinto")
    pygame.display.set_icon(imagen1)
    pygame.mixer.init()
    screen_manager = ScreenManager()
    clock = pygame.time.Clock()
    y_speed = 1.125
    running = True
    x_speed = 2


    while running:

        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                running = False

        x -= x_speed
        y -= y_speed
        if x <= - background.get_width():
            x = 0
            y = 0
        screen.blit(background, (x, y))
        screen.blit(background, (x + background.get_width(), y))
        screen.blit(background, (x, y + background.get_height()))
        screen.blit(background, (x + background.get_width(), y + background.get_height()))

        screen_manager.handle_events(events, screen)
        screen_manager.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()


def run():
    main()
