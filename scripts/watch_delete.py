import time, os
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import yagmail  # email alerts

# ================== LOG PATH ==================
log_file = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'ztipe-logs',
    'file_activity.log'
)

json_file = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'ztipe-logs',
    'activity.json'
)

os.makedirs(os.path.dirname(log_file), exist_ok=True)

# ================== EMAIL CONFIG ==================
EMAIL_USER = "your.email@gmail.com"
EMAIL_APP_PASSWORD = "your_app_password"
EMAIL_TO = "your.email@gmail.com"


# ================== JSON LOGGER ==================
def write_json_event(ts, user, action, file_path):
    entry = {
        "timestamp": ts,
        "username": user,
        "action": action,
        "filepath": file_path
    }

    with open(json_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


# ================== WATCHDOG HANDLER ==================
class DeleteHandler(FileSystemEventHandler):
    def on_deleted(self, event):
        if not event.is_directory:

            ts = time.strftime('%Y-%m-%d %H:%M:%S')
            user = 'ash'
            action = 'delete'
            path = event.src_path.replace('\\', '/')

            log_line = f"{ts}, {user}, {action}, {path}"

            # 1️⃣ write CSV-like log
            print("[LOG]", log_line)
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_line + "\n")

            # 2️⃣ write JSON log (FOR NIFI / KAFKA)
            write_json_event(ts, user, action, path)

            # 3️⃣ send email alert
            subject = "ALERT: File deleted!"
            body = f"""
Critical file delete detected.
User: {user}
File: {path}
Time: {ts}
"""

            try:
                yag = yagmail.SMTP(EMAIL_USER, EMAIL_APP_PASSWORD)
                yag.send(EMAIL_TO, subject, body)
                print("[EMAIL] Alert sent!")
            except Exception as e:
                print("[ERROR] Failed to send email:", e)


# ================== MAIN ==================
if __name__ == "__main__":
    watch_folder = input("Enter folder to monitor (full path): ").strip()

    if not os.path.isdir(watch_folder):
        print("Folder does not exist:", watch_folder)
        exit(1)

    event_handler = DeleteHandler()
    observer = Observer()
    observer.schedule(event_handler, path=watch_folder, recursive=True)

    observer.start()
    print("Watching for deletions in:", watch_folder)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()