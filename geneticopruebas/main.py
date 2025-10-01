import random
import numpy as np
from constants import CellType

def add_random_obstacles(grid, prob, start, goal, fake_goals):
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
    x1, x2 = 5, 50
    y1, y2 = 0.5, 0.05
    return y1 + (x - x1) * (y2 - y1) / (x2 - x1)

# mapping: 0=Arriba,1=Derecha,2=Abajo,3=Izquierda
MOVES = {
    0: (-1, 0), #Mover hacia arriba
    1: (0, 1),  #Mover hacia la derecha
    2: (1, 0),  #Mover hacia abajo
    3: (0, -1)  #Mover hacia la izquierda
}

class GeneticAlgorithm:
    def __init__(self, size, population_size, num_generations, chromosome_length, mutation_rate, crossover_rate, num_goals, prob_muros, prob_mover):
        # Crear tablero
        self.size_board = size
        self.board = np.zeros((self.size_board, self.size_board), dtype=int)
        self.start = (int(size / 2),int(size / 2))
        self.boards = [] # Lista para guardar el historial de los distintos tableros en el recorrido de un cromosoma
        # Determinar posicion de la meta
        self.goal = (random.randint(0, size - 1), random.randint(0, size - 1))
        while self.goal == self.start:
            self.goal = (random.randint(0, size - 1), random.randint(0, size - 1))
        # Añadir salidas falsas al tablero
        self.fake_goals = add_fake_goals(self.board,  num_goals-1, self.start, self.goal)
        # Añadir obstaculos al tablero
        self.board = add_random_obstacles(self.board, prob_muros, self.start, self.goal, self.fake_goals)
        self.prob_muros = prob_muros
        self.prob_mover = prob_mover

        # Parametros del algoritmo genetico
        self.population_size = population_size           # Cantidad de cromosomas en cada generacion
        self.num_generations = num_generations           # Número de generaciones (ciclos evolutivos) que se van a ejecutar
        self.chromosome_length = chromosome_length - 1   # Cantidad de movimientos en cada cromosoma
        self.crossover_rate = crossover_rate             # Probabilidad de cruce entre dos cromosomas
        self.mutation_rate = mutation_rate               # Probabilidad de mutacion de un gen

        # Seteamos poblacion inicial
        self.population = self.generate_initial_population()

    # Funcion que genera poblacion inicial con cromosomas de movimientos aleatorios
    def generate_initial_population(self):
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

    # Funcion para simular el recorrido de un cromosoma en el tablero
    def simulate_chromosome(self, chromosome, board):
        (x, y) = self.start
        path = []
        penalties = 0
        steps = 0
        reached = False
        boards = [np.copy(board)]

        for gene in chromosome:
            x_mov, y_mov = gene
            new_x, new_y = x + x_mov, y + y_mov # Posicion del agente luego de aplicar el movimiento del cromosoma
            # Comprobar que al moverse no sobrepasa el limite de tablero
            if not (0 <= new_x < self.size_board  and 0 <= new_y < self.size_board):
                penalties += 1
                path.append((x, y))
            else:
                cell = board[new_x][new_y]
                # Muro, penalizamos y no avanzamos
                if cell == CellType.MURO:
                    penalties += 1
                    path.append((x,y))
                # Si no es muro, podemos avanzar
                else:
                    x, y = new_x, new_y
                    path.append((x,y))
                    # Salida real, termina la busqueda
                    if (x,y) == self.goal:
                        reached = True
                        steps+=1
                        board = move_obstacles(board, self.prob_mover, (x, y), self.goal, self.fake_goals)
                        boards.append(np.copy(board))
                        break
                    # Salida trampa, penalizamos
                    elif (x,y) in self.fake_goals:
                        penalties += 2
            steps+=1

            # Mover obstaculos
            board = move_obstacles(board, self.prob_mover, (x, y), self.goal, self.fake_goals)
            boards.append(np.copy(board))

        return (x,y), path, penalties, steps, reached, boards

    # Funcion retorna fitness (medida de que tan buena es la solucion de un cromosoma)
    def fitness_func(self, pos_final, penalties, steps, reached):
        (x,y) = pos_final
        # Distancia Manhattan, sirve como heuristica de que tan cerca quedo el cromosoma de la salida real
        x_final, y_final = self.goal
        dist = abs(x - x_final) + abs (y - y_final)

        base_score = 1000
        # score = valor base - (distancia*valor que aumente impacto de la ditancia) - (penalizaciones*valor que aumente impacto de penalizaciones) - pasos
        score = base_score - (dist * 10) - (penalties * 20) - steps
        if reached:
            # Si llegó, se recompensa
            score += 10000

        if score < 1:
            # fitness debe ser positivo para la selección por ruleta.
            score = 1
        return score

    # Funcion para seleccionar un cromosoma padre
    def select_parent(self, fitness_population):
        total = sum(fitness_population)
        if total == 0:
            return random.choice(self.population)
        # Seleccion por ruleta: probabilidad proporcional al fitness
        pick = random.uniform(0, total)
        current = 0
        for i in range(self.population_size):
            chromosome = self.population[i]
            fitness = fitness_population[i]

            current += fitness
            if current > pick:
                return chromosome

        return self.population[-1]

    # Funcion que cruza dos cromosomas si se cumple la probabilidad
    def crossover(self, parent1, parent2):
        if random.random() < self.crossover_rate:
            # Se elige un punto de corte aleatorio
            idx = random.randint(1, self.chromosome_length - 1)
            child1 = parent1[:idx] + parent2[idx:]
            child2 = parent2[:idx] + parent1[idx:]
        else:
            # Caso que la probabilidad falla se copian tal cual
            child1, child2 = parent1[:], parent2[:]

        return child1, child2

    # Funcion que muta un gen del cromosoma por un movimiento aleatorio.
    def mutate(self, chromosome):
        c = chromosome[:]
        for i in range(self.chromosome_length):
            if random.random() < self.mutation_rate:
                value = random.randint(0,3)
                # Mover hacia arriba
                if value == 0:
                    c[i] = (-1, 0)
                # Mover hacia derecha
                elif value == 1:
                    c[i] = (0, 1)
                # Mover hacia abajo
                elif value == 2:
                    c[i] = (1, 0)
                # Mover hacia izquierda
                elif value == 3:
                    c[i] = (0, -1)
        return c

    # Función que ejecuta el algoritmo genético
    def run(self):
        best_fit = -float('inf')

        for i in range(self.num_generations):
            fitness_population = []
            for chromosome in self.population:
                # Simular el recorrido de un cromosoma
                (x,y), path, penalties, steps, reached, boards = self.simulate_chromosome(chromosome, np.copy(self.board))
                # Fitness del cromosoma
                score = self.fitness_func((x,y), penalties, steps, reached)
                fitness_population.append(score)

                # Si un cromosoma llego a la meta terminamos la ejecución.
                if reached:
                    best_path = path[:]
                    self.boards = [np.copy(b) for b in boards] # se guarda el historial de tableros que tuvo el recorrido del cromosoma
                    return (self.start, self.goal, best_path, self.boards, self.fake_goals)

                # Se actualiza cada vez el mejor cromosoma
                elif score>best_fit:
                    best_fit = score
                    best_path = path[:]
                    self.boards = [np.copy(b) for b in boards]

            # Reemplazar la población
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

            # Actualizar población para la próxima generacion
            self.population = new_population

        return (self.start, self.goal, best_path, self.boards, self.fake_goals)




import time
import csv

if __name__ == "__main__":
    print("ola")
    sizes = {
        25: 4,
    }
    prob_muros_list = [0.1, 0.3, 0.5]
    prob_mover_list = [0.1, 0.25, 0.5, 0.9]
    repeticiones = 50

    for size, num_goals in sizes.items():
        for prob_muros in prob_muros_list:
            for prob_mover in prob_mover_list:
                results = []
                print(f"\n:small_blue_diamond: Ejecutando size={size}, goals={num_goals}, muros={prob_muros}, mover={prob_mover}")

                for i in range(repeticiones):
                    start_time = time.perf_counter()  # :arrow_left: mejor precisión
                    population_size = 40
                    num_generations = 80
                    chromosome_length = 100
                    mutation_rate = 0.07
                    crossover_rate = 0.75

                    ga = GeneticAlgorithm(size, population_size, num_generations,
                                          chromosome_length, mutation_rate, crossover_rate, num_goals, prob_muros, prob_mover)

                    start, goal, best_chromosome, boards, fake_goals = ga.run()

                    end_time = time.perf_counter()
                    execution_time = end_time - start_time
                    results.append([execution_time, len(best_chromosome)])
                    print(f"Ejecución {i+1}: Tiempo={execution_time:.6f}s, Jugadas={len(best_chromosome)}")

                # Nombre de archivo único para cada combinación
                filename = f"size{size}_muros{prob_muros}_mover{prob_mover}.csv"
                with open(filename, mode="w", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow(["Tiempo (s)", "Jugadas"])
                    writer.writerows(results)

                print(f":white_check_mark: Resultados guardados en {filename}")