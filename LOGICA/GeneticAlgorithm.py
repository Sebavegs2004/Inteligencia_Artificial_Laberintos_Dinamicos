import random
import numpy as np
from constants import CellType

def add_random_obstacles(grid, prob, start, goal, fake_goals):
    """
    Agrega obstáculos aleatorios al tablero (grid).
    - grid: matriz numpy que representa el tablero.
    - prob: probabilidad de que una celda se convierta en obstáculo.
    - start: coordenadas de inicio.
    - goal: coordenadas de la meta real.
    - fake_goals: lista de metas falsas que no deben ser bloqueadas.

    Retorna el grid modificado con obstáculos (1 = obstáculo, 0 = libre).
    """
    size_x, size_y = grid.shape
    for x in range(size_x):
        for y in range(size_y):
            if (x, y) != start and (x, y) != goal and (x,y) not in fake_goals:
                if random.random() < prob:
                    grid[x][y] = 1
                else:
                    grid[x][y] = 0
    return grid

def move_obstacles(grid, prob, start, goal, fake_goals):
    size_x, size_y = grid.shape
    obstacles = [(x, y) for x in range(size_x) for y in range(size_y) if grid[x][y] == 1]

    for x, y in obstacles:
        if random.random() < prob:
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            random.shuffle(directions)
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < size_x and 0 <= ny < size_y:
                    if grid[nx][ny] == 0 and (nx, ny) != start and (nx, ny) != goal and (nx, ny) not in fake_goals:
                        grid[nx][ny] = 1
                        grid[x][y] = 0
                        break
    return grid


def add_fake_goals(grid, exit_count, start, goal):
    size_x, size_y = grid.shape
    fake_goals = []
    for _ in range(exit_count - 1):
        fake_pos = (random.randint(0, size_x - 1), random.randint(0, size_y - 1))
        while fake_pos == start or fake_pos == goal or fake_pos in fake_goals:
            fake_pos = (random.randint(0, size_x - 1), random.randint(0, size_y - 1))
        fake_goals.append(fake_pos)
    return fake_goals

def map_value(x):
    """
    Ecuacion de una recta que retorna la probabilidad de obstáculos en proporcion al tamaño de la grilla.

    Parámetros
    ----------
    x : int
        Tamaño de la grilla.

    Retorna
    -------
    float
        Probabilidad de obstáculo (entre 0.1 y 0.4).
    """
    x1, x2 = 5, 50
    y1, y2 = 0.4, 0.05
    return y1 + (x - x1) * (y2 - y1) / (x2 - x1)

# mapping: 0=Arriba,1=Derecha,2=Abajo,3=Izquierda
MOVES = {
    0: (-1, 0), #Mover hacia arriba
    1: (0, 1),  #Mover hacia la derecha
    2: (1, 0),  #Mover hacia abajo
    3: (0, -1)  #Mover hacia la izquierda
}

class GeneticAlgorithm:
    """
    Implementa un algoritmo genético para encontrar un camino desde el inicio hasta la meta en un tablero con:
    - Obstáculos dinámicos.
    - Metas falsas.
    """
    def __init__(self, size, population_size, num_generations, chromosome_length, mutation_rate, crossover_rate):
        """
        Inicializa el algoritmo:
        - Crea el tablero, asigna inicio y meta.
        - Agrega metas falsas y obstáculos.
        - Genera la población inicial de cromosomas.
        """
        # Tablero
        self.size_board = size
        self.board = np.zeros((self.size_board, self.size_board), dtype=int)
        self.start = (int(size / 2),int(size / 2))
        self.goal = (random.randint(0, size - 1), random.randint(0, size - 1))
        self.boards = []
        while self.goal == self.start:
            self.goal = (random.randint(0, size - 1), random.randint(0, size - 1))
        self.fake_goals = add_fake_goals(self.board, 2, self.start, self.goal)
        self.board = add_random_obstacles(self.board, map_value(self.size_board), self.start, self.goal, self.fake_goals)
        self.population_size = population_size
        self.num_generations = num_generations
        self.chromosome_length = chromosome_length - 1 # Debe ser -1 porque son movimientos, y nuestro path debe tener largo chromosome_length
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.population = self.generate_initial_population()

    def generate_initial_population(self):
        """
        Genera la población inicial de cromosomas.
        Cada cromosoma es una secuencia de movimientos (arriba, derecha, abajo, izquierda).
        """
        population = []
        for i in range(self.population_size):
            chromosome = []
            for _ in range (self.chromosome_length):
                value = random.randint(0,3)
                # Mover hacia arriba
                if value == 0:
                    chromosome.append((-1, 0))
                # Mover hacia derecha
                elif value == 1:
                    chromosome.append((0, 1))
                # Mover hacia abajo
                elif value == 2:
                    chromosome.append((1, 0))
                # Mover hacia izquierda
                elif value == 3:
                    chromosome.append((0, -1))
            population.append(chromosome)
        return population

    def simulate_chromosome(self, chromosome, board):
        """
        Simula un cromosoma moviéndose en el tablero.
        Retorna:
        - Posición final
        - Camino recorrido
        - Penalizaciones
        - Cantidad de pasos
        - Si llegó a la meta
        - Evolución del tablero (con obstáculos dinámicos)
        """
        (x, y) = self.start
        path = []
        penalties = 0
        steps = 0
        reached = False
        i=0
        boards = [np.copy(board)]

        for gene in chromosome:
            x_mov, y_mov = gene
            new_x, new_y = x + x_mov, y + y_mov

            if not (0 <= new_x < self.size_board  and 0 <= new_y < self.size_board):
                penalties += 1
                path.append((x, y))
            else:
                cell = board[new_x][new_y]
                if cell == CellType.MURO:
                    penalties += 1
                    path.append((x,y))
                else:
                    x, y = new_x, new_y
                    path.append((x,y))
                    if (x,y) == self.goal:
                        reached = True
                        steps+=1
                        board = move_obstacles(board, 0.2, (x, y), self.goal, self.fake_goals)
                        boards.append(np.copy(board))
                        break
                    elif (x,y) == self.fake_goals:
                        penalties += 2
            steps+=1
            i+=1

            # Mover obstaculos
            board = move_obstacles(board, 0.2, (x, y), self.goal, self.fake_goals)
            boards.append(np.copy(board))

        return (x,y), path, penalties, steps, reached, boards

    def fitness_func(self, pos_final, penalties, steps, reached):
        """
        Calcula el fitness de un cromosoma:
        - Penaliza distancia a la meta (Manhattan).
        - Penaliza pasos extra y colisiones.
        - Recompensa fuertemente si alcanza la meta.
        """
        (x,y) = pos_final
        # Distancia Manhattan
        x_final, y_final = self.goal
        dist = abs(x - x_final) + abs (y - y_final)

        base_score = 1000
        score = base_score - (dist * 10) - (penalties * 20) - steps

        if reached:
            score += 10000 - (steps - 50)

        if score < 1:
            score = 1

        return score

    def select_parent(self, fitness_population):
        """
        Elige a los cromosomas, la probabilidad de ser elegido es proporcional al fitness.
        """
        total = sum(fitness_population)
        if total == 0:
            return random.choice(self.population)
        # pick determina donde cae la aguja en la ruleta, cada cormosoma tiene probabilidad proporcional a su fitness (los cromosomas buenos tienen mas probabilidad)
        pick = random.uniform(0, total) # numero aleatorio entre 0 y la suma de todos los fitnesses
        current = 0
        for i in range(self.population_size):
            chromosome = self.population[i]
            fitness = fitness_population[i]

            current += fitness
            if current > pick:
                return chromosome

        return self.population[-1]

    def crossover(self, parent1, parent2):
        """
        Cruce de un punto:
        - Combina genes de dos padres en dos hijos.
        """
        if random.random() < self.crossover_rate:
            # Se elige un punto de corte aleatorio
            idx = random.randint(1, self.chromosome_length - 1)
            child1 = parent1[:idx] + parent2[idx:]
            child2 = parent2[:idx] + parent1[idx:]
        else:
            # Caso que la probabilidad falla se copian tal cual
            return parent1[:], parent2[:]

        return child1, child2

    def mutate(self, chromosome):
        """
        Aplica mutación en algunos genes de un cromosoma.
        Sustituye el movimiento por otro aleatorio con cierta probabilidad.
        """
        c = chromosome[:]
        for i in range(self.chromosome_length):
            if random.random() < self.mutation_rate:
                value = random.randint(0,3)
                # Mover hacia arriba
                if value == 0:
                    chromosome.append((-1, 0))
                # Mover hacia derecha
                elif value == 1:
                    chromosome.append((0, 1))
                # Mover hacia abajo
                elif value == 2:
                    chromosome.append((1, 0))
                # Mover hacia izquierda
                elif value == 3:
                    chromosome.append((0, -1))
        return c

    def run(self):
        """
        Ejecuta el algoritmo genético:
        - Evalúa la población.
        - Selecciona padres.
        - Aplica cruce y mutación.
        - Devuelve el mejor camino encontrado.
        """
        # Tablero
        best_fit = -float('inf')
        best_chromosome = None
        reached_population = []
        fitness_population = []

        for i in range(self.num_generations):
            # Calcular fitness de cada cromosoma, guardar si llego a la meta o no
            j=0
            for chromosome in self.population:

                (x,y), path, penalties, steps, reached, boards = self.simulate_chromosome(chromosome, np.copy(self.board))
                score = self.fitness_func((x,y), penalties, steps, reached)
                j+=1

                if reached:
                    best_fit = score
                    best_chromosome = chromosome[:] # guardamos una copia, chromosome original puede variar
                    best_path = path[:]
                    self.boards = [np.copy(b) for b in boards]
                    return (self.start, self.goal, best_path, self.boards, self.fake_goals)

                elif score>best_fit:
                    best_fit = score
                    best_chromosome = chromosome[:]
                    best_path = path[:]
                    self.boards = [np.copy(b) for b in boards]


            new_population = []
            while len(new_population) < self.population_size:
                parent1 = self.select_parent(fitness_population)
                parent2 = self.select_parent(fitness_population)
                child1, child2 = self.crossover(parent1, parent2)
                child1 = self.mutate(child1)
                child2 = self.mutate(child2)
                new_population.append(child1)
                if len(new_population) < self.population_size:
                    new_population.append(child2)


        return (self.start, self.goal, best_path, self.boards, self.fake_goals)