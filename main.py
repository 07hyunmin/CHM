import customtkinter as ctk
from tkinter import filedialog, messagebox
import logging
import threading
import os
from organizer_logic import FileOrganizer

# Custom Logging Handler to display logs in the UI
class TextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.configure(state="normal")
        
        # Color coding
        tag = "info"
        if record.levelno >= logging.ERROR:
            tag = "error"
        elif record.levelno >= logging.WARNING:
            tag = "warning"
            
        self.text_widget.insert("end", msg + "\n", tag)
        self.text_widget.see("end")
        self.text_widget.configure(state="disabled")

class FileOrganizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("Smart File Organizer")
        self.geometry("700x550")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Grid Configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # UI Components
        self.create_widgets()

        # Initialize Organizer and Logging
        self.organizer = FileOrganizer()
        self.setup_logging()

    def create_widgets(self):
        # Title
        self.title_label = ctk.CTkLabel(self, text="File Organizer ✨", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nw")

        # Path Selection Frame
        self.path_frame = ctk.CTkFrame(self)
        self.path_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.path_frame.grid_columnconfigure(0, weight=1)

        self.path_entry = ctk.CTkEntry(self.path_frame, placeholder_text="Select a folder to organize...")
        self.path_entry.grid(row=0, column=0, padx=(10, 0), pady=10, sticky="ew")

        self.browse_button = ctk.CTkButton(self.path_frame, text="Browse", width=100, command=self.browse_folder)
        self.browse_button.grid(row=0, column=1, padx=10, pady=10)

        # Log Window
        self.log_label = ctk.CTkLabel(self, text="Activity Logs", font=ctk.CTkFont(size=14, weight="bold"))
        self.log_label.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="nw")

        self.log_window = ctk.CTkTextbox(self, state="disabled", font=("Consolas", 12))
        self.log_window.grid(row=3, column=0, padx=20, pady=(5, 10), sticky="nsew")
        
        # Tag colors for logs
        self.log_window.tag_config("error", foreground="#FF6B6B")
        self.log_window.tag_config("info", foreground="#A0AEC0")
        self.log_window.tag_config("warning", foreground="#F6AD55")

        # Action Buttons
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="ew")

        self.organize_button = ctk.CTkButton(self.button_frame, text="Start Organizing", height=40, font=ctk.CTkFont(weight="bold"), command=self.start_organization)
        self.organize_button.pack(side="right", padx=0)

        self.clear_log_button = ctk.CTkButton(self.button_frame, text="Clear Logs", width=100, fg_color="#4A5568", hover_color="#2D3748", command=self.clear_logs)
        self.clear_log_button.pack(side="left")

    def setup_logging(self):
        self.logger = logging.getLogger("OrganizerUI")
        self.logger.setLevel(logging.INFO)
        
        handler = TextHandler(self.log_window)
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
        self.organizer.logger = self.logger

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, folder)
            self.logger.info(f"Target folder selected: {folder}")

    def clear_logs(self):
        self.log_window.configure(state="normal")
        self.log_window.delete("1.0", "end")
        self.log_window.configure(state="disabled")

    def start_organization(self):
        target = self.path_entry.get()
        if not target or not os.path.isdir(target):
            messagebox.showerror("Error", "Please select a valid folder first.")
            return

        self.organize_button.configure(state="disabled", text="Processing...")
        
        # Run in a separate thread to keep UI responsive
        thread = threading.Thread(target=self.run_logic, args=(target,))
        thread.daemon = True
        thread.start()

    def run_logic(self, target):
        try:
            self.organizer.organize(target)
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
        finally:
            self.organize_button.configure(state="normal", text="Start Organizing")
            messagebox.showinfo("Done", "Organization complete!")

if __name__ == "__main__":
    app = FileOrganizerApp()
    app.mainloop()
