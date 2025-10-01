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
import random


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
        self.dontgiveup_button = Button (256, 600, 'dontgiveup_button')
        self.agent_start_point = None
        self.surface = None
        self.simulation = None
        self.prize = None
        self.fake = None
        size = (376, 240)
        my = 200
        self.fake_pos = None
        self.fake_pos_draw = None
        self.agent_reaction_state = 0
        self.font = pygame.font.SysFont("Arial", 36)
        self.reaction_text = self.font.render("Agent live reaction:", False, Color.BLANCO)
        self.memory_text = self.font.render("Nah, I'd Win:", False, Color.BLANCO)
        self.memory_text.set_alpha(0)
        self.walking_reaction = pygame.transform.scale(ResourceManager.image_load('agent_running.jpeg'), size).convert()
        self.thinking_reaction = pygame.transform.scale(ResourceManager.image_load('agent_think.png'), size).convert()
        self.win_reaction = pygame.transform.scale(ResourceManager.image_load('agent_win.jpeg'), size).convert()
        self.sad_reaction = pygame.transform.scale(ResourceManager.image_load('agent_sad.jpg'), size).convert()
        self.giveup_reaction = pygame.transform.scale(ResourceManager.image_load('agent_giveup.png'), size).convert()
        self.bad_eat = pygame.transform.scale(ResourceManager.image_load('bad_eat.png'), size).convert()
        self.memory1 = pygame.transform.scale(ResourceManager.image_load('memory1.jpeg'), (size[0], my)).convert()
        self.memory2 = pygame.transform.scale(ResourceManager.image_load('memory2.jpeg'), (size[0], my)).convert()
        self.memory3 = pygame.transform.scale(ResourceManager.image_load('memory3.jpeg'), (size[0], my)).convert()
        self.memory_prize = pygame.transform.scale(ResourceManager.image_load('premio_fake.png'), (100, 100)).convert_alpha()
        self.trans_memory = ResourceManager.image_load('trans_memory.png').convert_alpha()
        self.agent_determination = ResourceManager.image_load('agent_determination.png').convert_alpha()
        self.agent_determination.set_alpha(0)
        self.memory_prize.set_alpha(0)
        self.trans_memory.set_alpha(0)
        self.memory1.set_alpha(0)
        self.memory2.set_alpha(0)
        self.memory3.set_alpha(0)
        self.memory_spacing = int((720  - my*3)/4) 
        self.prob_dontgiveup = 0.4
        self.dontgiveup_trigger = -1
        self.trigger_memory = 0
        self.memory_speed = 2
        self.memory_alpha_speed = 2
        self.memory1_x = 452 + self.memory1.get_width() + 300
        self.memory2_x = 452 - 300
        self.memory3_x = 452 + self.memory1.get_width() + 300
        self.memory1_alpha = 0
        self.memory2_alpha = 0
        self.memory3_alpha = 0
        self.memory_prize_alpha = 0
        self.trans_memory_alpha = 0
        self.memory_text_alpha = 0
        self.desaparecer = 0



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
                if self.agent.rep_pos() and self.running == 2:
                    self.agent_reaction_state = 1
                else:
                    self.agent_reaction_state = 0
                if self.iteracion + 1 == self.dontgiveup_trigger and random.random() <= self.prob_dontgiveup and self.simulation == 'genetic':
                    ResourceManager.stop_music()
                    sound = ResourceManager.sound_load('sad.mp3')
                    sound.play()
                    self.agent_reaction_state = 3
                    self.running = 3        

        if self.simulation == 'genetic':
            surface.blit(self.reaction_text, (800, 10))
            if self.agent_reaction_state == 0:
                surface.blit(self.walking_reaction, (788+ 48 , 60))
            if self.agent_reaction_state == 1:
                surface.blit(self.thinking_reaction, (788+ 48 , 60))
            if self.agent_reaction_state == 2:
                surface.blit(self.win_reaction, (788+ 48 , 60))
            if self.agent_reaction_state == 3:
                surface.blit(self.sad_reaction, (788+ 48 , 60))
            if self.agent_reaction_state == 4:
                surface.blit(self.giveup_reaction, (788+ 48 , 60))
            if self.agent_reaction_state == 5:
                surface.blit(self.bad_eat,  (788+ 48 , 60))

        if self.simulation == 'dstarlite':
            surface.blit(self.reaction_text, (800, 10))
            if self.agent_reaction_state == 0:
                surface.blit(self.walking_reaction, (788+ 48 , 60))
            if self.agent_reaction_state == 2:
                surface.blit(self.win_reaction, (788+ 48 , 60))
            if self.agent_reaction_state == 5:
                surface.blit(self.bad_eat,  (788+ 48 , 60))
            
            


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
            self.agent_reaction_state = 5
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
                self.agent_reaction_state =  3
                
        if self.running == 3:
            if pygame.time.get_ticks() - self.start_ticks > 5500:
                self.agent_reaction_state = 4
                self.dontgiveup_button.draw(surface)

        if self.running == 4:
            pygame.draw.rect(surface, Color.NEGRO, (0, 0, 1280, 720))
            if self.trigger_memory == 0 and pygame.time.get_ticks() - self.start_ticks > 2000:
                ResourceManager.music_load('noterindas.mp3')
                self.trigger_memory = 1
            if pygame.time.get_ticks() - self.start_ticks > 5000:
                surface.blit(self.memory1, (self.memory1_x, self.memory_spacing))
                surface.blit(self.memory2, (self.memory2_x, self.memory_spacing*2 + self.memory1.get_height()))
                surface.blit(self.memory3, (self.memory3_x, self.memory_spacing*3 + self.memory1.get_height()*2))
                surface.blit(self.trans_memory, (416, 135))
                surface.blit(self.memory_prize, (590,500))
                surface.blit(self.memory_text, (537,30))
                surface.blit(self.agent_determination, (416, 135))

                if self.desaparecer == 0:
                    self.memory1_x -= self.memory_speed
                    if self.memory1_alpha < 255:
                        self.memory1.set_alpha(self.memory1_alpha)
                        self.memory1_alpha += self.memory_alpha_speed
                    else:
                        self.memory1.set_alpha(255)
                        self.memory1_alpha = 255
                        self.desaparecer += 1
                if self.desaparecer == 1:
                    self.memory1_x -= self.memory_speed
                    if self.memory1_alpha > 0:
                        self.memory1.set_alpha(self.memory1_alpha)
                        self.memory1_alpha -= self.memory_alpha_speed
                    else:
                        self.memory1.set_alpha(0)
                        self.memory1_alpha = 0
                        self.desaparecer += 1
                if self.desaparecer == 2:
                    self.memory2_x += self.memory_speed
                    if self.memory2_alpha < 255:
                        self.memory2.set_alpha(self.memory2_alpha)
                        self.memory2_alpha += self.memory_alpha_speed
                    else:
                        self.memory2.set_alpha(255)
                        self.memory2_alpha = 255
                        self.desaparecer += 1
                if self.desaparecer == 3:
                    self.memory2_x += self.memory_speed
                    if self.memory2_alpha > 0:
                        self.memory2.set_alpha(self.memory2_alpha)
                        self.memory2_alpha -= self.memory_alpha_speed
                    else:
                        self.memory2.set_alpha(0)
                        self.memory2_alpha = 0
                        self.desaparecer += 1
                if self.desaparecer == 4:
                    self.memory3_x -= self.memory_speed
                    if self.memory3_alpha < 255:
                        self.memory3.set_alpha(self.memory3_alpha)
                        self.memory3_alpha += self.memory_alpha_speed
                    else:
                        self.memory3.set_alpha(255)
                        self.memory3_alpha = 255
                        self.desaparecer += 1
                if self.desaparecer == 5:
                    self.memory3_x -= self.memory_speed
                    if self.memory3_alpha > 0:
                        self.memory3.set_alpha(self.memory3_alpha)
                        self.memory3_alpha -= self.memory_alpha_speed
                    else:
                        self.memory3.set_alpha(0)
                        self.memory3_alpha = 0
                        self.desaparecer += 1
                if self.desaparecer == 6:
                    if self.memory_prize_alpha < 255:
                        self.memory_prize.set_alpha(self.memory_prize_alpha)
                        self.memory_prize_alpha += 3
                    else:
                        self.memory_prize.set_alpha(255)
                        self.desaparecer += 1
                if self.desaparecer == 7:
                    if self.trans_memory_alpha < 130:
                        self.trans_memory.set_alpha(self.trans_memory_alpha)
                        self.trans_memory_alpha += 2
                    else:
                        self.trans_memory.set_alpha(130)
                        self.desaparecer += 1
                if self.desaparecer == 8 and pygame.time.get_ticks() - self.start_ticks > 23000:
                        self.agent_determination.set_alpha(255)
                        self.memory_text.set_alpha(255)
                        self.desaparecer += 1
                if self.desaparecer == 9 and pygame.time.get_ticks() - self.start_ticks > 26000:
                    self.running = 2
                
        if self.running != 4:
            self.reset_button.draw(surface)
            self.remake_button.draw(surface)
            self.exit_button.draw(surface)

    def handle_events(self, events):
        if self.reset_button.click_event(events) and self.running < 4:
            pygame.mixer.stop()
            self.running = 0
            self.iteracion = 0
            self.repeat = False
            self.start_ticks = pygame.time.get_ticks()
            sound = ResourceManager.sound_load('go123.mp3')
            sound.set_volume(0.5)
            sound.play()
            self.fake_pos_draw = self.fake_pos
            self.agent_reaction_state = 0
            self.agent.reset()
            self.trigger_memory = 0
            self.memory1_x = 452
            self.memory2_x = 452
            self.memory3_x = 452
            self.desaparecer = 0
            self.trigger_memory = 0
            self.memory_prize_alpha = 0
            self.memory_prize.set_alpha(0)
            self.trans_memory.set_alpha(0)
            self.memory_text.set_alpha(0)
            self.agent_determination.set_alpha(0)
            self.trans_memory_alpha = 0
            self.memory_text_alpha = 0
            self.reload_map()
            self.prize_activated = False
            ResourceManager.stop_music()
        if self.remake_button.click_event(events) and self.running < 4:
            ResourceManager.stop_music()
            pygame.mixer.stop()
            if self.simulation == 'dstarlite':
                self.load_DStarlite(self.size, self.surface)
            else:
                self.load_GeneticAlgorithm(self.size, self.surface)
        if self.exit_button.click_event(events) and self.running < 4:
            ResourceManager.stop_music()
            pygame.mixer.stop()
            ResourceManager.music_load('tvtime.mp3')
            return 'selection'
        if self.dontgiveup_button.click_event(events) and self.running == 3:
            ResourceManager.sound_load('turn_off.mp3').play()
            self.start_ticks = pygame.time.get_ticks()
            self.running = 4
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
        self.agent_reaction_state = 0

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
        print(len(results[2]))
        self.end = results[1]
        self.size = size
        self.trigger_memory = 0
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
        if len(results[2]) >= 30 and results[1] == results[2][len(results[2]) - 1]:
            self.dontgiveup_trigger = len(results[2]) - int(len(results[2])*0.35)
        else:
            self.dontgiveup_trigger = -1
        self.trigger_memory = 0
        self.memory1_x = 452 + 300
        self.memory2_x = 452 - 300
        self.memory3_x = 452 + 300
        self.desaparecer = 0
        self.trigger_memory = 0
        self.memory_prize_alpha = 0
        self.trans_memory_alpha = 0
        self.memory_text_alpha = 0
        self.memory_prize.set_alpha(0)
        self.trans_memory.set_alpha(0)
        self.memory_text.set_alpha(0)
        self.agent_determination.set_alpha(0)



    def reload_map(self):
        if self.iteracion < len(self.walls):
            for x in range(self.size):
                for y in range(self.size):
                    self.map[y + 1][x + 1] = self.walls[self.iteracion][y][x]






