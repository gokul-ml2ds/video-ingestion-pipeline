## System Requirements

Before running the application, ensure the following are installed via Homebrew:

1. **FFmpeg**: Required for video processing.
   ```bash
   brew install ffmpeg
   ```

2. **Kafka**: If you want to run Kafka locally.
   ```bash
   brew install kafka
   ```

3. **Zookeeper**: Required by Kafka.
   ```bash
   brew install zookeeper
   ```

## Virtual Environment Setup

1. **Create a Virtual Environment**:
   Navigate to your project directory and create a virtual environment if it doesn't exist:
   ```bash
   python3 -m venv venv
   ```

2. **Activate the Virtual Environment**:
   Before running any scripts, activate the virtual environment:
   - On macOS and Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     .\venv\Scripts\activate
     ```

3. **Install Dependencies**:
   With the virtual environment activated, install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Docker Setup

1. **Install Docker Desktop**: Download and install Docker Desktop from [Docker's official website](https://www.docker.com/products/docker-desktop).

2. **Start Docker Desktop**: Open Docker Desktop and ensure it is running.

## Running the Application with Docker Compose

1. **Navigate to the project directory**:
   ```bash
   cd path/to/your/project
   ```

2. **Build and start the services**:
   ```bash
   docker-compose up --build
   ```

3. **Stop the services**:
   To stop the services, press `Ctrl+C` in the terminal where `docker-compose` is running, or run:
   ```bash
   docker-compose down
   ```

## Application Overview

This application monitors a specified directory for video files, processes them, and updates a database with the results.

### Directory Structure

- **Monitoring Directory**: The application monitors the `videos` folder for new video files.
- **Processed Videos**: Processed videos are saved in the `processed_videos` folder.
- **Logs**: Logs are displayed in the terminal.
- **Database**: Updates are made to the `video_status.db` database.

## Running the Application

After setting up Docker and starting the services, follow these steps to run the application:

1. **Run the Orchestrator**:
   Open a terminal and navigate to the project directory, then execute:
   ```bash
   python orchestrator.py
   ```

   This will launch the GUI for the File Monitoring App.

2. **Run the Consumers**:
   In a separate terminal, navigate to the project directory, then execute:
   ```bash
   python run_consumers.py
   ```

These scripts will start the file monitoring and processing components of your application.

### GUI Overview

<!-- add the ss of the gui here and center it -->

<img src="utils/SS.png" alt="GUI Screenshot" width="50%" style="display: block; margin: 0 auto;">

- **Start Monitoring**: Begins monitoring the `videos` directory for new files.
- **Stop Monitoring**: Stops the monitoring process.
- **Clear Log**: Clears the log display in the GUI.
- **Status Bar**: Displays the current status of the monitoring process.


