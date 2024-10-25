import sys
from queue import PriorityQueue

sys.path.append('/Users/simonebilleri/.python-lib/aima-python')

from aima3.search import Problem

class UniformColoring(Problem):
    def __init__(self, initial, goal_color, start_position, color_costs):
        """
        Inizializza il problema di Uniform Coloring con la testina.
        
        :param initial: Stato iniziale rappresentato come (griglia, posizione_testina).
        :param goal_color: Il colore obiettivo che tutte le celle devono avere alla fine.
        :param start_position: La posizione iniziale della testina (dove si trova 'T').
        :param color_costs: Dizionario dei costi di colorazione per ogni colore.
        """
        super().__init__(initial)
        self.goal_color = goal_color
        self.start_position = start_position
        self.color_costs = color_costs

    def actions(self, state):
        """
        Genera una lista di azioni possibili nello stato attuale.
        """
        actions = []
        grid, (x, y) = state
        rows, cols = len(grid), len(grid[0])

        if x > 0: actions.append('Up')
        if x < rows - 1: actions.append('Down')
        if y > 0: actions.append('Left')
        if y < cols - 1: actions.append('Right')

        if grid[x][y] != self.goal_color and (x, y) != self.start_position:
            actions.append('Paint')

        return actions

    def result(self, state, action):
        """
        Applica un'azione a uno stato e restituisce il nuovo stato risultante.
        """
        grid, (x, y) = state
        new_grid = [list(row) for row in grid]  # Crea una copia della griglia corrente
        
        if action == 'Up':
            new_position = (x - 1, y)
        elif action == 'Down':
            new_position = (x + 1, y)
        elif action == 'Left':
            new_position = (x, y - 1)
        elif action == 'Right':
            new_position = (x, y + 1)
        elif action == 'Paint':
            new_grid[x][y] = self.goal_color
            new_position = (x, y)

        new_grid[self.start_position[0]][self.start_position[1]] = 'T'
        return (tuple("".join(row) for row in new_grid), new_position)

    def goal_test(self, state):
        """
        Verifica se lo stato corrente corrisponde allo stato obiettivo.
        """
        grid, _ = state
        for x, row in enumerate(grid):
            for y, cell in enumerate(row):
                if (x, y) != self.start_position and cell != self.goal_color:
                    return False
        return True

    def path_cost(self, c, state1, action, state2):
        """
        Calcola il costo di un percorso tra due stati.
        """
        if action in ['Up', 'Down', 'Left', 'Right']:
            return c + 1  # Ogni movimento costa 1
        elif action == 'Paint':
            return c + self.color_costs[self.goal_color]
        else:
            return c

def find_starting_position(grid):
    """
    Trova la posizione iniziale della testina cercando la lettera 'T' nella griglia.
    Se ci sono più testine, solleva un errore.
    """
    positions = [(x, y) for x, row in enumerate(grid) for y, cell in enumerate(row) if cell == 'T']
    
    if len(positions) == 0:
        raise ValueError("Errore: 'T' non trovato nella griglia.")
    elif len(positions) > 1:
        raise ValueError("Errore: Più di una testina ('T') trovata nella griglia.")
    
    return positions[0]

def print_grid(grid):
    """
    Stampa la griglia in modo leggibile.
    """
    for row in grid:
        print(" ".join(row))
    print()

def calculate_total_cost(grid, color, start_position, color_costs):
    """
    Calcola il costo totale per uniformare tutte le celle della griglia a un colore specifico,
    utilizzando UCS per espandere i colori confinanti solo dopo aver calcolato il costo.
    """
    print("Calcolo del costo totale per colorare la griglia in", color)
    rows, cols = len(grid), len(grid[0])
    visited = set()  # Traccia delle celle già visitate
    total_cost = 0

    # Coda con priorità per UCS, inizia con la posizione di partenza
    frontier = PriorityQueue()
    frontier.put((0, start_position))

    while not frontier.empty():
        cost, (x, y) = frontier.get()

        # Salta se la cella è già stata visitata
        if (x, y) in visited:
            continue

        # Segna la cella come visitata
        visited.add((x, y))

        # Calcola il costo solo se il colore è diverso
        current_color = grid[x][y]
        if current_color != color:
            step_cost = color_costs[color]
            total_cost += step_cost  # Aggiungi il costo per colorare la cella

        # Espandi verso i vicini solo dopo aver calcolato il costo
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Up, Down, Left, Right
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and (nx, ny) not in visited:
                # Inserisci il vicino nella coda con il costo accumulato
                frontier.put((cost + 1, (nx, ny)))  # Ogni movimento ha un costo di 1
    return total_cost

def find_optimal_goal_color(grid, start_position, color_costs):
    """
    Trova il colore obiettivo più conveniente per uniformare la griglia.
    """
    colors = color_costs.keys() # Lista dei colori disponibili
    costs = {color: calculate_total_cost(grid, color, start_position, color_costs) for color in colors} # Calcola i costi per ogni colore
    optimal_color = min(costs, key=costs.get)
    print("Costi per ogni colore:", costs)
    print("Colore obiettivo ottimale:", optimal_color)
    return optimal_color

def uniform_cost_search(problem):
    """
    Implementa l'algoritmo di Uniform Cost Search (UCS) e salva solo i passaggi della soluzione ottimale.
    """
    node = (0, problem.initial, [])  # (costo, stato, percorso delle azioni)
    frontier = PriorityQueue()
    frontier.put(node)
    explored = set()
    optimal_solution_steps = []  # Lista per memorizzare i passaggi della soluzione ottimale

    while not frontier.empty():
        cost, state, path = frontier.get()

        if problem.goal_test(state):
            optimal_solution_steps.append((state, cost, path))  # Aggiunge solo gli stati della soluzione ottimale
            return path, cost, optimal_solution_steps

        explored.add(state)
        for action in problem.actions(state):
            child = problem.result(state, action)
            new_cost = problem.path_cost(cost, state, action, child)
            new_path = path + [action]

            if child not in explored and all(child != item[1] for item in frontier.queue):
                frontier.put((new_cost, child, new_path))
            elif any(child == item[1] and new_cost < item[0] for item in frontier.queue):
                for i, (old_cost, old_state, _) in enumerate(frontier.queue):
                    if old_state == child and new_cost < old_cost:
                        frontier.queue[i] = (new_cost, child, new_path)
                        break
                frontier.queue = sorted(frontier.queue)
    return None

def a_star_search(problem, heuristic):
    """
    Implementa l'algoritmo di A* Search e salva solo i passaggi della soluzione ottimale.
    """
    node = (heuristic(problem.initial), problem.initial, [])  # (f(n), stato, percorso delle azioni)
    frontier = PriorityQueue()
    frontier.put((0 + heuristic(problem.initial), 0, problem.initial, []))  # (f(n), costo, stato, percorso)
    explored = set()
    optimal_solution_steps = []  # Lista per memorizzare i passaggi della soluzione ottimale

    while not frontier.empty():
        f, g, state, path = frontier.get()

        if problem.goal_test(state):
            optimal_solution_steps.append((state, g, path))  # Aggiunge solo gli stati della soluzione ottimale
            return path, g, optimal_solution_steps  # Ritorna il costo effettivo g

        explored.add(state)
        for action in problem.actions(state):
            child = problem.result(state, action)
            new_cost = problem.path_cost(g, state, action, child)  # Usa g come costo reale
            h_cost = new_cost + heuristic(child)  # f(n) = g(n) + h(n)
            new_path = path + [action]

            if child not in explored and all(child != item[2] for item in frontier.queue):
                frontier.put((h_cost, new_cost, child, new_path))
            elif any(child == item[2] and h_cost < item[0] for item in frontier.queue):
                for i, (old_f, old_g, old_state, _) in enumerate(frontier.queue):
                    if old_state == child and h_cost < old_f:
                        frontier.queue[i] = (h_cost, new_cost, child, new_path)
                        break
                frontier.queue = sorted(frontier.queue)
            
    return None

def print_optimal_solution_steps(optimal_solution_steps):
    """
    Stampa i passaggi della soluzione ottimale.
    """
    for i, (state, cost, path) in enumerate(optimal_solution_steps):
        grid, _ = state
        print(f"Passaggio {i + 1}, Costo: {cost}, Azioni: {' -> '.join(path)}")
        print_grid(grid)

def heuristic_manhattan_distance(state):
    """
    Euristica della Distanza di Manhattan. Somma la distanza di Manhattan per tutte le celle da colorare rispetto alla posizione della testina.
    """
    grid, (tx, ty) = state
    total_distance = 0
    for x, row in enumerate(grid):
        for y, cell in enumerate(row):
            if cell != problem.goal_color:
                total_distance += abs(tx - x) + abs(ty - y)
    return total_distance

# Modifica nel main per scegliere l'algoritmo
# Modifica nel main per scegliere l'algoritmo
if __name__ == '__main__':
    initial_grid = ['GTG', 'BGB', 'YBG', 'GYB', 'GBY', 'BBB', 'GYB', 'BYG']
    
    try:
        start_position = find_starting_position(initial_grid)  # Trova la posizione di 'T'
        color_costs = {'B': 1, 'Y': 2, 'G': 3}
        optimal_goal_color = find_optimal_goal_color(initial_grid, start_position, color_costs)
        
        initial_state = (tuple(initial_grid), start_position)
        problem = UniformColoring(initial=initial_state, goal_color=optimal_goal_color, start_position=start_position, color_costs=color_costs)
        
        # Scelta dell'algoritmo
        algorithm_choice = input("Scegli l'algoritmo da utilizzare (UCS o A*): ").strip().lower()
        
        if algorithm_choice == 'ucs':
            path, total_cost, optimal_solution_steps = uniform_cost_search(problem)
        elif algorithm_choice == 'a*':
            path, total_cost, optimal_solution_steps = a_star_search(problem, heuristic_manhattan_distance)
        else:
            raise ValueError("Algoritmo non riconosciuto. Scegli 'UCS' o 'A*'.")

        if path:
            print("Solution found with cost:", total_cost)
            print_optimal_solution_steps(optimal_solution_steps)  # Stampa solo i passaggi della soluzione ottimale
        else:
            print("No solution found.")
            
    except ValueError as e:
        print(e)