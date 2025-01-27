import tkinter as tk
from tkinter import messagebox
from watchdog.observers import Observer
import threading
import time
from utils import VideoHandler, WATCH_DIR

class FileMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Monitor")
        self.observer = None
        self.is_running = False

        # Load and display the logo
        self.logo = tk.PhotoImage(file="CHOP-Logo.png")
        self.logo_label = tk.Label(root, image=self.logo)
        self.logo_label.pack(pady=10)

        self.start_button = tk.Button(root, text="Start Monitoring", command=self.start_monitoring)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(root, text="Stop Monitoring", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        self.message_display = tk.Text(root, height=10, width=50)
        self.message_display.pack(pady=10)
        self.message_display.config(state=tk.DISABLED)

    def display_message(self, message):
        self.message_display.config(state=tk.NORMAL)
        self.message_display.insert(tk.END, message + "\n")
        self.message_display.config(state=tk.DISABLED)

    def start_monitoring(self):
        if not self.is_running:
            self.observer = Observer()
            self.observer.schedule(VideoHandler(self), WATCH_DIR, recursive=False)
            self.observer.start()
            self.is_running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            threading.Thread(target=self.run_observer).start()
            print("Monitoring started.")

    def stop_monitoring(self):
        if self.is_running:
            self.observer.stop()
            self.observer.join()
            self.is_running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            print("Monitoring stopped.")

    def run_observer(self):
        try:
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_monitoring() 