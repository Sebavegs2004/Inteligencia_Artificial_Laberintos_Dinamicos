from importlib import reload

import numpy as np
import pygame
import random as rd
from LOGICA.DStarlite import run_DStarLite
from LOGICA.GeneticAlgorithm import GeneticAlgorithm
from button import Button
import sys
from INTERFAZ.resource_manager import ResourceManager
import os
from agent import Agente
import Color
import numpy


class Simulation:
    def __init__(self):
        self.size = None
        self.agent = None
        self.map = None
        self.size_map = None
        self.size_tile = None
        self.tile_sprites = None
        self.iteracion = 1
        self.walls = []
        self.end = None
        self.start_ticks = None
        self.running = 0
        self.prize = None
        self.prize_activated = False
        self.reset_button = Button(896, 410, 'reset')
        self.remake_button = Button(896, 500, 'remake')
        self.exit_button = Button(1080, 600, 'exit_button')
        self.agent_start_point = None
        self.surface = None
        self.simulation = None
        self.prize = None
        self.fake = None
        self.fake_pos = None
        self.fake_pos_draw = None
        self.agent_reaction_state = 0
        self.font = pygame.font.SysFont("Arial", 36)
        self.reaction_text = self.font.render("Agent live reaction", False, Color.BLANCO)
        self.walking_reaction = pygame.transform.scale(ResourceManager.image_load('agent_running.jpeg'), (472, 300)).convert()
        self.thinking_reaction = pygame.transform.scale(ResourceManager.image_load('agent_think.png'), (472, 300)).convert()
        self.win_reaction = pygame.transform.scale(ResourceManager.image_load('agent_win.jpeg'), (472, 300)).convert()
        self.sad_reaction = pygame.transform.scale(ResourceManager.image_load('agent_sad.jpg'), (472, 300)).convert()

    def draw(self, surface):
        pygame.draw.rect(surface, Color.GRAFITO, (768, 0, 512, 720))
        # if self.iteracion != len(self.walls) - 1:
        for x in range(self.size_map):
            for y in range(self.size_map):
                surface.blit(self.tile_sprites[self.map[x][y]], (46 + y * self.size_tile, 22 + x * self.size_tile))
        if self.running == 1:
            if self.agent.move():
                self.start_ticks = pygame.time.get_ticks()
                self.running = 2
                if self.agent.rep_pos():
                    self.agent_reaction_state = 1
                else:
                    self.agent_reaction_state = 0

        if self.simulation == 'genetic':
            surface.blit(self.reaction_text, (800, 10))
            if self.agent_reaction_state == 0:
                surface.blit(self.walking_reaction, (788 , 60))
            if self.agent_reaction_state == 1:
                surface.blit(self.thinking_reaction, (788, 60))
            if self.agent_reaction_state == 2:
                surface.blit(self.win_reaction, (788, 60))
            if self.agent_reaction_state == 3:
                surface.blit(self.sad_reaction, (788, 60))

    
        if self.running == 0 and pygame.time.get_ticks() - self.start_ticks >= 3000:
            ResourceManager.music_load('death_report.mp3')
            self.running = 1
        if self.running == 2:
            if self.agent_reaction_state == 1:
                if pygame.time.get_ticks() - self.start_ticks >= 1000:
                    self.iteracion = self.iteracion + 1
                    self.reload_map()
                    self.running = 1
            else:
                if pygame.time.get_ticks() - self.start_ticks >= 300:
                    self.iteracion = self.iteracion + 1
                    self.reload_map()
                    self.running = 1

        if not self.prize_activated:
            surface.blit(self.prize, (46 + (self.end[1] + 1) * self.size_tile, 22 + (self.end[0] + 1) * self.size_tile))
        if self.fake_pos_draw != []:
            for x in self.fake_pos_draw:
                surface.blit(self.fake,(46 + (x[1] + 1) * self.size_tile, 22 + (x[0] + 1) * self.size_tile))
        self.agent.draw(surface)

        if self.agent.pos in self.fake_pos_draw:
            self.fake_pos_draw.remove(self.agent.pos)
            ResourceManager.sound_load('nom.mp3').play()

        if self.iteracion + 1 == len(self.walls) and not self.prize_activated:
            if self.agent.pos == self.end:
                ResourceManager.stop_music()
                sound = ResourceManager.sound_load('prizemortadela.mp3')
                sound.play()
                self.prize_activated = True  # marca que ya se reprodujo
                self.agent_reaction_state = 2
            else:
                ResourceManager.stop_music()
                sound = ResourceManager.sound_load('sad.mp3')
                sound.play()
                self.prize_activated = True
                self.agent_reaction_state = 3
            
        self.reset_button.draw(surface)
        self.remake_button.draw(surface)
        self.exit_button.draw(surface)

    def handle_events(self, events):
        if self.reset_button.click_event(events):
            pygame.mixer.stop()
            self.running = 0
            self.iteracion = 0
            self.repeat = False
            self.start_ticks = pygame.time.get_ticks()
            sound = ResourceManager.sound_load('go123.mp3')
            sound.set_volume(0.5)
            sound.play()
            self.fake_pos_draw = self.fake_pos
            self.agent.reset()
            self.reload_map()
            self.prize_activated = False
            ResourceManager.stop_music()
        if self.remake_button.click_event(events):
            ResourceManager.stop_music()
            pygame.mixer.stop()
            if self.simulation == 'dstarlite':
                self.load_DStarlite(self.size, self.surface)
            else:
                self.load_GeneticAlgorithm(self.size, self.surface)
        if self.exit_button.click_event(events):
            ResourceManager.stop_music()
            pygame.mixer.stop()
            ResourceManager.music_load('tvtime.mp3')
            return 'selection'
        return None

    def set_borders(self):
        self.map[0][0] = 2
        self.map[0][self.size_map - 1] = 4
        self.map[self.size_map - 1][0] = 8
        self.map[self.size_map - 1][self.size_map - 1] = 6
        for x in range(self.size_map - 2):
            self.map[0][x + 1] = 3
            self.map[self.size_map - 1][x + 1] = 7
            self.map[x + 1][0] = 9
            self.map[x + 1][self.size_map - 1] = 5

        return

    def load_DStarlite(self, size, surface):
        surface.blit(ResourceManager.image_load('loading.png').convert_alpha(), (400,240))
        pygame.display.flip()
        self.simulation = 'dstarlite'
        results = run_DStarLite(size)
        self.prize_activated = False
        self.surface = surface
        self.running = 0
        self.iteracion = 0
        self.end = results[1]
        self.size = size
        self.walls = results[3]
        self.map = np.zeros((size + 2, size + 2), dtype=int)
        self.size_map = len(self.map[0])
        self.size_tile = int(676 / self.size_map)
        self.set_borders()
        for x in range(size):
            for y in range(size):
                self.map[y + 1][x + 1] = self.walls[0][y][x]
        self.agent = Agente((46 + (results[0][1] + 1) * self.size_tile, 22 + (results[0][0]) * self.size_tile), 'trans', results[2], self.size_tile, results[0])
        self.agent_start_point = (self.agent.x, self.agent.y)
        self.tile_sprites = [pygame.transform.scale(ResourceManager.image_load('sand.png'), (self.size_tile, self.size_tile)).convert(), # 0
                             pygame.transform.scale(ResourceManager.image_load('wall.png'), (self.size_tile, self.size_tile)).convert(), # 1
                             pygame.transform.scale(ResourceManager.image_load('wall_corner_ul.png'), (self.size_tile, self.size_tile)).convert(),
                             pygame.transform.scale(ResourceManager.image_load('wall_up.png'), (self.size_tile, self.size_tile)).convert(),
                             pygame.transform.scale(ResourceManager.image_load('wall_corner_ur.png'), (self.size_tile, self.size_tile)).convert(),
                             pygame.transform.scale(ResourceManager.image_load('wall_right.png'), (self.size_tile, self.size_tile)).convert(),
                             pygame.transform.scale(ResourceManager.image_load('wall_corner_dr.png'), (self.size_tile, self.size_tile)).convert(),
                             pygame.transform.scale(ResourceManager.image_load('wall_down.png'), (self.size_tile, self.size_tile)).convert(),
                             pygame.transform.scale(ResourceManager.image_load('wall_corner_dl.png'), (self.size_tile, self.size_tile)).convert(),
                             pygame.transform.scale(ResourceManager.image_load('wall_left.png'), (self.size_tile, self.size_tile)).convert()]

        self.start_ticks = pygame.time.get_ticks()
        sound = ResourceManager.sound_load('go123.mp3')
        sound.set_volume(0.3)
        sound.play()
        self.prize = pygame.transform.scale(ResourceManager.image_load('premio.png'), (self.size_tile, self.size_tile))
        self.prize = pygame.transform.scale(ResourceManager.image_load('premio.png'), (self.size_tile, self.size_tile))
        self.fake = pygame.transform.scale(ResourceManager.image_load('premio_fake.png'), (self.size_tile, self.size_tile))
        self.fake_pos = results[4].tolist()
        self.fake_pos = [tuple(x) for x in self.fake_pos]
        self.fake_pos_draw = self.fake_pos.copy()

    def load_GeneticAlgorithm(self, size, surface):
        surface.blit(ResourceManager.image_load('loading.png').convert_alpha(), (400,240))
        pygame.display.flip()
        population_size = 120
        num_generations = 50
        chromosome_length = size*3
        mutation_rate = 0.01
        crossover_rate = 0.4
        genetic = GeneticAlgorithm(size, population_size, num_generations, chromosome_length, mutation_rate, crossover_rate)
        results = genetic.run()
        self.prize_activated = False
        self.surface = surface
        self.running = 0
        self.iteracion = 0
        self.simulation = 'genetic'
        self.end = results[1]
        self.size = size
        self.walls = results[3]
        self.map = np.zeros((size + 2, size + 2), dtype=int)
        self.size_map = len(self.map[0])
        self.size_tile = int(676 / self.size_map)
        self.set_borders()
        for x in range(size):
            for y in range(size):
                self.map[y + 1][x + 1] = self.walls[0][y][x]
        self.agent = Agente((46 + (results[0][1] + 1) * self.size_tile, 22 + (results[0][0]) * self.size_tile), 'trans', results[2], self.size_tile, results[0])
        self.agent_start_point = (self.agent.x, self.agent.y)
        self.tile_sprites = [pygame.transform.scale(ResourceManager.image_load('sand.png'), (self.size_tile, self.size_tile)).convert(), # 0
                             pygame.transform.scale(ResourceManager.image_load('wall.png'), (self.size_tile, self.size_tile)).convert(), # 1
                             pygame.transform.scale(ResourceManager.image_load('wall_corner_ul.png'), (self.size_tile, self.size_tile)).convert(),
                             pygame.transform.scale(ResourceManager.image_load('wall_up.png'), (self.size_tile, self.size_tile)).convert(),
                             pygame.transform.scale(ResourceManager.image_load('wall_corner_ur.png'), (self.size_tile, self.size_tile)).convert(),
                             pygame.transform.scale(ResourceManager.image_load('wall_right.png'), (self.size_tile, self.size_tile)).convert(),
                             pygame.transform.scale(ResourceManager.image_load('wall_corner_dr.png'), (self.size_tile, self.size_tile)).convert(),
                             pygame.transform.scale(ResourceManager.image_load('wall_down.png'), (self.size_tile, self.size_tile)).convert(),
                             pygame.transform.scale(ResourceManager.image_load('wall_corner_dl.png'), (self.size_tile, self.size_tile)).convert(),
                             pygame.transform.scale(ResourceManager.image_load('wall_left.png'), (self.size_tile, self.size_tile)).convert()]

        self.start_ticks = pygame.time.get_ticks()
        sound = ResourceManager.sound_load('go123.mp3')
        sound.set_volume(0.5)
        sound.play()
        self.prize = pygame.transform.scale(ResourceManager.image_load('premio.png'), (self.size_tile, self.size_tile))
        self.fake = pygame.transform.scale(ResourceManager.image_load('premio_fake.png'), (self.size_tile, self.size_tile))
        self.fake_pos = results[4]
        self.fake_pos_draw = results[4]
        self.agent_reaction_state = 0



    def reload_map(self):
        if self.iteracion < len(self.walls):
            for x in range(self.size):
                for y in range(self.size):
                    self.map[y + 1][x + 1] = self.walls[self.iteracion][y][x]





