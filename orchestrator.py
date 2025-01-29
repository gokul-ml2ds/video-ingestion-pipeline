import tkinter as tk
from kafka import KafkaProducer
from app.gui import FileMonitorApp  

KAFKA_TOPIC = "video_files"
KAFKA_SERVER = 'localhost:9092'

# List of common video file extensions
VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm"}

producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)

if __name__ == "__main__":
    root = tk.Tk()
    app = FileMonitorApp(root)
    root.protocol("WM_DELETE_WINDOW", app.exit_app)
    root.mainloop()
