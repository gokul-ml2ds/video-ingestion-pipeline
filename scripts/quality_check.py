import ffmpeg
import sqlite3
from kafka import KafkaConsumer
import os
import json
from datetime import datetime


KAFKA_TOPIC = "video_files"
KAFKA_SERVER = 'localhost:9092'

def check_video_quality(file_path):
    try:
        score = 10  # Start with perfect score
        issues = []
        
        # Check if file exists and is readable
        if not os.path.exists(file_path):
            return 0, ["File does not exist"]
        
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size < 1024 * 10:  # Less than 10KB
            score -= 3
            issues.append("Extremely small file size")
        elif file_size < 1024 * 100:  # Less than 100KB
            score -= 2
            issues.append("Suspicious file size")
            
        # Probe video for detailed information
        try:
            probe = ffmpeg.probe(file_path)
            
            # Check for video streams
            video_streams = [stream for stream in probe['streams'] 
                           if stream['codec_type'] == 'video']
            if not video_streams:
                score -= 5
                issues.append("No video streams found")
            else:
                # Check video duration
                duration = float(probe['format'].get('duration', 0))
                if duration < 1:
                    score -= 2
                    issues.append("Video too short")
                
                # Check video resolution
                width = int(video_streams[0].get('width', 0))
                height = int(video_streams[0].get('height', 0))
                if width < 480 or height < 360:
                    score -= 1
                    issues.append("Low resolution")
                
                # Check bitrate
                bit_rate = int(probe['format'].get('bit_rate', 0))
                if bit_rate < 100000:  # Less than 100Kbps
                    score -= 1
                    issues.append("Low bitrate")
            
            # Check for audio streams
            audio_streams = [stream for stream in probe['streams'] 
                           if stream['codec_type'] == 'audio']
            if not audio_streams:
                score -= 2
                issues.append("No audio streams found")
                
        except ffmpeg.Error:
            score = 0
            issues.append("File corruption detected")
            
        # Ensure score stays within 0-10 range
        score = max(0, min(10, score))
        
        return score, issues
        
    except Exception as e:
        return 0, [f"Error during quality check: {str(e)}"]

def log_quality_status(file_path, quality_score, issues):
    try:
        print(f"Updating quality status for {file_path} with score: {quality_score}")
        conn = sqlite3.connect('video_status.db')
        cursor = conn.cursor()
        
        # Check if record exists
        cursor.execute('SELECT 1 FROM video_status WHERE file_path = ?', (file_path,))
        exists = cursor.fetchone() is not None
        
        quality_result = "Failed" if quality_score < 7 or "File corruption detected" in issues else "Passed"
        quality_details = json.dumps({"score": quality_score, "issues": issues})
        
        if exists:
            cursor.execute('''
                UPDATE video_status
                SET quality_check_result = ?,
                    quality_score = ?,
                    quality_details = ?
                WHERE file_path = ?
            ''', (quality_result, quality_score, quality_details, file_path))
        else:
            cursor.execute('''
                INSERT INTO video_status (
                    file_path, 
                    arrival_time, 
                    quality_check_result,
                    quality_score,
                    quality_details
                )
                VALUES (?, ?, ?, ?, ?)
            ''', (file_path, datetime.now().isoformat(), quality_result, 
                 quality_score, quality_details))
            
        conn.commit()
        print(f"Database updated for {file_path}")
            
    except sqlite3.IntegrityError as e:
        # If there's a conflict, try to update instead
        try:
            cursor.execute('''
                UPDATE video_status
                SET quality_check_result = ?,
                    quality_score = ?,
                    quality_details = ?
                WHERE file_path = ?
            ''', (quality_result, quality_score, quality_details, file_path))
            conn.commit()
            print(f"Updated existing record for {file_path}")
        except Exception as e2:
            print(f"Error in fallback update: {e2}")
    except Exception as e:
        print(f"Error updating quality status in database: {e}")
    finally:
        conn.close()


def deduplicate_database():
    conn = sqlite3.connect('video_status.db')
    cursor = conn.cursor()

    # Merge duplicates by updating the most recent entry with non-null values from older entries
    cursor.execute('''
        WITH ranked_videos AS (
            SELECT *,
                   ROW_NUMBER() OVER (PARTITION BY file_path ORDER BY id DESC) as rn
            FROM video_status
        ),
        merged_videos AS (
            SELECT file_path,
                   MAX(arrival_time) as arrival_time,
                   MAX(metadata_present) as metadata_present,
                   MAX(quality_check_result) as quality_check_result,
                   MAX(quality_score) as quality_score,
                   MAX(quality_details) as quality_details,
                   MAX(processing_complete) as processing_complete,
                   MAX(annotation_complete) as annotation_complete,
                   MAX(annotation_email) as annotation_email
            FROM ranked_videos
            WHERE rn > 1
            GROUP BY file_path
        )
        UPDATE video_status
        SET arrival_time = COALESCE(merged_videos.arrival_time, video_status.arrival_time),
            metadata_present = COALESCE(merged_videos.metadata_present, video_status.metadata_present),
            quality_check_result = COALESCE(merged_videos.quality_check_result, video_status.quality_check_result),
            quality_score = COALESCE(merged_videos.quality_score, video_status.quality_score),
            quality_details = COALESCE(merged_videos.quality_details, video_status.quality_details),
            processing_complete = COALESCE(merged_videos.processing_complete, video_status.processing_complete),
            annotation_complete = COALESCE(merged_videos.annotation_complete, video_status.annotation_complete),
            annotation_email = COALESCE(merged_videos.annotation_email, video_status.annotation_email)
        FROM merged_videos
        WHERE video_status.file_path = merged_videos.file_path
          AND video_status.id = (SELECT MAX(id) FROM video_status WHERE file_path = merged_videos.file_path)
    ''')

    # Delete older duplicates
    cursor.execute('''
        DELETE FROM video_status
        WHERE id NOT IN (
            SELECT MAX(id)
            FROM video_status
            GROUP BY file_path
        )
    ''')

    conn.commit()
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
            score, issues = check_video_quality(file_path)
            log_quality_status(file_path, score, issues)
            deduplicate_database()
            print(f"Quality check complete - Score: {score}/10")
            if issues:
                print("Issues found:", ", ".join(issues))


if __name__ == "__main__":
    main()

