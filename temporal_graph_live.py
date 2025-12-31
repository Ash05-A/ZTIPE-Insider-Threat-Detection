# temporal_graph_email_live.py
import time, os, math
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import networkx as nx
import smtplib
from email.message import EmailMessage
import matplotlib.pyplot as plt

# ---------------- CONFIG ----------------
WATCH_FOLDER = input("Enter folder to monitor (full path): ").strip()
LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ztipe-logs', 'file_activity.log')
HALF_LIFE_MINUTES = 60  # decay half-life in minutes

# Email configuration
SMTP_SERVER = input("SMTP server (e.g. smtp.gmail.com): ").strip()
SMTP_PORT = int(input("SMTP port (e.g. 587): ").strip())
EMAIL_USER = input("Your email address: ").strip()
EMAIL_PASS = input("Your email password or App Password: ").strip()
EMAIL_TO = input("Recipient email address: ").strip()

# Ensure log folder exists
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# ---------------- GRAPH INIT ----------------
G = nx.DiGraph()
plt.ion()  # interactive plotting
plt.figure(figsize=(12,8))

# ---------------- FUNCTIONS ----------------
def decay_weight(ts_str, current_time, half_life=HALF_LIFE_MINUTES):
    ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
    delta_minutes = (current_time - ts).total_seconds() / 60
    return math.exp(-delta_minutes / half_life)

def decay_edges():
    """Decay all edges continuously based on timestamp."""
    now = datetime.now()
    for u, v, d in G.edges(data=True):
        if 'ts' in d:
            d['weight'] = decay_weight(d['ts'], now)

def plot_graph():
    plt.clf()
    pos = nx.spring_layout(G)
    
    # Node colors
    node_colors = ['skyblue' if G.nodes[n].get('type')=='user' else 'lightgreen' for n in G.nodes()]
    
    # Edge colors based on weight (strong red → faded gray)
    edge_colors = []
    for u, v, d in G.edges(data=True):
        w = d['weight']
        color_intensity = min(max(w, 0.0), 1.0)
        # red color with fading alpha
        edge_colors.append((1.0, 0.0, 0.0, color_intensity))
    
    nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=1200,
            edge_color=edge_colors, width=2)
    
    # Edge labels
    edge_labels = {(u,v): f"{d['weight']:.2f}" for u,v,d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    
    plt.pause(0.1)

def send_email(user, file_path, timestamp):
    msg = EmailMessage()
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_TO
    msg['Subject'] = f"ALERT: File deleted - {os.path.basename(file_path)}"
    msg.set_content(f"Critical file delete detected.\nUser: {user}\nFile: {file_path}\nTime: {timestamp}")
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)
        print(f"[EMAIL] Sent to {EMAIL_TO}")
    except Exception as e:
        print("[EMAIL-ERROR]", e)

def process_log_line(line):
    line = line.strip()
    if not line:
        return
    try:
        ts, user, action, file_path = [x.strip() for x in line.split(",", 3)]
    except ValueError:
        return
    now = datetime.now()
    weight = decay_weight(ts, now)

    # Update graph
    G.add_node(user, type="user")
    G.add_node(file_path, type="file")
    if G.has_edge(user, file_path):
        G[user][file_path]["weight"] += weight
        if action not in G[user][file_path]["actions"]:
            G[user][file_path]["actions"].append(action)
        G[user][file_path]["ts"] = ts
    else:
        G.add_edge(user, file_path, weight=weight, actions=[action], ts=ts)

    print(f"[GRAPH-UPDATE] {user} -> {file_path} | weight: {G[user][file_path]['weight']:.3f} | actions: {G[user][file_path]['actions']}")

    # Send email only for deletions
    if action.lower() == "delete":
        send_email(user, file_path, ts)

# ---------------- WATCHDOG ----------------
class DeleteHandler(FileSystemEventHandler):
    def on_deleted(self, event):
        if not event.is_directory:
            ts = time.strftime('%Y-%m-%d %H:%M:%S')
            user = 'ash'
            action = 'delete'
            path = event.src_path.replace('\\','/')
            log_line = f"{ts}, {user}, {action}, {path}"
            print("[LOG]", log_line)
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(log_line + "\n")
            process_log_line(log_line)

# ---------------- MAIN ----------------
if __name__ == "__main__":
    if not os.path.isdir(WATCH_FOLDER):
        print("Folder does not exist:", WATCH_FOLDER)
        exit(1)
    
    event_handler = DeleteHandler()
    observer = Observer()
    observer.schedule(event_handler, path=WATCH_FOLDER, recursive=True)
    observer.start()
    print("Watching for deletions in", WATCH_FOLDER)

    try:
        while True:
            time.sleep(1)
            decay_edges()   # continuously decay old edges
            plot_graph()    # refresh the graph
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
