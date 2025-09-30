import pygame


def left_click(events):
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                return True
    return False


def left_hold():
    return pygame.mouse.get_pressed()[0] == 1


def right_click(events):
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:
                return True
    return False


def right_hold():
    return pygame.mouse.get_pressed()[2] == 1


def scroll_up(events):
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                return True
    return False


def scroll_down(events):
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 5:
                return True
    return False

def esc_press(events):
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return True
    return False


def shift_pressed():
    return pygame.key.get_pressed()[pygame.K_LSHIFT]



def r_press(events):
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                return True
    return False

def key_press(events):
    for event in events:
        if event.type == pygame.KEYDOWN:
            tecla = pygame.key.name(event.key)
            return tecla
    

