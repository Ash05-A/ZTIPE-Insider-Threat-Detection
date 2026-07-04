import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime
import math

LOG_FILE = r"C:\Users\yashd\ztipe-1A\ztipe-logs\file_activity.log"
HALF_LIFE_MINUTES = 60

def decay_weight(ts_str, current_time, half_life=HALF_LIFE_MINUTES):
    ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
    delta_minutes = (current_time - ts).total_seconds() / 60
    return math.exp(-delta_minutes / half_life)

G = nx.DiGraph()

def process_line(line):
    line = line.strip()
    if not line:
        return
    try:
        ts, user, action, file_path = [x.strip() for x in line.split(",", 3)]
    except ValueError:
        return
    now = datetime.now()
    weight = decay_weight(ts, now)
    G.add_node(user, type="user")
    G.add_node(file_path, type="file")
    if G.has_edge(user, file_path):
        G[user][file_path]["weight"] += weight
        if action not in G[user][file_path]["actions"]:
            G[user][file_path]["actions"].append(action)
    else:
        G.add_edge(user, file_path, weight=weight, actions=[action])

# Read all log lines
with open(LOG_FILE, "r", encoding="utf-8") as f:
    for line in f:
        process_line(line)

# Draw graph
plt.figure(figsize=(12,8))
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=1200)
edge_labels = {(u,v): f"{d['weight']:.2f}" for u,v,d in G.edges(data=True)}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
plt.show()
