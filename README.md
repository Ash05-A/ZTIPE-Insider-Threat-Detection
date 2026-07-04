# ZTIPE – Zero Trust Insider Threat Detection System

[![Docker](https://img.shields.io/badge/Docker-✓-blue?logo=docker)](https://www.docker.com/)
[![Kafka](https://img.shields.io/badge/Kafka-✓-231F20?logo=apachekafka)](https://kafka.apache.org/)
[![NiFi](https://img.shields.io/badge/NiFi-✓-728E9B?logo=apachenifi)](https://nifi.apache.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-✓-47A248?logo=mongodb)](https://www.mongodb.com/)
[![Python](https://img.shields.io/badge/Python-✓-3776AB?logo=python)](https://www.python.org/)

**Real‑time insider threat detection** using filesystem monitoring, event streaming, and graph‑based anomaly scoring – fully containerized with Docker Compose.

---

## 🧠 Overview

ZTIPE continuously watches file deletions on a host, streams those events through a modern data pipeline, stores them in a document database, and then applies self‑supervised graph analysis to identify suspicious user behaviour. The entire system is reproducible with a single `docker-compose up -d` command.

---

## 🏗️ Architecture
User deletes file
│
▼
watch_delete.py (Python Watchdog)
│
▼
activity.json (NDJSON)
│
▼
Apache NiFi (TailFile → PublishKafka)
│
▼
Apache Kafka (topic: file-events-json)
│
▼
Python Consumer (manual partition assignment)
│
▼
MongoDB (raw_events + threat_scores)
│
├──► Streamlit Dashboard (live view, threat scores, interaction graph)
└──► Graph Engine (periodic analysis with NetworkX)

text

---

## 🧰 Tech Stack

| Category            | Technology                              |
|---------------------|-----------------------------------------|
| File Monitoring     | Python Watchdog                         |
| Stream Ingestion    | Apache NiFi 2.3.0 (TailFile, PublishKafka) |
| Message Broker      | Apache Kafka 7.5.0 (Confluent)          |
| Database            | MongoDB 6                               |
| Anomaly Detection   | NetworkX, NumPy, Matplotlib (Python)    |
| Dashboard           | Streamlit                               |
| Containerization    | Docker, Docker Compose                  |
| Alerting (optional) | SMTP (Gmail)                            |

---

## 📁 Project Structure
ZTIPE-FINAL/
├── docker-compose.yml # All services orchestrated
├── .gitignore
├── scripts/
│ └── watch_delete.py # Watchdog (CSV + JSON logging)
├── consumer/
│ ├── Dockerfile
│ ├── requirements.txt
│ └── consumer.py # Kafka → MongoDB
├── graph-engine/
│ ├── Dockerfile
│ ├── requirements.txt
│ ├── graph_ssl_threat.py # Graph anomaly scoring
│ └── graph_runner.py # Periodic bridge
├── dashboard/
│ ├── Dockerfile
│ ├── requirements.txt
│ └── dashboard.py # Streamlit app
├── alerter/
│ ├── Dockerfile
│ ├── requirements.txt
│ └── alerter.py # Email alerts (optional)
└── nifi-keys/ # NiFi TLS keystore

text

---

## 🚀 Quick Start

### Prerequisites
- Docker Desktop (Windows/Mac/Linux)
- Git (optional – to clone)

### 1. Clone the repository
```bash
git clone https://github.com/Ash05-A/ZTIPE-Insider-Threat-Detection.git
cd ZTIPE-Insider-Threat-Detection
2. Start the stack
bash
docker-compose up -d
Wait ~30 seconds for all services (Kafka, NiFi, MongoDB, etc.) to become healthy.

3. Start file monitoring
Open a new terminal and run the watchdog:

bash
python scripts/watch_delete.py
Enter the path you want to monitor (e.g., C:\Users\Public\Desktop).
The script will log both CSV and NDJSON to the ztipe-logs folder.

4. Access the dashboard
Open http://localhost:8501 in your browser.

📊 Dashboard Features
Live Event Feed – every file deletion appears instantly.

Threat Scores – bar chart of anomaly scores per user, refreshed automatically.

Suspicious User Highlight – users above the threshold are flagged in red.

Interaction Graph (optional) – a visual node‑edge diagram of user–file relationships (can be enabled with a shared volume).

🧪 Demo Walkthrough
Start the stack (docker-compose up -d).

Run the watchdog on a test folder.

Delete one or more files in that folder.

Open the dashboard – the deleted file appears in the “Recent File Events” table.

Wait ~5 minutes (or manually trigger the graph engine) – threat scores and suspicious users appear.

(Optional) Check Kafka messages:

bash
docker exec -it ztipe-final-kafka-1 kafka-console-consumer --topic file-events-json --bootstrap-server localhost:9092 --from-beginning --max-messages 1
(Optional) View MongoDB data via Compass on localhost:27017.

🧠 How the Anomaly Detection Works
Events are collected from MongoDB for the last 5 minutes.

A directed graph is built: User nodes → File nodes, with weighted edges (number of interactions).

Each node’s total interaction weight is computed and normalised (0 = normal, 1 = most anomalous).

Scores are stored back into MongoDB and displayed in the dashboard.

✉️ Email Alerts (Optional)
Set real Gmail credentials in the alerter environment variables inside docker-compose.yml:

yaml
- SENDER_EMAIL=your.email@gmail.com
- SENDER_PASSWORD=your_app_password
Then rebuild:

bash
docker-compose up -d --build alerter
An email is sent whenever a user’s anomaly score exceeds 0.7.

✅ Resume Claims – All True
This project backs the following statements with a live, containerized system:

Built a real‑time event‑streaming pipeline using Python Watchdog, Apache NiFi, and Apache Kafka to collect and process file‑system activity.

Applied graph‑based analysis and anomaly‑scoring techniques to detect anomalous behavioural patterns; persisted results in MongoDB.

Containerized the full application using Docker and Docker Compose for reproducible deployment.

🐞 Troubleshooting
NiFi UI not loading? Wait 2–3 minutes after docker-compose up. NiFi 2.3.0 takes time to initialise. Check docker logs ztipe-final-nifi-1.

Consumer not inserting? Verify the Kafka topic exists: docker exec -it ztipe-final-kafka-1 kafka-topics --list --bootstrap-server localhost:9092. If missing, recreate file-events-json.

Dashboard empty? Trigger a new file deletion while the watchdog is running. Events appear within seconds.

📄 License
This project is intended for educational and portfolio purposes. Feel free to fork and extend.