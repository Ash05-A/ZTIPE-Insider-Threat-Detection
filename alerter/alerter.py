import os, time, smtplib
from email.message import EmailMessage
from pymongo import MongoClient

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://mongo:27017")
SMTP_SERVER = os.environ["SMTP_SERVER"]
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SENDER = os.environ["SENDER_EMAIL"]
PASSWORD = os.environ["SENDER_PASSWORD"]
RECIPIENT = os.environ["RECIPIENT_EMAIL"]

client = MongoClient(MONGO_URI)
db = client["ztipe"]
checkpoint_col = db["alert_checkpoint"]

def get_last_processed():
    doc = checkpoint_col.find_one({"_id": "last_alert"})
    return doc["timestamp"] if doc else None

def update_processed(ts):
    checkpoint_col.update_one({"_id": "last_alert"}, {"$set": {"timestamp": ts}}, upsert=True)

def send_alert(scores):
    msg = EmailMessage()
    msg["Subject"] = "ZTIPE Insider Threat Alert"
    msg["From"] = SENDER
    msg["To"] = RECIPIENT
    body = "Suspicious users detected:\n\n"
    for s in scores:
        body += f"{s['username']} - anomaly score: {s['anomaly_score']}\n"
    msg.set_content(body)
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER, PASSWORD)
        server.send_message(msg)
    print("Alert email sent.")

while True:
    last = get_last_processed()
    latest_doc = db.threat_scores.find_one(sort=[("calculation_time", -1)])
    if latest_doc and (not last or latest_doc["calculation_time"] > last):
        suspicious = [s for s in latest_doc["scores"] if s.get("suspicious")]
        if suspicious:
            print(f"New alert: {len(suspicious)} suspicious users")
            send_alert(suspicious)
        update_processed(latest_doc["calculation_time"])
    time.sleep(60)