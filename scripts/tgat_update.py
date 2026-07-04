# tgat_update.py
import time
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import dgl
from dgl.nn import TGATConv

CSV_FILE = r"C:\Users\yashd\ztipe-1A\scripts\temporal_edges.csv"
CHECK_INTERVAL = 5  # seconds

# -------- TGAT MODEL --------
class SimpleTGAT(nn.Module):
    def __init__(self, in_dim=1, out_dim=16, num_heads=2, time_dim=16):
        super().__init__()
        self.tgat = TGATConv(in_dim, out_dim, time_dim=time_dim, num_heads=num_heads)
    def forward(self, g, x, edge_time):
        return self.tgat(g, x, edge_time)

model = SimpleTGAT()
prev_embeddings = None

print("TGAT updater running... monitoring CSV for new edges.")

while True:
    try:
        edges = pd.read_csv(CSV_FILE, names=["src","dst","action","ts"])
        if edges.empty:
            time.sleep(CHECK_INTERVAL)
            continue
        
        nodes = pd.Index(edges["src"].append(edges["dst"]).unique())
        node2id = {n:i for i,n in enumerate(nodes)}
        edges["src_id"] = edges["src"].map(node2id)
        edges["dst_id"] = edges["dst"].map(node2id)
        edges["timestamp"] = pd.to_datetime(edges["ts"]).astype(int)//10**9  # seconds

        src = torch.tensor(edges["src_id"].values)
        dst = torch.tensor(edges["dst_id"].values)
        ts = torch.tensor(edges["timestamp"].values, dtype=torch.float32)

        g = dgl.graph((src, dst))
        x = torch.ones(g.num_nodes(), 1)  # simple feature

        embeddings = model(g, x, ts)

        if prev_embeddings is not None and embeddings.shape[0] == prev_embeddings.shape[0]:
            drift_scores = 1 - F.cosine_similarity(prev_embeddings, embeddings)
            for n, drift in zip(nodes, drift_scores):
                print(f"[DRIFT] Node {n}: {drift.item():.3f}")
        prev_embeddings = embeddings.clone()

    except Exception as e:
        print("[TGAT-ERROR]", e)

    time.sleep(CHECK_INTERVAL)
