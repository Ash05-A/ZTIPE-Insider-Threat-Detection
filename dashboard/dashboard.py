import streamlit as st
from pymongo import MongoClient
import os

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://mongo:27017")
client = MongoClient(MONGO_URI)
db = client["ztipe"]

st.set_page_config(page_title="ZTIPE Dashboard", layout="wide")
st.title("ZTIPE Insider Threat Dashboard")

st.header("Recent File Events")
events = list(db.raw_events.find().sort("timestamp", -1).limit(100))
if events:
    # Show as table – Streamlit handles list of dicts natively
    # Pick only the fields you care about
    filtered = [ { "timestamp": e["timestamp"], "username": e["username"], "action": e["action"], "filepath": e["filepath"] } for e in events ]
    st.dataframe(filtered, use_container_width=True)
else:
    st.info("No events recorded yet.")

st.header("Latest Threat Scores")
latest = db.threat_scores.find_one(sort=[("calculation_time", -1)])
if latest:
    st.write(f"Analysis window: {latest['window_start']} → {latest['window_end']}")
    scores = latest.get("scores", [])
    if scores:
        # Build a dict suitable for st.bar_chart (no pandas needed)
        usernames = [s["username"] for s in scores]
        anomaly_scores = [s["anomaly_score"] for s in scores]
        chart_data = {"username": usernames, "anomaly_score": anomaly_scores}
        st.bar_chart(chart_data, x="username", y="anomaly_score")
        st.dataframe(scores)
        suspicious = [s["username"] for s in scores if s.get("suspicious")]
        if suspicious:
            st.error(f"⚠️ Suspicious users detected: {', '.join(suspicious)}")
else:
    st.info("No scores computed yet.")

st.header("User‑File Interaction Graph")
graph_path = "/plots/graph.png"
if os.path.exists(graph_path):
    st.image(graph_path, caption="Real‑time interaction graph", use_container_width=True)
else:
    st.info("Graph image will appear after the next analysis cycle.")