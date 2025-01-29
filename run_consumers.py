import subprocess
import sys
from pathlib import Path
def run_consumers():
    scripts_dir = Path("scripts")
    consumers = [
        "quality_check.py",
        "metadata_check.py",
        "process_video.py"
    ]
    
    processes = []
    for consumer in consumers:
        script_path = scripts_dir / consumer
        process = subprocess.Popen([sys.executable, str(script_path)])
        processes.append(process)
    
    try:
        # Keep the script running
        for process in processes:
            process.wait()
    except KeyboardInterrupt:
        # Handle graceful shutdown
        for process in processes:
            process.terminate()

if __name__ == "__main__":
    run_consumers() 