import subprocess
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def run_consumers():
    scripts_dir = Path("scripts")
    consumers = [
        "quality_check.py",
        "metadata_check.py",
        "process_video.py"
    ]
    
    processes = []
    env = os.environ.copy()
    env["PYTHONPATH"] = project_root
    
    for consumer in consumers:
        script_path = scripts_dir / consumer
        process = subprocess.Popen([sys.executable, str(script_path)], env=env)
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