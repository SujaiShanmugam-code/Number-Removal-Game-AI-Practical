import tkinter as tk
from tkinter import messagebox
import random, math, time

class GameNode:
    def __init__(self, num_list, human_score, comp_score, parent=None, move_index=None, digit=None):
        self.num_list = num_list.copy()
        self.human_score = human_score
        self.comp_score = comp_score
        self.parent = parent
        self.children = []
        self.move_index = move_index
        self.digit = digit
        self.value = None
        self.is_terminal = not num_list

    def add_child(self, child_node):
        self.children.append(child_node)

    def evaluate(self):
        return self.comp_score - self.human_score


class GameTree:
    def __init__(self, initial_list, human_score, comp_score, max_depth, first_player="computer"):
        self.root = GameNode(initial_list, human_score, comp_score)
        self.max_depth = max_depth
        self.nodes_visited = 0
        self.root_is_max = (first_player == "computer")

    def apply_move(self, turn, digit, human_score, comp_score):
        if digit == 1:
            if turn == "computer":
                comp_score -= 1
            else:
                human_score -= 1
        elif digit == 2:
            comp_score -= 1
            human_score -= 1
        elif digit == 3:
            if turn == "computer":
                human_score -= 1
            else:
                comp_score -= 1
        return human_score, comp_score

    def generate_tree(self, node, depth, current_player):
        if depth >= self.max_depth or node.is_terminal:
            return
        for i, digit in enumerate(node.num_list):
            new_list = node.num_list.copy()
            new_list.pop(i)
            new_human, new_comp = self.apply_move(current_player, digit, node.human_score, node.comp_score)
            child = GameNode(new_list, new_human, new_comp, parent=node, move_index=i, digit=digit)
            node.add_child(child)
            next_player = "human" if current_player == "computer" else "computer"
            self.generate_tree(child, depth + 1, next_player)

    def minimax(self, node, depth, is_maximizing):
        self.nodes_visited += 1
        if depth == 0 or node.is_terminal:
            node.value = node.evaluate()
            return node.value
        if is_maximizing:
            best_value = -math.inf
            for child in node.children:
                best_value = max(best_value, self.minimax(child, depth - 1, False))
            node.value = best_value
            return best_value
        else:
            best_value = math.inf
            for child in node.children:
                best_value = min(best_value, self.minimax(child, depth - 1, True))
            node.value = best_value
            return best_value

    def alpha_beta(self, node, depth, alpha, beta, is_maximizing):
        self.nodes_visited += 1
        if depth == 0 or node.is_terminal:
            node.value = node.evaluate()
            return node.value
        if is_maximizing:
            best_value = -math.inf
            for child in node.children:
                best_value = max(best_value, self.alpha_beta(child, depth - 1, alpha, beta, False))
                alpha = max(alpha, best_value)
                if beta <= alpha:
                    break
            node.value = best_value
            return best_value
        else:
            best_value = math.inf
            for child in node.children:
                best_value = min(best_value, self.alpha_beta(child, depth - 1, alpha, beta, True))
                beta = min(beta, best_value)
                if beta <= alpha:
                    break
            node.value = best_value
            return best_value

    def get_best_move(self, algorithm="minimax"):
        self.nodes_visited = 0
        start_time = time.time()
        first_player = "computer" if self.root_is_max else "human"
        self.generate_tree(self.root, 0, first_player)
        if algorithm == "minimax":
            self.minimax(self.root, self.max_depth, self.root_is_max)
        else:
            self.alpha_beta(self.root, self.max_depth, -math.inf, math.inf, self.root_is_max)
        best_child = (max(self.root.children, key=lambda c: c.value)
                      if self.root_is_max else min(self.root.children, key=lambda c: c.value))
        execution_time = time.time() - start_time
        return best_child.move_index if best_child else 0, self.nodes_visited, execution_time


class Game:
    def __init__(self, master):
        self.master = master
        master.title("Number Removal Game")
        self.bg_color, self.button_color, self.text_color = "#f0f0f0", "#3078a9", "#2c3e50"
        master.configure(bg=self.bg_color)
        self.setup_frame = tk.Frame(master, bg=self.bg_color, padx=10, pady=10)
        self.setup_frame.pack(pady=20)
        tk.Label(self.setup_frame, text="Number Removal Game", font=("Arial", 16, "bold"),
                 bg=self.bg_color, fg=self.text_color).pack(pady=20)
        tk.Label(self.setup_frame, text="Choose string length (15-25):", bg=self.bg_color).pack()
        self.length_var = tk.IntVar(value=15)
        tk.Entry(self.setup_frame, textvariable=self.length_var, width=3).pack(pady=5)
        options_frame = tk.Frame(self.setup_frame, bg=self.bg_color)
        options_frame.pack(pady=10, fill="x")
        algo_frame = tk.Frame(options_frame, bg=self.bg_color, padx=20)
        algo_frame.pack(side=tk.LEFT, fill="y")
        self.algo_var = tk.StringVar(value="minimax")
        tk.Label(algo_frame, text="Choose search algorithm:", bg=self.bg_color).pack(anchor="w")
        tk.Radiobutton(algo_frame, text="Minimax", variable=self.algo_var, value="minimax", bg=self.bg_color).pack(anchor="w")
        tk.Radiobutton(algo_frame, text="Alpha-Beta", variable=self.algo_var, value="alphabeta", bg=self.bg_color).pack(anchor="w")
        player_frame = tk.Frame(options_frame, bg=self.bg_color, padx=20)
        player_frame.pack(side=tk.LEFT, fill="y")
        self.first_player_var = tk.StringVar(value="human")
        tk.Label(player_frame, text="Who starts the game?", bg=self.bg_color).pack(anchor="w")
        tk.Radiobutton(player_frame, text="Human", variable=self.first_player_var, value="human", bg=self.bg_color).pack(anchor="w")
        tk.Radiobutton(player_frame, text="Computer", variable=self.first_player_var, value="computer", bg=self.bg_color).pack(anchor="w")
        tk.Button(self.setup_frame, text="Start Game", command=self.start_game,
                  bg=self.button_color, fg="white", width=15).pack(pady=10)
        self.game_frame = None
        self.max_depth = 3
        self.stats = {"minimax": {"nodes_visited": [], "execution_times": [], "wins": 0},
                      "alphabeta": {"nodes_visited": [], "execution_times": [], "wins": 0}}

    def start_game(self):
        length = self.length_var.get()
        if not 15 <= length <= 25:
            return messagebox.showerror("Error", "Length must be between 15 and 25.")
        self.num_list = [random.choice([1, 2, 3]) for _ in range(length)]
        self.human_score, self.comp_score = 50, 50
        self.current_turn = self.first_player_var.get()
        self.game_tree = GameTree(self.num_list, self.human_score, self.comp_score,
                                  self.max_depth, first_player=self.current_turn)
        window_width = max(600, length * 45)
        self.master.geometry(f"{window_width}x400")
        self.master.minsize(window_width, 400)
        self.setup_frame.pack_forget()
        self.game_frame = tk.Frame(self.master, bg=self.bg_color)
        self.game_frame.pack(pady=20, fill="both", expand=True)
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
        self.buttons_frame = tk.Frame(self.game_frame, bg=self.bg_color)
        self.buttons_frame.pack(pady=20)
        self.update_buttons()
        tk.Button(self.game_frame, text="New Game", command=self.new_game,
                  bg=self.button_color, fg="white", width=10).pack(pady=10)
        if self.current_turn == "computer":
            self.master.after(1000, self.computer_move)

    def update_buttons(self):
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()
        colors = {1: "#fcb101", 2: "#3ae374", 3: "#17c0eb"}
        for idx, digit in enumerate(self.num_list):
            tk.Button(self.buttons_frame, text=str(digit), font=("Arial", 12),
                      command=lambda idx=idx: self.human_move(idx), width=3,
                      bg=colors[digit], fg="white").pack(side=tk.LEFT, padx=2)

    def human_move(self, index):
        if self.current_turn != "human":
            return
        digit = self.num_list.pop(index)
        self.human_score, self.comp_score = self.game_tree.apply_move("human", digit, self.human_score, self.comp_score)
        self.update_display()
        self.game_tree = GameTree(self.num_list, self.human_score, self.comp_score, self.max_depth, first_player="computer")
        if not self.num_list:
            return self.end_game()
        self.current_turn = "computer"
        self.turn_label.config(text="Current turn: Computer")
        self.master.after(1000, self.computer_move)

    def computer_move(self):
        if self.current_turn != "computer":
            return
        algo_choice = self.algo_var.get()
        move_index, nodes_visited, execution_time = self.game_tree.get_best_move(algo_choice)
        self.stats[algo_choice]["nodes_visited"].append(nodes_visited)
        self.stats[algo_choice]["execution_times"].append(execution_time)
        self.stats_label.config(text=f"Nodes visited: {nodes_visited} | Execution time: {execution_time:.4f} sec")
        move_index = move_index if move_index is not None and move_index < len(self.num_list) else 0
        digit = self.num_list.pop(move_index)
        self.human_score, self.comp_score = self.game_tree.apply_move("computer", digit, self.human_score, self.comp_score)
        self.update_display()
        self.game_tree = GameTree(self.num_list, self.human_score, self.comp_score, self.max_depth, first_player="human")
        if not self.num_list:
            return self.end_game()
        self.current_turn = "human"
        self.turn_label.config(text="Current turn: Human")

    def update_display(self):
        self.score_label.config(text=f"Human: {self.human_score}    Computer: {self.comp_score}")
        self.update_buttons()

    def end_game(self):
        algo_choice = self.algo_var.get()
        result = "It's a draw!" if self.human_score == self.comp_score else ("Human wins!" if self.human_score > self.comp_score else "Computer wins!")
        if self.comp_score > self.human_score:
            self.stats[algo_choice]["wins"] += 1
        avg_nodes = sum(self.stats[algo_choice]["nodes_visited"]) / max(1, len(self.stats[algo_choice]["nodes_visited"]))
        avg_time = sum(self.stats[algo_choice]["execution_times"]) / max(1, len(self.stats[algo_choice]["execution_times"]))
        messagebox.showinfo("Game Over", f"Game ended!\n{result}\n\nFinal scores:\nHuman: {self.human_score}\nComputer: {self.comp_score}"
                            f"\n\nAlgorithm: {algo_choice.capitalize()}\nAvg. nodes visited: {avg_nodes:.1f}\nAvg. execution time: {avg_time:.4f} sec")
        self.current_turn = None

    def new_game(self):
        self.game_frame.destroy()
        self.setup_frame.pack(pady=20)


if __name__ == "__main__":
    root = tk.Tk()
    Game(root)
    root.mainloop()