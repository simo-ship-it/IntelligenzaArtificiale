import sys
from queue import PriorityQueue
import cv2
import pytesseract
from aima3.search import Problem
import time
import heapq
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

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

        # Movimenti nella griglia
        if x > 0: actions.append('Up')
        if x < rows - 1: actions.append('Down')
        if y > 0: actions.append('Left')
        if y < cols - 1: actions.append('Right')

        # Azione di colorazione solo se la cella non è colorata e non è la posizione iniziale
        if grid[x][y] != self.goal_color and (x, y) != self.start_position:
            actions.append('Paint')

        return actions

    def result(self, state, action):
        grid, (x, y) = state
        new_grid = [list(row) for row in grid]  # Copia della griglia

        # Movimenti
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

        # Mantiene la posizione iniziale con 'T'
        new_grid[self.start_position[0]][self.start_position[1]] = 'T'
        return (tuple("".join(row) for row in new_grid), new_position)

    def goal_test(self, state):
        grid, position = state
        # Verifica che tutte le celle siano colorate e che la testina sia nella posizione iniziale
        all_colored = all(cell == self.goal_color for row in grid for cell in row if cell != 'T')
        is_at_start = position == self.start_position
        return all_colored and is_at_start

    def path_cost(self, c, state1, action, state2):
        # Ogni movimento e ogni pittura hanno un costo
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

        # Calcola il costo solo se la cella corrente non è la testina
        if (x, y) != start_position:
            current_color = grid[x][y]
            if current_color != color:
                step_cost = color_costs[color]
                total_cost += step_cost

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Movimenti possibili: su, giù, sinistra, destra
            nx, ny = x + dx, y + dy  # Nuove coordinate
            if 0 <= nx < rows and 0 <= ny < cols and (nx, ny) not in visited:  # Controlla i limiti della griglia
                frontier.put((cost + 1, (nx, ny)))  # Aggiungi il costo per il movimento

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
    # Coda prioritaria (heap) che tiene traccia degli stati
    frontier = []
    # Aggiungiamo lo stato iniziale nella frontiera con un costo pari a 0
    heapq.heappush(frontier, (0, problem.initial, []))  # (costo, stato, percorso delle azioni)
    
    # Dizionario che memorizza il costo minimo con cui uno stato è stato esplorato
    explored = {}
    
    # Set per memorizzare stati esplorati per evitare duplicati (usiamo hashing per velocità)
    visited = set()
    
    while frontier:
        cost, state, path = heapq.heappop(frontier)  # Estrarre lo stato con il costo più basso
        
        # Early goal detection: se abbiamo raggiunto lo stato obiettivo, terminiamo
        if problem.goal_test(state):
            return path, cost, [(state, cost, path)]
        
        grid, current_position = state  # Estrarre la griglia e la posizione corrente
        
        # Genera un hash dello stato corrente per velocizzare il confronto
        state_hash = hash(state)
        if state_hash in visited:
            continue
        
        # Aggiungi lo stato corrente alla lista degli esplorati
        visited.add(state_hash)
        
        # Memorizziamo il miglior costo esplorato per lo stato
        explored[state] = cost
        
        # Pre-filtraggio delle azioni: evitiamo mosse che portano indietro o sono ridondanti
        for action in problem.actions(state):
            child = problem.result(state, action)
            new_cost = problem.path_cost(cost, state, action, child)

            # Early goal detection: controllo immediato se il figlio è la soluzione
            if problem.goal_test(child):
                return path + [action], new_cost, [(child, new_cost, path + [action])]

            # Ottimizzazione: esploriamo solo nuovi stati o stati con costi migliori
            child_hash = hash(child)
            if child_hash not in visited or explored.get(child, float('inf')) > new_cost:
                heapq.heappush(frontier, (new_cost, child, path + [action]))
            
            # Se la modalità debug è attiva, stampa le informazioni di debug
            if debug:
                print(f"Action: {action}, Cost: {new_cost}")
                print_grid(child[0])  # Stampa la griglia dopo ogni mossa

    return None

# Funzione A* ottimizzata con gestione migliorata della frontiera
def a_star_search_optimized(problem, heuristic, debug=False):
    frontier = []
    heapq.heappush(frontier, (0 + heuristic(problem.initial, problem.goal_color, problem.color_costs), 0, problem.initial, []))  # (f(n), g(n), stato, percorso delle azioni)
    
    explored = {}
    
    while frontier:
        f, g, state, path = heapq.heappop(frontier)
        
        if problem.goal_test(state):
            return path, g, [(state, g, path)]
        
        grid, _ = state
        
        if state in explored and explored[state] <= g:
            continue
        
        explored[state] = g
        
        for action in problem.actions(state):
            child = problem.result(state, action)
            new_g = problem.path_cost(g, state, action, child)
            new_f = new_g + heuristic(child, problem.goal_color, problem.color_costs)
            new_path = path + [action]
            
            if child not in explored or explored[child] > new_g:
                heapq.heappush(frontier, (new_f, new_g, child, new_path))
            
            if debug:
                print(f"Action: {action}, Cost: {new_g}")
                print_grid(child[0])

    return None

def print_optimal_solution_steps(optimal_solution_steps):
    for i, (state, cost, path) in enumerate(optimal_solution_steps):
        grid, _ = state
        print(f"Passaggio {i + 1}, Costo: {cost}, Azioni: {' -> '.join(path)}")
        print_grid(grid)

# Euristica migliorata per A* che considera i costi di pittura e la distanza massima
def improved_heuristic(state, goal_color, color_costs):
    grid, (tx, ty) = state
    total_paint_cost = 0
    max_distance = 0
    
    for x, row in enumerate(grid):
        for y, cell in enumerate(row):
            if cell != goal_color:
                # Aggiungi il costo di pittura per ogni cella che non è colorata correttamente
                total_paint_cost += color_costs[goal_color]
                
                # Calcola la distanza di Manhattan dalla testina alla cella corrente
                distance = abs(tx - x) + abs(ty - y)
                
                # Tieni traccia della distanza massima per considerare la cella più lontana
                if distance > max_distance:
                    max_distance = distance

    # L'euristica è la somma del costo di pittura più la distanza massima per raggiungere la cella più lontana
    return total_paint_cost + max_distance

# GUI per l'applicazione
class UniformColoringGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Uniform Coloring Search")
        self.root.geometry("1000x1000")

        self.image_label = tk.Label(self.root, text="Nessuna immagine caricata")
        self.image_label.pack(pady=10)

        self.canvas = tk.Canvas(self.root, width=500, height=500)
        self.canvas.pack()

        self.upload_button = tk.Button(self.root, text="Carica Immagine", command=self.upload_image)
        self.upload_button.pack(pady=10)

        self.color_costs_label = tk.Label(self.root, text="Costi dei colori: Non calcolati")
        self.color_costs_label.pack()

        self.color_choice_var = tk.StringVar()
        self.color_choice_menu = tk.OptionMenu(self.root, self.color_choice_var, "")
        self.color_choice_menu.pack()

        self.algorithm_label = tk.Label(self.root, text="Scegli l'algoritmo:")
        self.algorithm_label.pack()

        self.algorithm_var = tk.StringVar(value="ucs")
        self.ucs_radio = tk.Radiobutton(self.root, text="UCS", variable=self.algorithm_var, value="ucs")
        self.ucs_radio.pack()
        self.a_star_radio = tk.Radiobutton(self.root, text="A*", variable=self.algorithm_var, value="a*")
        self.a_star_radio.pack()

        self.debug_var = tk.BooleanVar(value=False)
        self.debug_check = tk.Checkbutton(self.root, text="Attiva modalità Debug", variable=self.debug_var)
        self.debug_check.pack()

        self.run_button = tk.Button(self.root, text="Esegui", command=self.run_algorithm)
        self.run_button.pack(pady=10)

        self.exit_button = tk.Button(self.root, text="Exit", command=self.exit_program)
        self.exit_button.pack(pady=10)

        self.grid_image = None
        self.grid = None

    def upload_image(self):
        file_path = filedialog.askopenfilename()
        if not file_path:
            return

        self.grid_image = cv2.imread(file_path)
        image = cv2.cvtColor(self.grid_image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image.thumbnail((500, 500))
        self.tk_image = ImageTk.PhotoImage(image)
        self.canvas.create_image(250, 250, image=self.tk_image)

        try:
            self.grid = process_image_to_grid(file_path)
            self.image_label.config(text="Immagine caricata correttamente")
            self.calculate_and_display_color_costs()  # Calcola e visualizza i costi dei colori
        except ValueError as e:
            messagebox.showerror("Errore", str(e))

    def calculate_and_display_color_costs(self):
        start_position = find_starting_position(self.grid)
        color_costs = {'B': 1, 'Y': 2, 'G': 3}  # Definisci i costi dei colori
        costs = {color: calculate_total_cost(self.grid, color, start_position, color_costs) for color in color_costs}
        
        # Mostra i costi nella GUI
        self.color_costs_label.config(text=f"Costi dei colori: {costs}")
        
        # Aggiorna il menu di scelta del colore obiettivo
        menu = self.color_choice_menu["menu"]
        menu.delete(0, "end")  # Rimuovi eventuali opzioni precedenti
        for color in costs.keys():
            menu.add_command(label=color, command=lambda c=color: self.color_choice_var.set(c))

    def run_algorithm(self):
        if not self.grid:
            messagebox.showwarning("Attenzione", "Devi caricare un'immagine prima di eseguire l'algoritmo!")
            return

        try:
            start_position = find_starting_position(self.grid)
            color_costs = {'B': 1, 'Y': 2, 'G': 3}
            
            # Usa il colore scelto dall'utente
            chosen_goal_color = self.color_choice_var.get()
            if not chosen_goal_color:
                messagebox.showwarning("Attenzione", "Devi scegliere un colore obiettivo prima di eseguire l'algoritmo!")
                return
            
            initial_state = (tuple(self.grid), start_position)
            problem = UniformColoring(initial=initial_state, goal_color=chosen_goal_color, start_position=start_position, color_costs=color_costs)

            if self.algorithm_var.get() == "ucs":
                path, total_cost, optimal_solution_steps = uniform_cost_search_optimized(problem, self.debug_var.get())
                algo_name = "UCS"
            else:
                path, total_cost, optimal_solution_steps = a_star_search_optimized(problem, improved_heuristic, self.debug_var.get())
                algo_name = "A*"

            if path:
                if not self.debug_var.get():
                    messagebox.showinfo("Soluzione trovata", f"{algo_name} trovato soluzione con costo: {total_cost}")
                    self.show_solution_steps(optimal_solution_steps)
                else:
                    num_moves = len(path)
                    messagebox.showinfo("Soluzione trovata", f"{algo_name} trovato soluzione con costo: {total_cost} e {num_moves} mosse")
                    self.show_solution_steps(optimal_solution_steps)
            else:
                messagebox.showwarning("Nessuna soluzione", "Nessuna soluzione trovata.")

        except ValueError as e:
            messagebox.showerror("Errore", str(e))


    def show_solution_steps(self, optimal_solution_steps):
        result_window = tk.Toplevel(self.root)
        result_window.title("Passaggi della Soluzione")

        text_area = tk.Text(result_window, wrap="word", height=30, width=80)
        text_area.pack(pady=10)

        for i, (state, cost, path) in enumerate(optimal_solution_steps):
            grid, _ = state
            text_area.insert(tk.END, f"Passaggio {i + 1}, Costo: {cost}, Azioni: {' -> '.join(path)}\n")
            text_area.insert(tk.END, "\n".join(" ".join(row) for row in grid))
            text_area.insert(tk.END, "\n\n")

        text_area.config(state="disabled")

    # Funzione per chiudere l'applicazione
    def exit_program(self):
        self.root.quit()  # Oppure puoi usare self.root.destroy() per chiudere completamente l'applicazione


# Funzione principale
if __name__ == "__main__":
    root = tk.Tk()
    app = UniformColoringGUI(root)
    root.mainloop()