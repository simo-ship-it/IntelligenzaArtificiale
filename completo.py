import sys
from queue import PriorityQueue
import cv2
import pytesseract
from aima3.search import Problem
import time
import heapq

# Funzioni per elaborazione delle immagini e acquisizione della griglia
def remove_table_borders(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary_image = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
    remove_horizontal = cv2.morphologyEx(binary_image, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)

    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
    remove_vertical = cv2.morphologyEx(binary_image, cv2.MORPH_OPEN, vertical_kernel, iterations=2)

    borders_removed = binary_image - remove_horizontal - remove_vertical
    borders_removed = cv2.bitwise_not(borders_removed)
    return borders_removed

def extract_and_organize_text(image):
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(image, config=custom_config)
    
    lines = text.splitlines()
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    return cleaned_lines

def process_image_to_grid(image_path):
    image = cv2.imread(image_path)
    processed_image = remove_table_borders(image)
    sorted_rows = extract_and_organize_text(processed_image)
    result_array = [row.replace(" ", "") for row in sorted_rows]
    return result_array

# Classe del problema di Uniform Coloring
class UniformColoring(Problem):
    def __init__(self, initial, goal_color, start_position, color_costs):
        super().__init__(initial)
        self.goal_color = goal_color
        self.start_position = start_position
        self.color_costs = color_costs

    def actions(self, state):
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
        grid, (x, y) = state
        new_grid = [list(row) for row in grid]
        
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
        grid, _ = state
        for x, row in enumerate(grid):
            for y, cell in enumerate(row):
                if (x, y) != self.start_position and cell != self.goal_color:
                    return False
        return True

    def path_cost(self, c, state1, action, state2):
        if action in ['Up', 'Down', 'Left', 'Right']:
            return c + 1
        elif action == 'Paint':
            return c + self.color_costs[self.goal_color]
        else:
            return c

# Funzioni ausiliarie per UCS/A*
def find_starting_position(grid):
    positions = [(x, y) for x, row in enumerate(grid) for y, cell in enumerate(row) if cell == 'T']
    
    if len(positions) == 0:
        raise ValueError("Errore: 'T' non trovato nella griglia.")
    elif len(positions) > 1:
        raise ValueError("Errore: Più di una testina ('T') trovata nella griglia.")
    
    return positions[0]

def print_grid(grid):
    for row in grid:
        print(" ".join(row))
    print()

def calculate_total_cost(grid, color, start_position, color_costs):
    rows, cols = len(grid), len(grid[0])
    visited = set()
    total_cost = 0
    frontier = PriorityQueue()
    frontier.put((0, start_position))

    while not frontier.empty():
        cost, (x, y) = frontier.get()

        if (x, y) in visited:
            continue

        visited.add((x, y))

        current_color = grid[x][y]
        if current_color != color:
            step_cost = color_costs[color]
            total_cost += step_cost

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and (nx, ny) not in visited:
                frontier.put((cost + 1, (nx, ny)))
    return total_cost

def find_optimal_goal_color(grid, start_position, color_costs):
    colors = color_costs.keys()
    costs = {color: calculate_total_cost(grid, color, start_position, color_costs) for color in colors}
    optimal_color = min(costs, key=costs.get)
    print(f"Costi per ogni colore: {costs}")
    print(f"Colore obiettivo ottimale: {optimal_color}")
    return optimal_color

# Funzione UCS ottimizzata con gestione migliorata della frontiera
def uniform_cost_search_optimized(problem, debug=False):
    # Inizializza la frontiera come una coda con priorità (heap)
    frontier = []
    heapq.heappush(frontier, (0, problem.initial, []))  # (costo, stato, percorso delle azioni)
    
    # Utilizziamo un dizionario per memorizzare il costo minimo con cui uno stato è stato esplorato
    explored = {}
    
    while frontier:
        cost, state, path = heapq.heappop(frontier)
        
        # Se lo stato è l'obiettivo, restituiamo il percorso
        if problem.goal_test(state):
            return path, cost, [(state, cost, path)]
        
        grid, _ = state
        
        # Controlla se lo stato è già stato esplorato con un costo inferiore
        if state in explored and explored[state] <= cost:
            continue
        
        # Memorizziamo il costo minimo con cui abbiamo esplorato lo stato
        explored[state] = cost
        
        for action in problem.actions(state):
            child = problem.result(state, action)
            new_cost = problem.path_cost(cost, state, action, child)
            new_path = path + [action]
            
            # Se non abbiamo esplorato questo stato con un costo inferiore, aggiungiamo alla frontiera
            if child not in explored or explored[child] > new_cost:
                heapq.heappush(frontier, (new_cost, child, new_path))
            
            if debug:
                print(f"Action: {action}, Cost: {new_cost}")
                print_grid(child[0])  # Stampa la griglia dopo ogni mossa
                # time.sleep(0.1)  # Aggiunge un ritardo per simulare il movimento

    return None

# Funzione A* ottimizzata con gestione migliorata della frontiera
def a_star_search_optimized(problem, heuristic, debug=False):
    # Inizializza la frontiera come una coda con priorità (heap)
    frontier = []
    heapq.heappush(frontier, (0 + heuristic(problem.initial), 0, problem.initial, []))  # (f(n), g(n), stato, percorso delle azioni)
    
    # Utilizziamo un dizionario per memorizzare il costo minimo con cui uno stato è stato esplorato
    explored = {}
    
    while frontier:
        f, g, state, path = heapq.heappop(frontier)
        
        # Se lo stato è l'obiettivo, restituiamo il percorso
        if problem.goal_test(state):
            return path, g, [(state, g, path)]
        
        grid, _ = state
        
        # Controlla se lo stato è già stato esplorato con un costo inferiore
        if state in explored and explored[state] <= g:
            continue
        
        # Memorizziamo il costo minimo con cui abbiamo esplorato lo stato
        explored[state] = g
        
        for action in problem.actions(state):
            child = problem.result(state, action)
            new_g = problem.path_cost(g, state, action, child)
            new_f = new_g + heuristic(child)
            new_path = path + [action]
            
            # Se non abbiamo esplorato questo stato con un costo inferiore, aggiungiamo alla frontiera
            if child not in explored or explored[child] > new_g:
                heapq.heappush(frontier, (new_f, new_g, child, new_path))
            
            if debug:
                print(f"Action: {action}, Cost: {new_g}")
                print_grid(child[0])  # Stampa la griglia dopo ogni mossa
                # time.sleep(0.01)  # Aggiunge un ritardo per simulare il movimento

    return None

def print_optimal_solution_steps(optimal_solution_steps):
    for i, (state, cost, path) in enumerate(optimal_solution_steps):
        grid, _ = state
        print(f"Passaggio {i + 1}, Costo: {cost}, Azioni: {' -> '.join(path)}")
        print_grid(grid)

def heuristic_manhattan_distance(state):
    grid, (tx, ty) = state
    total_distance = 0
    for x, row in enumerate(grid):
        for y, cell in enumerate(row):
            if cell != problem.goal_color:
                total_distance += abs(tx - x) + abs(ty - y)
    return total_distance

# Main per eseguire l'intero processo utilizzando un'immagine come input per la griglia e la modalità debug
if __name__ == '__main__':
    image_path = 'PROVA.png'  # Inserisci il percorso dell'immagine
    try:
        # Chiedi se attivare la modalità debug
        debug_choice = input("Vuoi attivare la modalità debug? (s/n): ").strip().lower()
        debug = debug_choice == 's'
        
        # Acquisizione della griglia dall'immagine
        grid = process_image_to_grid(image_path)  
        
        # Trova la posizione iniziale della testina 'T'
        start_position = find_starting_position(grid)
        
        # Definizione dei costi di colorazione per ogni colore
        color_costs = {'B': 1, 'Y': 2, 'G': 3}
        
        # Calcolo del colore obiettivo ottimale
        optimal_goal_color = find_optimal_goal_color(grid, start_position, color_costs)

        # Stampa della griglia letta dall'immagine
        print("Griglia letta dall'immagine:")
        print_grid(grid)

        # Impostazione dello stato iniziale
        initial_state = (tuple(grid), start_position)
        problem = UniformColoring(initial=initial_state, goal_color=optimal_goal_color, start_position=start_position, color_costs=color_costs)

        # Chiedi quale algoritmo utilizzare
        algorithm_choice = input("Scegli l'algoritmo da utilizzare (UCS o A*): ").strip().lower()
        
        if algorithm_choice == 'ucs':
            path, total_cost, optimal_solution_steps = uniform_cost_search_optimized(problem, debug)
        elif algorithm_choice == 'a*':
            path, total_cost, optimal_solution_steps = a_star_search_optimized(problem, heuristic_manhattan_distance, debug)
        else:
            raise ValueError("Algoritmo non riconosciuto. Scegli 'UCS' o 'A*'.")

        # Se viene trovata una soluzione, stampa i risultati finali
        if path and not debug:
            print(f"Soluzione trovata con costo: {total_cost}")
            print_optimal_solution_steps(optimal_solution_steps)  # Stampa solo i passaggi della soluzione ottimale
        elif path and debug:
            print(f"Modalità debug completata, soluzione trovata con costo: {total_cost}")
        else:
            print("Nessuna soluzione trovata.")
            
    except ValueError as e:
        print(e)