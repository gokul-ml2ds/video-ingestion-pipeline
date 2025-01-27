import ffmpeg
import json
import os
from kafka import KafkaConsumer
import sqlite3

KAFKA_TOPIC = "video_files"
KAFKA_SERVER = 'localhost:9092'
PROCESSED_DIR = "processed_videos"

def process_video(input_file):
    try:
        # Ensure the processed_videos directory exists
        if not os.path.exists(PROCESSED_DIR):
            os.makedirs(PROCESSED_DIR)

        # Probe the video to get its dimensions
        probe = ffmpeg.probe(input_file)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        if not video_stream:
            raise ValueError("No video stream found")

        # Get input dimensions
        width = int(video_stream['width'])
        height = int(video_stream['height'])

        # Calculate target dimensions that are divisible by 2
        target_width = 720
        target_height = int((target_width / width) * height)
        # Ensure height is even
        target_height = target_height + (target_height % 2)

        # Define the output file name
        base_name = os.path.basename(input_file)
        name, ext = os.path.splitext(base_name)
        output_file = os.path.join(PROCESSED_DIR, f"{name}_processed{ext}")

        # Process the video with grayscale effect
        stream = (
            ffmpeg
            .input(input_file)
            .filter('scale', target_width, target_height)
            .filter('colorchannelmixer', 
                rr=0.3, rg=0.59, rb=0.11,
                gr=0.3, gg=0.59, gb=0.11,
                br=0.3, bg=0.59, bb=0.11)
            .output(output_file)
            .overwrite_output()
        )

        # Run FFmpeg command
        stream.run(capture_stdout=True, capture_stderr=True)
        return output_file

    except ffmpeg.Error as e:
        print(f"FFmpeg error occurred: {e.stderr.decode()}")
        raise
    except Exception as e:
        print(f"Error processing video: {str(e)}")
        raise

def log_processing_status(file_path, processing_complete):
    conn = sqlite3.connect('video_status.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE video_status
        SET processing_complete = ?
        WHERE file_path = ?
    ''', (processing_complete, file_path))
    conn.commit()
    conn.close()

def main():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_SERVER,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='video-processor-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    for message in consumer:
        file_path = message.value.get('file_path')
        if file_path:
            print(f"Processing file: {file_path}")
            try:
                processed_file = process_video(file_path)
                log_processing_status(file_path, True)
                print(f"Processed file created: {processed_file}")
            except Exception as e:
                log_processing_status(file_path, False)
                print(f"Error processing video: {e}")

if __name__ == "__main__":
    main()