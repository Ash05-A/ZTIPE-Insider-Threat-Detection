import os
import sys
import json
import networkx as nx
import numpy as np
import matplotlib
matplotlib.use('Agg')   # <-- Force headless backend early
import matplotlib.pyplot as plt

# ---------------- CONFIG ----------------
log_file_path = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\yashd\ztipe-1A\ztipe-logs\file_activity.log"

# ---------------- READ LOG ----------------
if not os.path.exists(log_file_path):
    print("Log file not found. Run Watchdog first to generate logs.")
    exit(1)

G = nx.DiGraph()

with open(log_file_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue

        try:
            ts, user, action, file_path = [x.strip() for x in line.split(",", 3)]
        except ValueError:
            continue

        G.add_node(user, type="user")
        G.add_node(file_path, type="file")

        if G.has_edge(user, file_path):
            G[user][file_path]['weight'] += 1
        else:
            G.add_edge(user, file_path, weight=1)

# ---------------- SELF-SUPERVISED THREAT SCORING ----------------
scores = {}

for node in G.nodes():
    edges = G.edges(node, data=True)
    score = sum(d.get('weight', 1) for _, _, d in edges)
    scores[node] = score

# Avoid crash if empty graph
if scores:
    max_score = max(scores.values())
else:
    max_score = 1

# Normalize
for node in scores:
    scores[node] = scores[node] / max_score if max_score != 0 else 0

# ---------------- OUTPUT TOP SUSPICIOUS NODES ----------------
print("\nTop suspicious nodes (higher score = more anomalous):")

top_nodes = sorted(scores.items(), key=lambda x: x[1], reverse=True)

for node, score in top_nodes:
    print(f"{node}: {score:.3f}")

# ---------------- JSON OUTPUT (PIPELINE READY) ----------------
output = {
    "results": [
        {"user": node, "score": float(score)}
        for node, score in top_nodes
    ]
}

print("\n--- JSON OUTPUT ---")
print(json.dumps(output))

# ---------------- OPTIONAL: PLOT (DISABLED IN HEADLESS MODE) ----------------
# In Docker container the plot is saved to file instead of displayed.
save_plot = os.environ.get("SAVE_GRAPH_PLOT", "false").lower() == "true"
if save_plot:
    plt.figure(figsize=(10, 6))
    types = nx.get_node_attributes(G, 'type')
    colors = ['skyblue' if types.get(n) == 'user' else 'lightgreen' for n in G.nodes()]
    weights = [G[u][v]['weight'] for u, v in G.edges()]
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color=colors, node_size=1200, width=weights)
    plt.title("Graph SSL Threat Scoring")
    plot_path = os.environ.get("PLOT_OUTPUT_PATH", "/tmp/graph.png")
    plt.savefig(plot_path)
    print(f"Plot saved to {plot_path}")
else:
    # plt.show()   # <-- Removed to avoid headless display error
    pass