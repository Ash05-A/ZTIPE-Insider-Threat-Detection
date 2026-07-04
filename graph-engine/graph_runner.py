import os, sys, time, subprocess, json
from datetime import datetime, timedelta
from pymongo import MongoClient

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://mongo:27017")
TEMP_LOG = "/tmp/temp_activity.log"
WINDOW_MINUTES = 5

def run():
    client = MongoClient(MONGO_URI)
    db = client["ztipe"]
    cutoff = datetime.utcnow() - timedelta(minutes=WINDOW_MINUTES)

    events = list(db.raw_events.find({
        "timestamp": {"$gte": cutoff.strftime("%Y-%m-%d %H:%M:%S")}
    }).sort("timestamp", 1))

    if not events:
        print("No events in window.")
        client.close()
        return

    with open(TEMP_LOG, 'w', encoding='utf-8') as f:
        for ev in events:
            line = f"{ev['timestamp']}, {ev['username']}, {ev['action']}, {ev['filepath']}\n"
            f.write(line)

    try:
        result = subprocess.run(
            ["python", "graph_ssl_threat.py", TEMP_LOG],
            capture_output=True, text=True, check=True
        )
        output = result.stdout
        print("Graph output:\n", output)
    except subprocess.CalledProcessError as e:
        print("Graph script failed:", e.stderr)
        client.close()
        return

    scores = {}
    try:
        json_start = output.find('--- JSON OUTPUT ---')
        if json_start != -1:
            json_str = output[json_start:].split('\n', 1)[1].strip()
            data = json.loads(json_str)
            for item in data.get("results", []):
                scores[item["user"]] = item["score"]
    except:
        pass

    if not scores:
        for line in output.splitlines():
            if ':' in line:
                node, score_str = line.split(':', 1)
                try:
                    scores[node.strip()] = float(score_str.strip())
                except ValueError:
                    pass

    now = datetime.utcnow()
    window_start = now - timedelta(minutes=WINDOW_MINUTES)
    doc = {
        "calculation_time": now.isoformat(),
        "window_start": window_start.isoformat(),
        "window_end": now.isoformat(),
        "scores": [
            {"username": user, "anomaly_score": score, "suspicious": score > 0.7}
            for user, score in scores.items()
        ]
    }
    db.threat_scores.insert_one(doc)
    print(f"Stored {len(doc['scores'])} scores.")
    client.close()

if __name__ == "__main__":
    while True:
        run()
        time.sleep(60 * 5)   # every 5 minutes