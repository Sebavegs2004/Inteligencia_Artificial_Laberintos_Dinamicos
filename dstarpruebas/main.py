import heapq
import math
import numpy as np
import random
import os


def add_random_obstacles(grid, prob, start, goal):
    size_x, size_y = grid.shape
    for x in range(size_x):
        for y in range(size_y):
            if (x, y) != start and (x, y) not in goal:
                if random.random() < prob:
                    grid[x][y] = 1
                else:
                    grid[x][y] = 0
    return grid


def move_obstacles(grid, prob, start, goal):
    size_x, size_y = grid.shape
    obstacles = [(x, y) for x in range(size_x) for y in range(size_y) if grid[x][y] == 1]

    for x, y in obstacles:
        if random.random() < prob:
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            random.shuffle(directions)
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < size_x and 0 <= ny < size_y:
                    if grid[nx][ny] == 0 and (nx, ny) != start and (nx, ny) not in goal:
                        grid[nx][ny] = 1
                        grid[x][y] = 0
                        break
    return grid


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


class PriorityQueue:
    def __init__(self):
        self.heap = []
        self.entry_finder = {}  # nodo -> (k1, k2, nodo)

    def insert(self, node, priority):
        entry = (priority[0], priority[1], node)
        self.entry_finder[node] = entry
        heapq.heappush(self.heap, entry)

    def update(self, node, priority):
        self.remove(node)
        self.insert(node, priority)

    def remove(self, node):
        if node in self.entry_finder:
            entry = self.entry_finder.pop(node)
            self.heap.remove(entry)
            heapq.heapify(self.heap)

    def pop(self):
        while self.heap:
            k1, k2, node = heapq.heappop(self.heap)
            if node in self.entry_finder and self.entry_finder[node] == (k1, k2, node):
                self.entry_finder.pop(node)
                return node
        return None

    def top(self):
        while self.heap:
            k1, k2, node = self.heap[0]
            if node in self.entry_finder:
                return node
            else:
                heapq.heappop(self.heap)
        return None

    def top_key(self):
        while self.heap:
            k1, k2, node = self.heap[0]
            if node in self.entry_finder:
                return (k1, k2)
            else:
                heapq.heappop(self.heap)
        return (math.inf, math.inf)

    def contains(self, node):
        return node in self.entry_finder

    def empty(self):
        return len(self.entry_finder) == 0


class DStarLite:
    def __init__(self, grid, start, goal):
        self.grid = grid
        self.start = start
        self.goal = goal
        self.k_m = 0
        self.s_last = start

        self.g = {}
        self.rhs = {}

        self.U = PriorityQueue()

        for x in range(len(grid)):
            for y in range(len(grid[0])):
                self.g[(x, y)] = math.inf
                self.rhs[(x, y)] = math.inf

        self.rhs[goal] = 0
        self.U.insert(goal, self.calculate_key(goal))

    def calculate_key(self, s):
        val = min(self.g[s], self.rhs[s])
        return (val + manhattan(self.start, s) + self.k_m, val)

    def neighbors(self, s):
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
        if self.grid[v[0]][v[1]] == 1:  # obstáculo
            return math.inf
        return 1  # coste uniforme

    def update_vertex(self, u):
        if u != self.goal:
            self.rhs[u] = min([self.cost(u, s) + self.g[s] for s in self.neighbors(u)] or [math.inf])
        if self.U.contains(u):
            self.U.remove(u)
        if self.g[u] != self.rhs[u]:
            self.U.insert(u, self.calculate_key(u))

    def compute_shortest_path(self):
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

    def plan(self):
        self.compute_shortest_path()
        if self.g[self.start] == math.inf:
            return None

        path = [self.start]
        s = self.start
        while s != self.goal:
            min_cost = math.inf
            next_s = None
            for sp in self.neighbors(s):
                val = self.cost(s, sp) + self.g[sp]
                if val < min_cost:
                    min_cost = val
                    next_s = sp
            if next_s is None:
                return None
            s = next_s
            path.append(s)
        return path


def run_DStarLite(size, num_goals, prob_muro, prob_mover):
        while True:
            grid = np.zeros((size, size), dtype=int)
            start = (0, 0)
            current_start = start
            goals = []
            for _ in range(num_goals):
                g = (random.randint(0, size-1), random.randint(0, size-1))
                while g == start:
                    g = (random.randint(0, size-1), random.randint(0, size-1))
                goals.append(g)
            real_goal = random.choice(goals)
            fake_goals = np.copy(goals)
            grids = []
            jugadas = []
            grid = add_random_obstacles(grid, prob_muro, start=current_start, goal=goals)
            grids.append(np.copy(grid))
            remaining_goals = goals.copy()
            while remaining_goals:
                goal = random.choice(remaining_goals)
                dstar = DStarLite(grid, current_start, goal)
                dstar.compute_shortest_path()

                if dstar.g[current_start] == math.inf:
                    remaining_goals.remove(goal)
                    continue

                def get_next_from_g(dstar, s):
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

                    grid = move_obstacles(grid, prob_mover, start=current_start, goal=goals)
                    grids.append(np.copy(grid))

                    dstar.k_m += manhattan(dstar.s_last, current_start)
                    dstar.s_last = current_start
                    dstar.start = current_start

                    for x in range(size):
                        for y in range(size):
                            if grid[x][y] != dstar.grid[x][y]:
                                dstar.grid[x][y] = grid[x][y]
                                dstar.update_vertex((x, y))

                    dstar.compute_shortest_path()

                if current_start == real_goal:
                    mask = [not np.array_equal(g, real_goal) for g in fake_goals]
                    fake_goals = fake_goals[mask]
                    return start, real_goal, jugadas, grids, fake_goals
                else:
                    remaining_goals.remove(goal)


def map_value(x):
    x1, x2 = 5, 50
    y1, y2 = 0.4, 0.1
    return y1 + (x - x1) * (y2 - y1) / (x2 - x1)

import time
import csv

if __name__ == "__main__":
    sizes = {
        10: 2,
        25: 4,
        50: 8
    }
    prob_muros_list = [0.1, 0.3, 0.5]
    prob_mover_list = [0.1, 0.25, 0.5, 0.9]
    repeticiones = 200

    for size, num_goals in sizes.items():
        for prob_muros in prob_muros_list:
            for prob_mover in prob_mover_list:
                results = []
                print(f"\n🔹 Ejecutando size={size}, goals={num_goals}, muros={prob_muros}, mover={prob_mover}")

                for i in range(repeticiones):
                    start_time = time.perf_counter()
                    start, real_goal, jugadas, grids, fake_goals = run_DStarLite(
                        size, num_goals, prob_muros, prob_mover
                    )
                    end_time = time.perf_counter()
                    execution_time = end_time - start_time
                    results.append([execution_time, len(jugadas)])
                    print(f"Ejecución {i+1}: Tiempo={execution_time:.6f}s, Jugadas={len(jugadas)}")

                filename = f"size{size}_muros{prob_muros}_mover{prob_mover}.csv"
                with open(filename, mode="w", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow(["Tiempo (s)", "Jugadas"])
                    writer.writerows(results)