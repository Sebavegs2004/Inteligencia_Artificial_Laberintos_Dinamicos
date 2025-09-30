import heapq
import math
import numpy as np
import random
import os


def add_random_obstacles(grid, prob, start, goal): 
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
            if (x, y) != start and (x, y) not in goal: # Evita que los obstaculos se coloquen en las posibles salidas.
                if random.random() < prob:
                    grid[x][y] = 1
                else:
                    grid[x][y] = 0
    return grid


def move_obstacles(grid, prob, start, goal): 
    """
    Mueve obstáculos aleatoriamente dentro del tablero.
    - prob: probabilidad de que un obstáculo se mueva.
    - start, goal, fake_goals no pueden ser ocupados por obstáculos.

    Retorna el grid actualizado con nuevos movimientos de obstáculos.
    """
    size_x, size_y = grid.shape
    obstacles = [(x, y) for x in range(size_x) for y in range(size_y) if grid[x][y] == 1]

    for x, y in obstacles:
        if random.random() < prob:
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            random.shuffle(directions)
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < size_x and 0 <= ny < size_y:
                    if grid[nx][ny] == 0 and (nx, ny) != start and (nx, ny) not in goal: # e
                        grid[nx][ny] = 1
                        grid[x][y] = 0
                        break
    return grid


def manhattan(a, b):
    """ Calcula la distancia de Manhattan entre dos posiciones (a, b). """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


class PriorityQueue:
    """
    Cola de prioridades para gestionar los nodos de D* Lite.

    Usa heapq y mantiene referencias para actualizar nodos ya insertados.
    """ 
    def __init__(self):
        self.heap = []
        self.entry_finder = {}  # nodo -> (k1, k2, nodo)

    def insert(self, node, priority):
        """ Inserta un nodo con su prioridad (k1, k2). """
        entry = (priority[0], priority[1], node)
        self.entry_finder[node] = entry
        heapq.heappush(self.heap, entry)

    def update(self, node, priority):
        """ Actualiza la prioridad de un nodo existente. """
        self.remove(node)
        self.insert(node, priority)

    def remove(self, node):
        """ Elimina un nodo de la cola. """
        if node in self.entry_finder:
            entry = self.entry_finder.pop(node)
            self.heap.remove(entry)
            heapq.heapify(self.heap)

    def pop(self):
        """ Extrae el nodo con menor prioridad. """
        while self.heap:
            k1, k2, node = heapq.heappop(self.heap)
            if node in self.entry_finder and self.entry_finder[node] == (k1, k2, node):
                self.entry_finder.pop(node)
                return node
        return None

    def top(self):
        """ Devuelve el nodo con mayor prioridad sin eliminarlo. """
        while self.heap:
            k1, k2, node = self.heap[0]
            if node in self.entry_finder:
                return node
            else:
                heapq.heappop(self.heap)
        return None

    def top_key(self):
        """ Devuelve la clave (k1, k2) del nodo en la cima. """
        while self.heap:
            k1, k2, node = self.heap[0]
            if node in self.entry_finder:
                return (k1, k2)
            else:
                heapq.heappop(self.heap)
        return (math.inf, math.inf)

    def contains(self, node):
        """ Verifica si un nodo está en la cola. """
        return node in self.entry_finder

    def empty(self):
        """ Verifica si la cola está vacía. """
        return len(self.entry_finder) == 0


class DStarLite:
    """
    Implementación del algoritmo D* Lite para búsqueda de caminos en entornos dinámicos.

    Atributos
    ---------
    grid : np.ndarray
        Grilla con obstáculos.
    start : tuple
        Posición inicial del agente.
    goal : tuple
        Meta objetivo.
    g : dict
        Costos acumulados.
    rhs : dict
        Costos inmediatos esperados.
    U : PriorityQueue
        Cola de prioridades con nodos pendientes.
    """
    def __init__(self, grid, start, goal):
        self.grid = grid
        self.start = start
        self.goal = goal
        self.k_m = 0
        self.s_last = start

        # Diccionarios para valores de g y rhs
        self.g = {}
        self.rhs = {}
        self.U = PriorityQueue() # Cola de prioridades

        for x in range(len(grid)):
            for y in range(len(grid[0])):
                self.g[(x, y)] = math.inf
                self.rhs[(x, y)] = math.inf

        self.rhs[goal] = 0
        self.U.insert(goal, self.calculate_key(goal))

    def calculate_key(self, s):
        """ Calcula la clave (k1, k2) para un nodo según D* Lite. """
        val = min(self.g[s], self.rhs[s])
        return (val + manhattan(self.start, s) + self.k_m, val)

    def neighbors(self, s):
        """ Devuelve los vecinos libres de un nodo. """
        x, y = s
        moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        result = []
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(self.grid) and 0 <= ny < len(self.grid[0]):
                if self.grid[nx][ny] == 0:  # libre
                    result.append((nx, ny))
        return result

    def cost(self, u, v):
        """ Retorna el costo de moverse de u a v (∞ si hay obstáculo). """
        if self.grid[v[0]][v[1]] == 1:  # obstáculo
            return math.inf
        return 1  # coste uniforme

    def update_vertex(self, u):
        """ Actualiza un vértice en base a sus vecinos. """
        if u != self.goal:
            self.rhs[u] = min([self.cost(u, s) + self.g[s] for s in self.neighbors(u)] or [math.inf])
        if self.U.contains(u):
            self.U.remove(u)
        if self.g[u] != self.rhs[u]:
            self.U.insert(u, self.calculate_key(u))

    def compute_shortest_path(self):
        """ Recalcula el camino más corto según cambios en el entorno. """
        while (self.U.top_key() < self.calculate_key(self.start)) or (self.rhs[self.start] != self.g[self.start]):
            u = self.U.top()
            k_old = self.U.top_key()
            k_new = self.calculate_key(u)

            if k_old < k_new:
                self.U.update(u, k_new)
            elif self.g[u] > self.rhs[u]:
                self.g[u] = self.rhs[u]
                self.U.remove(u)
                for s in self.neighbors(u):
                    self.update_vertex(s)
            else:
                g_old = self.g[u]
                self.g[u] = math.inf
                for s in self.neighbors(u) + [u]:
                    if self.rhs[s] == self.cost(s, u) + g_old:
                        if s != self.goal:
                            self.rhs[s] = min([self.cost(s, sp) + self.g[sp] for sp in self.neighbors(s)] or [math.inf])
                    self.update_vertex(s)


def run_DStarLite(size, num_goals=5):
        """
        Ejecuta D* Lite en una grilla de tamaño dado con metas múltiples.

        Parámetros
        ----------
        size : int
            Tamaño de la grilla (size x size).
        num_goals : int
            Número de metas a generar (una real y el resto falsas).

        Retorna
        -------
        start : tuple
            Posición inicial.
        real_goal : tuple
            Meta verdadera alcanzada.
        jugadas : list[tuple]
            Movimientos realizados por el agente.
        grids : list[np.ndarray]
            Estados de la grilla a lo largo del recorrido.
        fake_goals : np.ndarray
            Metas descartadas.
        """
        while True:
            grid = np.zeros((size, size), dtype=int)
            start = (0, 0)
            current_start = start
            goals = []
            for _ in range(num_goals): # Selección de metas
                g = (random.randint(0, size-1), random.randint(0, size-1))
                while g == start:
                    g = (random.randint(0, size-1), random.randint(0, size-1))
                goals.append(g)
            real_goal = random.choice(goals)
            fake_goals = np.copy(goals)
            grids = []
            jugadas = []
            grid = add_random_obstacles(grid, prob=map_value(size), start=current_start, goal=goals) # Añadir obstáculos iniciales
            grids.append(np.copy(grid))
            remaining_goals = goals.copy()
            while remaining_goals:
                goal = random.choice(remaining_goals)
                dstar = DStarLite(grid, current_start, goal)
                dstar.compute_shortest_path()

                if dstar.g[current_start] == math.inf:
                    remaining_goals.remove(goal)
                    continue

                def get_next_from_g(dstar, s): # Devuelve el vecino con menor costo desde el estado s. 
                    min_cost = math.inf
                    next_s = None
                    for sp in dstar.neighbors(s):
                        cost = dstar.cost(s, sp) + dstar.g[sp]
                        if cost < min_cost:
                            min_cost = cost
                            next_s = sp
                    return next_s

                reached_goal = False
                while current_start != goal:
                    next_s = get_next_from_g(dstar, current_start)
                    if next_s is None:
                        break
                    current_start = next_s
                    jugadas.append(current_start)

                    grid = move_obstacles(grid, prob=0.4, start=current_start, goal=goals) # Mover obstáculos 
                    grids.append(np.copy(grid))

                    # Actualizar información de D* Lite
                    dstar.k_m += manhattan(dstar.s_last, current_start)
                    dstar.s_last = current_start
                    dstar.start = current_start

                    # Detectar cambios en la grilla
                    for x in range(size):
                        for y in range(size):
                            if grid[x][y] != dstar.grid[x][y]:
                                dstar.grid[x][y] = grid[x][y]
                                dstar.update_vertex((x, y))

                    dstar.compute_shortest_path()
                    if current_start == real_goal:
                        break


                if current_start == real_goal:
                    mask = [not np.array_equal(g, real_goal) for g in fake_goals]
                    fake_goals = fake_goals[mask]
                    return start, real_goal, jugadas, grids, fake_goals
                else:
                    remaining_goals.remove(goal)


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
    y1, y2 = 0.4, 0.1
    return y1 + (x - x1) * (y2 - y1) / (x2 - x1)
