import sqlite3

def ensure_database():
    conn = sqlite3.connect('video_status.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS video_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT,
            arrival_time TEXT,
            metadata_present BOOLEAN,
            quality_check_result TEXT,
            quality_score INTEGER,
            quality_details TEXT,
            processing_complete BOOLEAN,
            annotation_complete BOOLEAN,
            annotation_email TEXT
        )
    ''')
    conn.commit()
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

