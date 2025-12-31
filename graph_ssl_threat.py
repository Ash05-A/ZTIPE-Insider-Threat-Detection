# graph_ssl_threat.py
import os
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

# ---------------- CONFIG ----------------
log_file_path = r"C:\Users\yashd\ztipe-1A\ztipe-logs\file_activity.log"


# ---------------- READ LOG ----------------
if not os.path.exists(log_file_path):
    print("Log file not found. Run Module 1/2A first to generate logs.")
    exit(1)

G = nx.DiGraph()

with open(log_file_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        ts, user, action, file_path = [x.strip() for x in line.split(",", 3)]
        G.add_node(user, type="user")
        G.add_node(file_path, type="file")
        if G.has_edge(user, file_path):
            G[user][file_path]['weight'] += 1
        else:
            G.add_edge(user, file_path, weight=1)

# ---------------- SELF-SUPERVISED THREAT SCORING ----------------
# Simplified: anomaly score = sum of edge weights for a node
scores = {}
for node in G.nodes():
    edges = G.edges(node, data=True)
    score = sum(d['weight'] for _, _, d in edges)
    scores[node] = score

# Normalize scores
max_score = max(scores.values()) if scores else 1
for node in scores:
    scores[node] /= max_score

# ---------------- OUTPUT TOP SUSPICIOUS NODES ----------------
print("\nTop suspicious nodes (higher score = more anomalous):")
top_nodes = sorted(scores.items(), key=lambda x: x[1], reverse=True)
for node, score in top_nodes:
    print(f" {node}: {score:.3f}")

# ---------------- OPTIONAL: PLOT ----------------
plt.figure(figsize=(10,6))
types = nx.get_node_attributes(G, 'type')
colors = ['skyblue' if types[n]=='user' else 'lightgreen' for n in G.nodes()]
weights = [G[u][v]['weight'] for u,v in G.edges()]
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color=colors, node_size=1200, width=weights)
plt.title("Graph SSL Threat Scoring")
plt.show()
