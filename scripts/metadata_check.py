import json
from kafka import KafkaConsumer
import subprocess
import sqlite3
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')    

KAFKA_TOPIC = "video_files"
KAFKA_SERVER = 'localhost:9092'

def extract_metadata(file_path):
    try:
        # Check for accompanying JSON metadata file
        metadata_file = f"{os.path.splitext(file_path)[0]}.json"
        if not os.path.exists(metadata_file):
            print(f"Metadata file missing for {file_path}. Sending notification.")
            send_email_notification(file_path)
            return None

        # Load metadata from JSON file
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)

        return metadata

    except Exception as e:
        print(f"Error extracting metadata: {e}")
        return None

def send_email_notification(file_path):
    recipient = "gokuln@seas.upenn.edu"
    subject = "Missing Metadata Notification"
    body = f"The metadata file for {file_path} is missing. Please create it manually."

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_USER
    msg['To'] = recipient

    try:
        # Connect to Gmail's SMTP server using SSL
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
        print(f"\033[92mEmail sent to {recipient} about missing metadata for {file_path}.\033[0m")
    except Exception as e:
        print(f"\033[91mFailed to send email notification: {e}\033[0m")

def log_metadata_status(file_path, metadata_present):
    try:
        conn = sqlite3.connect('video_status.db')
        cursor = conn.cursor()
        
        # Check if record exists
        cursor.execute('SELECT 1 FROM video_status WHERE file_path = ?', (file_path,))
        exists = cursor.fetchone() is not None
        
        if exists:
            cursor.execute('''
                UPDATE video_status
                SET metadata_present = ?
                WHERE file_path = ?
            ''', (metadata_present, file_path))
        else:
            cursor.execute('''
                INSERT INTO video_status (file_path, arrival_time, metadata_present)
                VALUES (?, ?, ?)
            ''', (file_path, datetime.now().isoformat(), metadata_present))
            
        conn.commit()
    except Exception as e:
        print(f"Error updating metadata status: {e}")
    finally:
        conn.close()

def update_metadata_status(file_path, metadata_present):
    conn = sqlite3.connect('video_status.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE video_status
        SET metadata_present = ?
        WHERE file_path = ?
    ''', (metadata_present, file_path))
    conn.commit()
    conn.close()

def main():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_SERVER,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='video-metadata-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    for message in consumer:
        file_path = message.value.get('file_path')
        if file_path:
            print(f"Processing file: {file_path}")
            metadata = extract_metadata(file_path)
            metadata_present = metadata is not None
            log_metadata_status(file_path, metadata_present)
            if metadata_present:
                print(f"Metadata for {file_path}: {json.dumps(metadata, indent=2)}")
            else:
                print(f"Failed to extract metadata for {file_path}")
    

if __name__ == "__main__":
    main()