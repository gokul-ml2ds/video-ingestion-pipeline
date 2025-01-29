import sqlite3
from watchdog.events import FileSystemEventHandler
from kafka import KafkaProducer
import json
import os
from scripts.metadata_check import extract_metadata, update_metadata_status
from scripts.quality_check import check_video_quality
from scripts.process_video import process_video
from utils.database import ensure_database

WATCH_DIR = "videos"
KAFKA_TOPIC = "video_files"
JSON_TOPIC = "video_metadata"
KAFKA_SERVER = 'localhost:9092'

# List of common video file extensions
VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm"}



ensure_database()
producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)

class VideoHandler(FileSystemEventHandler):
    def __init__(self, app):
        self.app = app

    def on_created(self, event):
        if event.is_directory:
            return

        file_path = event.src_path
        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext in VIDEO_EXTENSIONS:
            self.process_video_file(file_path)
        elif file_ext == ".json":
            self.process_metadata_file(file_path)

    def process_video_file(self, file_path):
        # Send message to Kafka
        message = {"file_path": file_path}
        producer.send(KAFKA_TOPIC, json.dumps(message).encode('utf-8'))
        self.app.display_message(f"\033[92mNew video file detected: {file_path}\033[0m")


    def process_metadata_file(self, metadata_file):
        # Extract the corresponding video file path
        video_file_path = os.path.splitext(metadata_file)[0] + ".mp4"  # Assuming .mp4, adjust as needed
        if os.path.exists(video_file_path):
            # Update the database to reflect that metadata is now present
            update_metadata_status(video_file_path, True)
            print(f"\033[92mMetadata file detected and database updated for {video_file_path}.\033[0m")
            # Send message to JSON_TOPIC
            message = {"file_path": video_file_path, "metadata_file": metadata_file}
            producer.send(JSON_TOPIC, json.dumps(message).encode('utf-8'))
            self.app.display_message(f"\033[92mMetadata file detected: {metadata_file}\033[0m")

