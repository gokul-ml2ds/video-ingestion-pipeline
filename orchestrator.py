import tkinter as tk
from utils import VideoHandler, WATCH_DIR  # Import from shared.py
from kafka import KafkaProducer
import json
import os
from gui import FileMonitorApp  

KAFKA_TOPIC = "video_files"
KAFKA_SERVER = 'localhost:9092'

# List of common video file extensions
VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm"}

producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)

if __name__ == "__main__":
    root = tk.Tk()
    app = FileMonitorApp(root)
    root.protocol("WM_DELETE_WINDOW", app.stop_monitoring)
    root.mainloop()
