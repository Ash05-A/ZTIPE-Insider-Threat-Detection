import time, os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import yagmail  # new: for sending email

# log file path inside host project
log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ztipe-logs', 'file_activity.log')

# ====== EMAIL CONFIG ======
EMAIL_USER = "your.email@gmail.com"          # your Gmail
EMAIL_APP_PASSWORD = "your_app_password"    # Gmail App Password
EMAIL_TO = "your.email@gmail.com"           # recipient
# ==========================

class DeleteHandler(FileSystemEventHandler):
    def on_deleted(self, event):
        if not event.is_directory:
            ts = time.strftime('%Y-%m-%d %H:%M:%S')
            user = 'ash'
            action = 'delete'
            path = event.src_path.replace('\\','/')
            log_line = f"{ts}, {user}, {action}, {path}"
            
            # 1️⃣ write to log
            print("[LOG]", log_line)
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_line + "\n")
            
            # 2️⃣ send email
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

if __name__ == "__main__":
    watch_folder = input("Enter folder to monitor (full path): ").strip()
    if not os.path.isdir(watch_folder):
        print("Folder does not exist:", watch_folder)
        exit(1)

    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    event_handler = DeleteHandler()
    observer = Observer()
    observer.schedule(event_handler, path=watch_folder, recursive=True)
    observer.start()
    print("Watching for deletions in", watch_folder)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
