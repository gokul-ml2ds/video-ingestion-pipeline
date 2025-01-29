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

