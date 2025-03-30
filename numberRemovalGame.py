import tkinter as tk # for GUI
from tkinter import messagebox # messagebox for alerts (popup)
import random, math, time # random for random values(1,2,3), 
# math for calculations, and time for execution time
 
class GameNode: # Game node in tree
    def __init__(self, num_list, human_score, comp_score, parent=None, move_index=None, digit=None):
        self.num_list = num_list.copy() # copy of remaining numbers
        self.human_score = human_score # Human player's score
        self.comp_score = comp_score  # Computer's score
        self.parent = parent # Parent node (ancestors)
        self.children = [] # List of child nodes ( descendents)
        self.move_index = move_index # Index of the move made
        self.digit = digit # The number that was removed
        self.value = None # Value for minimax or alpha beta pruning
        self.is_terminal = not num_list # True if no numbers are left

    def add_child(self, child_node): # Add a child name to the tree
        self.children.append(child_node) 

    def evaluate(self): # Heuristic Evaluation function 
        return self.comp_score - self.human_score


class GameTree: # The main game tree 
    def __init__(self, initial_list, human_score, comp_score, max_depth, first_player="computer"):
        self.root = GameNode(initial_list, human_score, comp_score) # Initialize root node by calling above GameNode
        self.max_depth = max_depth # Depth limit for search algorithms which is 3
        self.nodes_visited = 0   # Count nodes visited 
        self.root_is_max = (first_player == "computer") # Determines if root is maximizing

    # Function to apply game scores
    def apply_move(self, turn, digit, human_score, comp_score):
        if digit == 1: # If number removed is 1 , current player lose his point 
            if turn == "computer":
                comp_score -= 1
            else:
                human_score -= 1
        elif digit == 2:  # If number removed is 2, both players lose 1 point
            comp_score -= 1
            human_score -= 1
        elif digit == 3:  # If number removed is 3 , opponent lose his point
            if turn == "computer":
                human_score -= 1
            else:
                comp_score -= 1
        return human_score, comp_score # Return updated scores for both human and computer

    # The Recursive function to generate the game tree
    def generate_tree(self, node, depth, current_player):
        if depth >= self.max_depth or node.is_terminal:
            return   # Stop recursion if max depth(3) is reached or game is over

        for i, digit in enumerate(node.num_list):
            new_list = node.num_list.copy() # make a copy of num_list and save in new_list
            new_list.pop(i)  # Remove selected number
            new_human, new_comp = self.apply_move(current_player, digit, node.human_score, node.comp_score) #update the score
            child = GameNode(new_list, new_human, new_comp, parent=node, move_index=i, digit=digit) # call gameNode for newly updated
            node.add_child(child)  # Add child node
            next_player = "human" if current_player == "computer" else "computer" # Switch turn 
            self.generate_tree(child, depth + 1, next_player)  # Generate the subtree by calling same function 

    # Minimax algorithm 
    def minimax(self, node, depth, is_maximizing):
        self.nodes_visited += 1  # Track visited nodes by increment + 1
        if depth == 0 or node.is_terminal:
            node.value = node.evaluate() # Assign heuristic value
            return node.value
        if is_maximizing:
            best_value = -math.inf
            for child in node.children:
                best_value = max(best_value, self.minimax(child, depth - 1, False))
            node.value = best_value
            return best_value #find the best value (if comp start)
        else:
            best_value = math.inf
            for child in node.children:
                best_value = min(best_value, self.minimax(child, depth - 1, True))
            node.value = best_value
            return best_value  #find the best value (if human start)

   # Alpha-Beta Pruning algorithm 
    def alpha_beta(self, node, depth, alpha, beta, is_maximizing):
        self.nodes_visited += 1  # Track visited nodes by increment + 1
        if depth == 0 or node.is_terminal:
            node.value = node.evaluate()  # Assign heuristic value
            return node.value
        if is_maximizing:
            best_value = -math.inf # - inifinity
            for child in node.children:
                best_value = max(best_value, self.alpha_beta(child, depth - 1, alpha, beta, False))
                alpha = max(alpha, best_value)
                if beta <= alpha:
                    break  # The Beta cutoff at max
            node.value = best_value
            return best_value # best value if comp start (max level)
        else:
            best_value = math.inf # + inifinity
            for child in node.children:
                best_value = min(best_value, self.alpha_beta(child, depth - 1, alpha, beta, True))
                beta = min(beta, best_value)
                if beta <= alpha:
                    break  # The Alpha cutoff at min
            node.value = best_value 
            return best_value # best value if human start (min level)

    # Get the best move using Minimax or Alpha-Beta pruning
    def get_best_move(self, algorithm="minimax"):
        self.nodes_visited = 0
        start_time = time.time()  # Track execution time (starts)
        first_player = "computer" if self.root_is_max else "human"
        self.generate_tree(self.root, 0, first_player)  # Generate game tree
        if algorithm == "minimax":
            self.minimax(self.root, self.max_depth, self.root_is_max) #call minimax func
        else:
            self.alpha_beta(self.root, self.max_depth, -math.inf, math.inf, self.root_is_max) # else call alpha beta pruning func
        best_child = (max(self.root.children, key=lambda c: c.value)
                      if self.root_is_max else min(self.root.children, key=lambda c: c.value))
        execution_time = time.time() - start_time # Calculate execution time by minising from start_time
        return best_child.move_index if best_child else 0, self.nodes_visited, execution_time  # Return best move with node visited and execution time


# Initialize the game window with setup options
class Game:
    def __init__(self, master):
        self.master = master
        master.title("Number Removal Game")

        # Define colors for UI elements
        self.bg_color, self.button_color, self.text_color = "#f0f0f0", "#3078a9", "#2c3e50"
        master.configure(bg=self.bg_color)

         # Setup frame for initial game options
        self.setup_frame = tk.Frame(master, bg=self.bg_color, padx=10, pady=10)
        self.setup_frame.pack(pady=20)

        # Title label
        tk.Label(self.setup_frame, text="Number Removal Game", font=("Arial", 16, "bold"),
                 bg=self.bg_color, fg=self.text_color).pack(pady=20)
        
        # Input field for string length selection
        tk.Label(self.setup_frame, text="Choose string length (15-25):", bg=self.bg_color).pack()
        self.length_var = tk.IntVar(value=15)
        tk.Entry(self.setup_frame, textvariable=self.length_var, width=3).pack(pady=5)
        
        # Options frame for algorithm and player selection
        options_frame = tk.Frame(self.setup_frame, bg=self.bg_color)
        options_frame.pack(pady=10, fill="x")
        
        # Algorithm selection
        algo_frame = tk.Frame(options_frame, bg=self.bg_color, padx=20)
        algo_frame.pack(side=tk.LEFT, fill="y")
        self.algo_var = tk.StringVar(value="minimax")
        tk.Label(algo_frame, text="Choose search algorithm:", bg=self.bg_color).pack(anchor="w")
        tk.Radiobutton(algo_frame, text="Minimax", variable=self.algo_var, value="minimax", bg=self.bg_color).pack(anchor="w")
        tk.Radiobutton(algo_frame, text="Alpha-Beta", variable=self.algo_var, value="alphabeta", bg=self.bg_color).pack(anchor="w")
        
        # First player selection
        player_frame = tk.Frame(options_frame, bg=self.bg_color, padx=20)
        player_frame.pack(side=tk.LEFT, fill="y")
        self.first_player_var = tk.StringVar(value="human")
        tk.Label(player_frame, text="Who starts the game?", bg=self.bg_color).pack(anchor="w")
        tk.Radiobutton(player_frame, text="Human", variable=self.first_player_var, value="human", bg=self.bg_color).pack(anchor="w")
        tk.Radiobutton(player_frame, text="Computer", variable=self.first_player_var, value="computer", bg=self.bg_color).pack(anchor="w")
        
        # Start game button
        tk.Button(self.setup_frame, text="Start Game", command=self.start_game,
                  bg=self.button_color, fg="white", width=15).pack(pady=10)
        
        self.game_frame = None # Placeholder for game UI
        self.max_depth = 3 # Search depth for algorithms which is 3
        
        # Stats for comparision
        self.stats = {"minimax": {"nodes_visited": [], "execution_times": [], "wins": 0},
                      "alphabeta": {"nodes_visited": [], "execution_times": [], "wins": 0}}

    # Start the game with selected options and initialize the game state.
    def start_game(self):

        # get length from length_var and store in length which is variable
        length = self.length_var.get()
        if not 15 <= length <= 25:
            return messagebox.showerror("Error", "Length must be between 15 and 25.")
       
        # Generate a random sequence of numbers from 1 to 3 (1,2,3)       
        self.num_list = [random.choice([1, 2, 3]) for _ in range(length)]
        
        # Initialize scores for both players 
        self.human_score, self.comp_score = 50, 50

        # set turn for first player using first_player_var
        self.current_turn = self.first_player_var.get()

        # Create the game tree 
        self.game_tree = GameTree(self.num_list, self.human_score, self.comp_score,
                                  self.max_depth, first_player=self.current_turn)
        
        # Adjust window size dynamically based on number sequence length
        window_width = max(600, length * 45)
        self.master.geometry(f"{window_width}x400")
        self.master.minsize(window_width, 400)
        
        # Hide setup frame and create game User interface
        self.setup_frame.pack_forget()
        self.game_frame = tk.Frame(self.master, bg=self.bg_color)
        self.game_frame.pack(pady=20, fill="both", expand=True)
        
        # Add spacing and game status labels
        tk.Frame(self.game_frame, height=30, bg=self.bg_color).pack()
        self.score_label = tk.Label(self.game_frame, text=f"Human: {self.human_score}    Computer: {self.comp_score}",
                                    font=("Arial", 12), bg=self.bg_color)
        self.score_label.pack(pady=10)
        self.turn_label = tk.Label(self.game_frame,
                                   text=f"Current turn: {'Human' if self.current_turn == 'human' else 'Computer'}",
                                   font=("Arial", 12), bg=self.bg_color)
        self.turn_label.pack(pady=5)
        self.algo_info_label = tk.Label(self.game_frame, text=f"Algorithm: {self.algo_var.get().capitalize()}",
                                        font=("Arial", 10), bg=self.bg_color)
        self.algo_info_label.pack(pady=5)
        self.stats_label = tk.Label(self.game_frame, text="Nodes visited: - | Execution time: -",
                                    font=("Arial", 10), bg=self.bg_color)
        self.stats_label.pack(pady=5)
        
        # Create frame for interactive 'Number Buttons'
        self.buttons_frame = tk.Frame(self.game_frame, bg=self.bg_color)
        self.buttons_frame.pack(pady=20)
        self.update_buttons()
        
        # Button for 'New game' 
        tk.Button(self.game_frame, text="New Game", command=self.new_game,
                  bg=self.button_color, fg="white", width=10).pack(pady=10)
       
        # If the computer starts first, trigger its move after a delay 1000 milliseconds which is 1 seecond.
        if self.current_turn == "computer":
            self.master.after(1000, self.computer_move)

    def update_buttons(self):
        # Clear existing buttons from the frame
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()

        # Different colors for each digit value 1 , 2 and 3
        colors = {1: "#fcb101", 2: "#3ae374", 3: "#17c0eb"}

         # Recreate buttons for available numbers in num_list
        for idx, digit in enumerate(self.num_list):
            tk.Button(self.buttons_frame, text=str(digit), font=("Arial", 12),
                      command=lambda idx=idx: self.human_move(idx), width=3,
                      bg=colors[digit], fg="white").pack(side=tk.LEFT, padx=2)

    # Make sure it's the human's turn before proceeding
    def human_move(self, index):
        if self.current_turn != "human":
            return

        # Remove the selected digit from the list and update the score
        digit = self.num_list.pop(index)
        self.human_score, self.comp_score = self.game_tree.apply_move("human", digit, self.human_score, self.comp_score)
        
        # Update the display to show the changes
        self.update_display()

        # Rebuild the game tree with the updated state, switching turns to the computer
        self.game_tree = GameTree(self.num_list, self.human_score, self.comp_score, self.max_depth, first_player="computer")
        
        # Check if the game has ended (no more numbers left to pick)
        if not self.num_list:
            return self.end_game()

        # Switch turn to the computer and shows/Schedule its move
        self.current_turn = "computer"
        self.turn_label.config(text="Current turn: Computer")
        self.master.after(1000, self.computer_move)

    # make sure it's the computer's turn before proceeding
    def computer_move(self):
        if self.current_turn != "computer":
            return
        
        # Get the selected algorithm choice from algo_var
        algo_choice = self.algo_var.get()

        # Compute the 'best move' using the chosen algorithm
        move_index, nodes_visited, execution_time = self.game_tree.get_best_move(algo_choice)
        
        # Track stats for comparative analysis
        self.stats[algo_choice]["nodes_visited"].append(nodes_visited)
        self.stats[algo_choice]["execution_times"].append(execution_time)
        self.stats_label.config(text=f"Nodes visited: {nodes_visited} | Execution time: {execution_time:.4f} sec")
       
        # Make sure the selected move 'index' is within bounds
        move_index = move_index if move_index is not None and move_index < len(self.num_list) else 0
        
        # Remove(pop) the chosen digit from the list and update scores
        digit = self.num_list.pop(move_index)
        self.human_score, self.comp_score = self.game_tree.apply_move("computer", digit, self.human_score, self.comp_score)
        
        # Update display
        self.update_display()
        
        # Rebuild game tree for the next turn, switching back to human (if last move by computer)
        self.game_tree = GameTree(self.num_list, self.human_score, self.comp_score, self.max_depth, first_player="human")
        
        # Check if the game has ended
        if not self.num_list:
            return self.end_game()

        # Switch turn back to human
        self.current_turn = "human"
        self.turn_label.config(text="Current turn: Human")

    # Update the score display
    def update_display(self):
        self.score_label.config(text=f"Human: {self.human_score}    Computer: {self.comp_score}")
        # Refresh the buttons to match the current game state
        self.update_buttons()

    # Retrieve selected algorithm
    def end_game(self):
        algo_choice = self.algo_var.get()
        
        # Find the winner based on scores
        result = "It's a draw!" if self.human_score == self.comp_score else ("Human wins!" if self.human_score > self.comp_score else "Computer wins!")
        
        # Track the number of wins for the computer
        if self.comp_score > self.human_score:
            self.stats[algo_choice]["wins"] += 1
        
        # Compute average stats for nodes visited and execution time
        avg_nodes = sum(self.stats[algo_choice]["nodes_visited"]) / max(1, len(self.stats[algo_choice]["nodes_visited"]))
        avg_time = sum(self.stats[algo_choice]["execution_times"]) / max(1, len(self.stats[algo_choice]["execution_times"]))
        
        # Display and show the game results in a messagebox
        messagebox.showinfo("Game Over", f"Game ended!\n{result}\n\nFinal scores:\nHuman: {self.human_score}\nComputer: {self.comp_score}"
                            f"\n\nAlgorithm: {algo_choice.capitalize()}\nAvg. nodes visited: {avg_nodes:.1f}\nAvg. execution time: {avg_time:.4f} sec")
        
        # Reset the turn to None and indicating the game is over!
        self.current_turn = None

    def new_game(self):
        # Destroy the current game frame and return to setup screen
        self.game_frame.destroy()
        self.setup_frame.pack(pady=20)

#  The Tkinter window initialation
if __name__ == "__main__":
    root = tk.Tk()
    Game(root) # Start the game GUI by calling game class
    root.mainloop()  # For running the Tkinter event loop