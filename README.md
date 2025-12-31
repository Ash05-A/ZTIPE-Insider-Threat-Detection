# ZTIPE – Zero Trust Insider Threat Detection
ZTIPE is a Python-based cybersecurity project that detects suspicious insider activities using file-system monitoring and graph-based behavior analysis.
## Modules Implemented
### File Deletion Monitoring
- Monitors a selected folder in real time
- Logs file deletion activities with timestamp, user, and file path
- Generates a structured activity log for further analysis

### Temporal Graph-Based Alerting
- Builds a temporal behavior graph from file activity logs
- Detects abnormal deletion patterns based on frequency and timing
- Triggers alerts for suspicious user behavior (email support optional)

### Graph-Based Self-Supervised Threat Scoring
- Constructs a user–file interaction graph from activity logs
- Computes anomaly scores using graph structure without labeled data
- Identifies potentially malicious insider nodes based on behavior intensity

## Technologies Used
- Python
- Watchdog
- NetworkX
- Matplotlib

## Project Use Case
This system is designed to assist organizations in identifying insider threats by continuously monitoring file activities and analyzing user behavior without requiring prior attack labels.

## Status
Partial implementation completed 
