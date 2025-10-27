#!/usr/bin/env python
# coding: utf-8

# In[2]:


import tkinter as tk
from tkinter import messagebox
import random
import math
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class GraphApp:
    def __init__(self, master):
        self.master = master
        master.title("State Graph Generator")

        tk.Label(master, text="Upper limit of the states (≠ 0):").pack()
        self.entry_upper = tk.Entry(master)
        self.entry_upper.pack()

        tk.Label(master, text="Lower limit of the states (≠ 0):").pack()
        self.entry_lower = tk.Entry(master)
        self.entry_lower.pack()

        radio_frame = tk.Frame(master)
        radio_frame.pack(pady=5)
        tk.Label(radio_frame, text="How far back ?").pack()
        options = ["Direct Predecessors", "All Predecessors"]
        self.var = tk.StringVar(value="")
        for opt in options:
            rb = tk.Radiobutton(radio_frame, text=opt, variable=self.var, value=opt)
            rb.pack(side='left', padx=10)

        tk.Button(master, text="Generate Graphs", command=self.run_program).pack(pady=10)

        # === Frame for Canvas + Legend Side by Side ===
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # === Canvas Frame (left side) ===
        self.canvas_container = tk.Frame(self.main_frame)
        self.canvas_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_container)
        self.scrollbar = tk.Scrollbar(self.canvas_container, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # === Legend Frame (right side) ===
        self.legend_frame = tk.Frame(self.main_frame, padx=10, pady=10)
        self.legend_frame.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Label(self.legend_frame, text="Legend", font=('Arial', 12, 'bold')).pack(pady=(0, 5))
        tk.Label(self.legend_frame, text="Top: Parent Sum", justify='left').pack(anchor='w')
        tk.Label(self.legend_frame, text="Bottom: Node Value", justify='left').pack(anchor='w')

        # Enable mouse wheel scroll
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.figure_canvas = None

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def run_program(self):
        if self.figure_canvas:
            self.figure_canvas.get_tk_widget().destroy()

        try:
            state_upper = int(self.entry_upper.get())
            state_lower = int(self.entry_lower.get())
            algo = self.var.get()

            if state_upper == 0 or state_lower == 0:
                messagebox.showerror("Input Error", "State values must not be 0.")
                return

            # --- Graph Setup ---
            num_layers = random.randint(4, 6)
            nodes_per_layer = [1 + random.randint(0, x) + x for x in range(num_layers)]
            value_range = (-1 * abs(int(state_lower)), abs(int(state_upper)))
            min_parents = 2
            max_parents = 4

            G = nx.DiGraph()
            layers = []
            pos = {}
            node_counter = 0
            y_step = 1.5
            x_gap = 1.5

            def get_color(value):
                if value == 0:
                    return "grey"
                elif value > 0:
                    return "lightblue"
                else:
                    return "red"

            first_value = random.choices([1, 2, -1, -2])[0]
            G.add_node(node_counter, value=first_value)
            G.nodes[node_counter]['parent'] = 0
            layers.append([node_counter])
            pos[node_counter] = (0, 0)
            node_counter += 1

            for i in range(1, len(nodes_per_layer)):
                current_layer = []
                prev_layer = layers[i - 1]
                for _ in range(nodes_per_layer[i]):
                    node_id = node_counter
                    G.add_node(node_id)
                    num_parents = min(len(prev_layer), random.randint(min_parents, max_parents))
                    parents = random.sample(prev_layer, num_parents)
                    for parent in parents:
                        G.add_edge(parent, node_id)
                    current_layer.append(node_id)
                    node_counter += 1
                layers.append(current_layer)

            for node in G.nodes:
                if G.in_degree(node) == 0:
                    continue
                if algo == "Direct Predecessors":
                    parent_sum = sum(G.nodes[p]['value'] for p in G.predecessors(node))
                else:
                    parent_sum = sum(G.nodes[p]['value'] for p in nx.ancestors(G, node))

                rand_val = random.randint(*value_range)
                if rand_val == 0:
                    rand_val = random.choice([1, -1])
                G.nodes[node]["parent"] = parent_sum
                G.nodes[node]['value'] = rand_val + parent_sum

            for i, layer in enumerate(layers):
                x_offset = -(len(layer) - 1) * x_gap / 2
                for j, node in enumerate(layer):
                    pos[node] = (x_offset + j * x_gap, -i * y_step)

            # --- Plotting setup ---
            total_stages = len(layers) + 1
            ncols = 2
            nrows = math.ceil(total_stages / ncols)

            fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(10, nrows * 4), constrained_layout=True)
            axes = axes.flatten()

            node_colors = ['lightblue' if G.nodes[0]['value'] > 0 else 'red'] + ["grey" for n in G.nodes if n != 0]
            node_labels = {n: f"{G.nodes[n]['value']}" if n == 0 else "" for n in G.nodes}

            # Plot initial
            axes[0].set_title("Initial Graph (Only Entrant Active)")
            nx.draw(G, pos,
                    ax=axes[0],
                    with_labels=True,
                    labels=node_labels,
                    node_size=800,
                    node_color=node_colors,
                    edgecolors='black',
                    arrows=True)

            # Plot cascades
            for i in range(1, total_stages):
                for node in layers[i - 1]:
                    val = G.nodes[node]['value']
                    par = G.nodes[node]['parent']
                    node_colors[node] = get_color(val)
                    if node == 0:
                        node_labels[node] = f"{val}"
                    else:
                        node_labels[node] = f"{par}\n{val}"

                axes[i].set_title(f"Activating Layer {i}")
                nx.draw(G, pos,
                        ax=axes[i],
                        with_labels=True,
                        labels=node_labels.copy(),
                        node_size=800,
                        node_color=node_colors.copy(),
                        edgecolors='black',
                        arrows=True)

            # Hide extra subplot boxes
            for j in range(total_stages, len(axes)):
                axes[j].axis('off')

            # --- Embed figure ---
            self.figure_canvas = FigureCanvasTkAgg(fig, master=self.scrollable_frame)
            self.figure_canvas.draw()
            self.figure_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid integer values.")

# --- Run App ---
root = tk.Tk()
app = GraphApp(root)
root.mainloop()


# In[ ]:




