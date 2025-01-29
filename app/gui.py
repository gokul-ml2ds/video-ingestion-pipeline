import tkinter as tk
from tkinter import ttk, messagebox, Menu
from watchdog.observers import Observer
import threading
import time
from file_monitor import WATCH_DIR
from file_monitor import VideoHandler


class FileMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Monitor")

        # Set the window size to a specific width and height
        window_width = 430  # Adjust width as needed
        window_height = 500  # Adjust height as needed
        self.root.geometry(f"{window_width}x{window_height}")

        # Bind the resize event
        self.root.bind("<Configure>", self.on_resize)

        # Configure a style for ttk widgets
        self.style = ttk.Style()
        self.style.theme_use("clam")  # Try 'clam', 'default', 'alt', or others
        self.style.configure("Main.TFrame", background="#ffffff")  # Main background color
        self.style.configure("Header.TLabel", font=("Helvetica", 16, "bold"), background="#ffffff")
        self.style.configure("Status.TLabel", background="#f0f0f0", relief="sunken", font=("Helvetica", 10), padding=(5, 5))

        # Menu Bar
        self._create_menu_bar()

        # Main Frame
        self.main_frame = ttk.Frame(self.root, style="Main.TFrame", padding="10 10 10 10")
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        # Make the main frame expandable
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Logo
        self.logo_frame = ttk.Frame(self.main_frame, style="Main.TFrame")
        self.logo_frame.grid(row=0, column=0, pady=10, columnspan=2, sticky="ew")

        self.logo = tk.PhotoImage(file="utils/CHOP-Logo.png")
        self.logo = self.logo.subsample(2, 2)  # Reduce size by half
        self.logo_label = ttk.Label(self.logo_frame, image=self.logo, background="#ffffff")
        self.logo_label.pack()

        # Header Label
        self.header_label = ttk.Label(
            self.main_frame, text="File Monitoring App", style="Header.TLabel"
        )
        self.header_label.grid(row=1, column=0, columnspan=2, pady=(10, 20), sticky="ew")

        # Buttons Frame
        self.buttons_frame = ttk.Frame(self.main_frame, style="Main.TFrame")
        self.buttons_frame.grid(row=2, column=0, columnspan=2, pady=(0, 10), sticky="ew")

        self.start_button = ttk.Button(
            self.buttons_frame, text="Start Monitoring", command=self.start_monitoring
        )
        self.start_button.grid(row=0, column=0, padx=10)

        self.stop_button = ttk.Button(
            self.buttons_frame, text="Stop Monitoring", command=self.stop_monitoring, state=tk.DISABLED
        )
        self.stop_button.grid(row=0, column=1, padx=10)

        self.clear_button = ttk.Button(
            self.buttons_frame, text="Clear Log", command=self.clear_log
        )
        self.clear_button.grid(row=0, column=2, padx=10)

        # Message Display
        self.message_display = tk.Text(
            self.main_frame, height=15, width=int(self.root.winfo_screenwidth() * 0.8 / 10), font=("Helvetica", 10), wrap="word"
        )
        self.message_display.grid(row=3, column=0, columnspan=2, pady=10, sticky="nsew")
        self.message_display.config(state=tk.DISABLED)

        # Make the text widget expandable
        self.main_frame.rowconfigure(3, weight=1)

        # Status Bar
        self.status_bar = ttk.Label(
            self.root, text="Not Monitoring", style="Status.TLabel", anchor="w"
        )
        self.status_bar.grid(row=4, column=0, columnspan=2, sticky="ew")

        self.observer = None
        self.is_running = False

    def _create_menu_bar(self):
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = Menu(menubar, tearoff=False)
        file_menu.add_command(label="Exit", command=self.exit_app)
        menubar.add_cascade(label="File", menu=file_menu)

        help_menu = Menu(menubar, tearoff=False)
        help_menu.add_command(label="About", command=self.show_about_dialog)
        menubar.add_cascade(label="Help", menu=help_menu)

    def start_monitoring(self):
        if not self.is_running:
            self.observer = Observer()
            self.observer.schedule(VideoHandler(self), WATCH_DIR, recursive=False)
            self.observer.start()
            self.is_running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_bar.config(text="Monitoring...", foreground="green")
            threading.Thread(target=self.run_observer, daemon=True).start()
            self.display_message("Monitoring started.")
            print("Monitoring started.")

    def stop_monitoring(self):
        if self.is_running:
            self.observer.stop()
            self.observer.join()
            self.is_running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.status_bar.config(text="Not Monitoring", foreground="red")
            self.display_message("Monitoring stopped.")
            print("Monitoring stopped.")

    def clear_log(self):
        self.message_display.config(state=tk.NORMAL)
        self.message_display.delete("1.0", tk.END)
        self.message_display.config(state=tk.DISABLED)

    def display_message(self, message):
        self.message_display.config(state=tk.NORMAL)
        self.message_display.insert(tk.END, message + "\n")
        self.message_display.see(tk.END)
        self.message_display.config(state=tk.DISABLED)

    def run_observer(self):
        try:
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_monitoring()

    def exit_app(self):
        """Cleanly stop the observer if running, then exit."""
        if self.is_running:
            self.stop_monitoring()
        self.root.quit()

    def show_about_dialog(self):
        messagebox.showinfo(
            "About",
            "File Monitoring App\n\nThis application monitors a directory for file changes "
            "using Watchdog.\n\n© 2025 Your Organization"
        )

    def on_resize(self, event):
        # Adjust the width of the text widget based on the new window size
        new_width = int(self.root.winfo_width() * 0.8 / 10)
        self.message_display.config(width=new_width)


if __name__ == "__main__":
    root = tk.Tk()
    app = FileMonitorApp(root)
    root.mainloop()
