import pygame.transform

from resource_manager import ResourceManager

class Agente:
    def __init__(self, xy, image, movements, size, start):
        self.image = pygame.transform.scale(ResourceManager.image_load(image + '.png'), (size, size)).convert_alpha()
        self.size = size
        self.start = start
        self.pos = start
        self.x = 46 + (start[1] + 1) * self.size
        self.y = 22 + (start[0] + 1) * self.size
        self.speed = 1
        self.movements = movements
        self.next_movement = 0


    def move(self):
        if (self.next_movement) != (len(self.movements)):
            if self.pos[1] > self.movements[self.next_movement][1]:
                self.x = self.x - self.speed
            elif self.pos[1] < self.movements[self.next_movement][1]:
                self.x = self.x + self.speed
            elif self.pos[0] > self.movements[self.next_movement][0]:
                self.y = self.y - self.speed
            elif self.pos[0] < self.movements[self.next_movement][0]:
                self.y = self.y + self.speed

            if self.x == (46 + (self.movements[self.next_movement][1] + 1) * self.size) and self.y == (22 + (self.movements[self.next_movement][0] + 1) * self.size):
                self.pos = self.movements[self.next_movement]
                self.next_movement = self.next_movement + 1
                return True

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

    def reset(self):
        self.pos = self.start
        self.x = 46 + (self.pos[1] + 1) * self.size
        self.y = 22 + (self.pos[0] + 1) * self.size
        self.next_movement = 0
        self.printed = 1

    def rep_pos(self):
        if self.next_movement != len(self.movements):
            if self.pos == self.movements[self.next_movement]:
                return True
            return False