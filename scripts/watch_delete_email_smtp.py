import os, time, smtplib, ssl
from email.mime.text import MIMEText
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ztipe-logs', 'file_activity.log')

def send_email(smtp_host, smtp_port, username, password, to_email, subject, body):
    msg = MIMEText(body)
    msg['From'] = username
    msg['To'] = to_email
    msg['Subject'] = subject
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls(context=context)
            server.login(username, password)
            server.send_message(msg)
        print(f"[EMAIL] Sent to {to_email}")
    except Exception as e:
        print("[EMAIL-ERROR]", e)

class DeleteHandler(FileSystemEventHandler):
    def __init__(self, smtp_host, smtp_port, username, password, to_email):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.to_email = to_email

    def on_deleted(self, event):
        if not event.is_directory:
            ts = time.strftime('%Y-%m-%d %H:%M:%S')
            user = os.getlogin()
            action = 'delete'
            path = event.src_path.replace('\\','/')
            log_line = f"{ts}, {user}, {action}, {path}"
            print("[LOG]", log_line)
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_line + "\n")

            subject = "ALERT: File Deleted"
            body = f"User: {user}\nFile: {path}\nTime: {ts}"
            send_email(self.smtp_host, self.smtp_port, self.username, self.password, self.to_email, subject, body)

if __name__ == "__main__":
    watch_folder = input("Enter folder to monitor (full path): ").strip()
    if not os.path.isdir(watch_folder):
        print("Folder does not exist:", watch_folder)
        exit(1)

    print("\n=== Email configuration ===")
    smtp_host = input("SMTP server (e.g. smtp.gmail.com): ").strip()
    smtp_port = int(input("SMTP port (e.g. 587): ").strip())
    username = input("Your email address: ").strip()
    password = input("Your email password or App Password: ").strip()
    to_email = input("Recipient email address: ").strip()

    handler = DeleteHandler(smtp_host, smtp_port, username, password, to_email)
    observer = Observer()
    observer.schedule(handler, path=watch_folder, recursive=True)
    observer.start()
    print("\nWatching for deletions in", watch_folder)
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
