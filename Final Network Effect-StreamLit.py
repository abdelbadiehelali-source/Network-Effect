#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import random
import math
import networkx as nx
import matplotlib.pyplot as plt

st.title("State Graph Generator")

# Legend section
st.sidebar.markdown("### Legend")
st.sidebar.markdown("- **Top Number:** Parent Sum")
st.sidebar.markdown("- **Bottom Number:** Node Value")
st.sidebar.markdown("- **Blue:** Positive Values")
st.sidebar.markdown("- **Red:** Negative Values")
st.sidebar.markdown("- **Gray:** Neutral or Unused Nodes")

# === Inputs ===
state_upper = st.number_input("Upper limit of the states (≠ 0)", value=5, step=1)
state_lower = st.number_input("Lower limit of the states (≠ 0)", value=-5, step=1)
algo = st.radio("How far back?", ["Direct Predecessors", "All Predecessors"])
generate = st.button("Generate Graphs")

# === Function to generate and display graphs ===
def run_program(state_upper, state_lower, algo):
    if state_upper == 0 or state_lower == 0:
        st.error("State values must not be 0.")
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

    first_value = random.choices([x for x in range(state_lower, state_upper, 1)] if x != 0)[0]
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

    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(10, nrows * 4))
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

    for j in range(total_stages, len(axes)):
        axes[j].axis('off')

    st.pyplot(fig)

# === Run ===
if generate:
    run_program(state_upper, state_lower, algo)


# In[ ]:




