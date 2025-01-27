import ffmpeg
import sqlite3
from kafka import KafkaConsumer
import os
import json

KAFKA_TOPIC = "video_files"
KAFKA_SERVER = 'localhost:9092'

def check_video(file_path):
    try:
        probe = ffmpeg.probe(file_path)
        if not probe['streams']:
            return "Corrupted"
        if os.path.getsize(file_path) < 1024 * 10:
            return "Corrupted"
        return "Passed"
    except Exception:
        return "Corrupted"

def log_quality_status(file_path, quality_result="Passed"):
    try:
        print(f"Updating quality status for {file_path} with result: {quality_result}")
        conn = sqlite3.connect('video_status.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE video_status
            SET quality_check_result = ?
            WHERE file_path = ?
        ''', (quality_result, file_path))
        conn.commit()
        print(f"Database updated for {file_path}")
    except Exception as e:
        print(f"Error updating quality status in database: {e}")
    finally:
        conn.close()

def main():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_SERVER,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='video-quality-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    for message in consumer:
        file_path = message.value.get('file_path')
        if file_path:
            print(f"Quality checking file: {file_path}")
            result = check_video(file_path)
            log_quality_status(file_path, result)
            print(f"Quality check result: {result}")

if __name__ == "__main__":
    main()

