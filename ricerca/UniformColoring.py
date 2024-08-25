import sys
sys.path.append('/Users/simonebilleri/.python-lib/aima-python')

from aima3.search import Problem, astar_search

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
        Le azioni includono il movimento della testina e la colorazione della cella corrente,
        eccetto la cella iniziale con 'T'.

        :param state: Lo stato attuale rappresentato come (griglia, posizione_testina).
        :return: Lista di azioni possibili. 
                 Ogni azione potrebbe essere 'Up', 'Down', 'Left', 'Right', o 'Paint'.
        """
        actions = []
        grid, (x, y) = state
        rows, cols = len(grid), len(grid[0])

        # Aggiungi azioni di movimento se sono all'interno dei limiti della griglia
        if x > 0: actions.append('Up')
        if x < rows - 1: actions.append('Down')
        if y > 0: actions.append('Left')
        if y < cols - 1: actions.append('Right')

        # Aggiungi azione di colorazione solo se la cella corrente non è già del colore desiderato
        # e non è la posizione di partenza 'T'
        if grid[x][y] != self.goal_color and (x, y) != self.start_position:
            actions.append('Paint')

        return actions

    def result(self, state, action):
        """
        Applica un'azione a uno stato e restituisce il nuovo stato risultante.

        :param state: Lo stato corrente rappresentato come (griglia, posizione_testina).
        :param action: L'azione da eseguire ('Up', 'Down', 'Left', 'Right', 'Paint').
        :return: Nuovo stato risultante dopo l'applicazione dell'azione.
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

        # Mantieni la casella iniziale con 'T' invariata
        new_grid[self.start_position[0]][self.start_position[1]] = 'T'

        return (tuple("".join(row) for row in new_grid), new_position)

    def goal_test(self, state):
        """
        Verifica se lo stato corrente corrisponde allo stato obiettivo.

        :param state: Lo stato corrente rappresentato come (griglia, posizione_testina).
        :return: True se tutte le celle della griglia sono dello stesso colore goal, 
                 eccetto la cella con 'T', False altrimenti.
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
        Ogni mossa o azione di colorazione ha un costo specifico.

        :param c: Il costo accumulato fino a state1.
        :param state1: Lo stato corrente.
        :param action: L'azione eseguita per passare da state1 a state2.
        :param state2: Il nuovo stato risultante dall'azione.
        :return: Il costo aggiornato del percorso.
        """
        if action in ['Up', 'Down', 'Left', 'Right']:
            return c + 1  # Ogni movimento costa 1
        elif action == 'Paint':
            _, (x, y) = state2
            # Costo della colorazione basato sul colore di destinazione
            return c + self.color_costs[self.goal_color]
        else:
            return c

    def h(self, node):
        """
        Funzione euristica per A* o altre ricerche informate.
        Potrebbe calcolare, per esempio, il numero di celle non colorate correttamente,
        eccetto la cella con 'T'.

        :param node: Il nodo corrente nello spazio di ricerca.
        :return: Un valore euristico che stima il costo dal nodo corrente al goal.
        """
        state, _ = node.state
        return sum(
            self.color_costs[cell]
            for x, row in enumerate(state)
            for y, cell in enumerate(row)
            if (x, y) != self.start_position and cell != self.goal_color
        )

def find_starting_position(grid):
    """
    Trova la posizione iniziale della testina cercando la lettera 'T' nella griglia.

    :param grid: La griglia rappresentata come una tupla di stringhe.
    :return: Una tupla (x, y) che rappresenta la posizione della testina.
    """
    for x, row in enumerate(grid):
        for y, cell in enumerate(row):
            if cell == 'T':
                return (x, y)
    return None  # Ritorna None se 'T' non è trovato

def print_grid(grid):
    """
    Stampa la griglia in modo leggibile.
    
    :param grid: La griglia rappresentata come una tupla di stringhe.
    """
    print("Griglia attuale:")
    for row in grid:
        print(" ".join(row))
    print()

def calculate_total_cost(grid, color, start_position, color_costs):
    """
    Calcola il costo totale per uniformare tutte le celle della griglia a un colore specifico,
    inclusi i costi di spostamento e di colorazione.

    :param grid: La griglia rappresentata come una tupla di stringhe.
    :param color: Il colore obiettivo da valutare.
    :param start_position: La posizione iniziale della testina (dove si trova 'T').
    :param color_costs: Dizionario dei costi di colorazione per ogni colore.
    :return: Il costo totale stimato per uniformare la griglia al colore specificato.
    """
    total_cost = 0
    rows, cols = len(grid), len(grid[0])

    for x in range(rows):
        for y in range(cols):
            if (x, y) != start_position:
                current_color = grid[x][y]
                if current_color != color:
                    # Aggiungi il costo per cambiare il colore
                    total_cost += color_costs[color]

    return total_cost

def find_optimal_goal_color(grid, start_position, color_costs):
    """
    Trova il colore obiettivo più conveniente per uniformare la griglia.

    :param grid: La griglia rappresentata come una tupla di stringhe.
    :param start_position: La posizione iniziale della testina (dove si trova 'T').
    :param color_costs: Dizionario dei costi di colorazione per ogni colore.
    :return: Il colore obiettivo più conveniente.
    """
    colors = color_costs.keys()
    costs = {color: calculate_total_cost(grid, color, start_position, color_costs) for color in colors}
    optimal_color = min(costs, key=costs.get)
    print("Costi per ogni colore:", costs)
    print("Colore obiettivo ottimale:", optimal_color)
    return optimal_color

# Esempio di utilizzo
if __name__ == '__main__':
    initial_grid = ['GTG', 'GGG', 'GGG', 'YYB']
    start_position = find_starting_position(initial_grid)  # Trova la posizione di 'T'
    
    if start_position is None:
        print("Errore: 'T' non trovato nella griglia.")
    else:
        color_costs = {'B': 1, 'Y': 2, 'G': 3}  # Costi di colorazione per ciascun colore
        optimal_goal_color = find_optimal_goal_color(initial_grid, start_position, color_costs)
        
        initial_state = (tuple(initial_grid), start_position)
        problem = UniformColoring(initial=initial_state, goal_color=optimal_goal_color, start_position=start_position, color_costs=color_costs)
        
        solution_astar = astar_search(problem)

        # Stampa la soluzione
        print("A* Solution (sequence of actions):", solution_astar.solution())
        
        # Ricrea la griglia finale applicando la soluzione trovata
        final_state = initial_state
        for action in solution_astar.solution():
            final_state = problem.result(final_state, action)

        # Stampa la griglia finale
        final_grid, _ = final_state
        print_grid(final_grid)
