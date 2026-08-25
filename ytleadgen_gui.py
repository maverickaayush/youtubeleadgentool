#!/usr/bin/env python3
"""
YouTube LeadGen Tool - GUI Application
Modern Tkinter interface with persistent configuration
"""

import os
import sys
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path

from ytleadgen_core import run_leadgen_core


# Get application directory
if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(APP_DIR, "ytleadgen_config.json")


class YouTubeLeadGenGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube LeadGen Tool")
        self.root.geometry("900x750")
        
        # Variables
        self.api_key_var = tk.StringVar()
        self.api_key_visible = False
        self.keywords_var = tk.StringVar()
        self.min_subs_var = tk.StringVar(value="0")
        self.max_subs_var = tk.StringVar(value="1000000000")
        self.bio_key_var = tk.StringVar()
        self.country_var = tk.StringVar()
        self.require_email_var = tk.BooleanVar(value=False)
        self.test_mode_var = tk.BooleanVar(value=False)
        self.headless_var = tk.BooleanVar(value=True)
        self.out_dir_var = tk.StringVar(value=APP_DIR)
        
        # Load config
        self.load_config()
        
        # Build UI
        self.build_ui()
        
        # Worker thread tracking
        self.is_running = False
    
    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                
                self.api_key_var.set(config.get("api_key", ""))
                self.keywords_var.set(config.get("keywords", ""))
                self.min_subs_var.set(str(config.get("min_subs", 0)))
                self.max_subs_var.set(str(config.get("max_subs", 1000000000)))
                self.bio_key_var.set(config.get("bio_key", ""))
                self.country_var.set(config.get("country", ""))
                self.require_email_var.set(config.get("require_email", False))
                self.test_mode_var.set(config.get("test_mode", False))
                self.headless_var.set(config.get("headless", True))
                self.out_dir_var.set(config.get("out_dir", APP_DIR))
            except Exception as e:
                print(f"Error loading config: {e}")
    
    def save_config(self):
        """Save configuration to file"""
        config = {
            "api_key": self.api_key_var.get(),
            "keywords": self.keywords_var.get(),
            "min_subs": int(self.min_subs_var.get() or 0),
            "max_subs": int(self.max_subs_var.get() or 1000000000),
            "bio_key": self.bio_key_var.get(),
            "country": self.country_var.get(),
            "require_email": self.require_email_var.get(),
            "test_mode": self.test_mode_var.get(),
            "headless": self.headless_var.get(),
            "out_dir": self.out_dir_var.get()
        }
        
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {e}")
    
    def build_ui(self):
        """Build the GUI interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # ===== Input Form Section =====
        form_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        form_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        form_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # API Key
        ttk.Label(form_frame, text="API Key:").grid(row=row, column=0, sticky=tk.W, pady=5)
        api_key_frame = ttk.Frame(form_frame)
        api_key_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        api_key_frame.columnconfigure(0, weight=1)
        
        self.api_key_entry = ttk.Entry(api_key_frame, textvariable=self.api_key_var, show="*", width=50)
        self.api_key_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        self.show_api_button = ttk.Button(api_key_frame, text="Show", command=self.toggle_api_visibility, width=8)
        self.show_api_button.grid(row=0, column=1)
        
        ttk.Button(api_key_frame, text="Save", command=self.save_api_key, width=8).grid(row=0, column=2, padx=(5, 0))
        
        row += 1
        
        # Keywords
        ttk.Label(form_frame, text="Keywords:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(form_frame, textvariable=self.keywords_var, width=50).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(form_frame, text="(comma separated)", font=('TkDefaultFont', 8, 'italic')).grid(row=row, column=2, sticky=tk.W, padx=(5, 0))
        
        row += 1
        
        # Min/Max Subs
        subs_frame = ttk.Frame(form_frame)
        subs_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(form_frame, text="Subscribers:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Label(subs_frame, text="Min:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(subs_frame, textvariable=self.min_subs_var, width=15).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Label(subs_frame, text="Max:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(subs_frame, textvariable=self.max_subs_var, width=15).pack(side=tk.LEFT)
        
        row += 1
        
        # Bio Keyword
        ttk.Label(form_frame, text="Bio Keyword:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(form_frame, textvariable=self.bio_key_var, width=50).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(form_frame, text="(optional)", font=('TkDefaultFont', 8, 'italic')).grid(row=row, column=2, sticky=tk.W, padx=(5, 0))
        
        row += 1
        
        # Country
        ttk.Label(form_frame, text="Country:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(form_frame, textvariable=self.country_var, width=50).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(form_frame, text="(e.g., US, IN)", font=('TkDefaultFont', 8, 'italic')).grid(row=row, column=2, sticky=tk.W, padx=(5, 0))
        
        row += 1
        
        # Output Directory
        ttk.Label(form_frame, text="Output Folder:").grid(row=row, column=0, sticky=tk.W, pady=5)
        out_frame = ttk.Frame(form_frame)
        out_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        out_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(out_frame, textvariable=self.out_dir_var, width=40).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(out_frame, text="Browse", command=self.browse_output_dir).grid(row=0, column=1)
        
        row += 1
        
        # Checkboxes
        check_frame = ttk.Frame(form_frame)
        check_frame.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=10)
        
        ttk.Checkbutton(check_frame, text="Require Email", variable=self.require_email_var).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Checkbutton(check_frame, text="Test Mode (5 channels)", variable=self.test_mode_var).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Checkbutton(check_frame, text="Headless Browser", variable=self.headless_var).pack(side=tk.LEFT)
        
        # ===== Control Buttons =====
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        self.run_button = ttk.Button(button_frame, text="Run LeadGen", command=self.run_leadgen, width=20)
        self.run_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log, width=15).pack(side=tk.LEFT, padx=5)
        
        # ===== Progress Bar =====
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress = ttk.Progressbar(progress_frame, mode='determinate', length=400)
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.progress_label = ttk.Label(progress_frame, text="Ready")
        self.progress_label.grid(row=0, column=1, padx=(10, 0))
        
        # ===== Log Area =====
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(log_frame)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Text widget
        self.log_text = tk.Text(log_frame, height=20, width=80, yscrollcommand=scrollbar.set, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.config(command=self.log_text.yview)
    
    def toggle_api_visibility(self):
        """Toggle API key visibility"""
        self.api_key_visible = not self.api_key_visible
        if self.api_key_visible:
            self.api_key_entry.config(show="")
            self.show_api_button.config(text="Hide")
        else:
            self.api_key_entry.config(show="*")
            self.show_api_button.config(text="Show")
    
    def save_api_key(self):
        """Save only the API key"""
        if not self.api_key_var.get().strip():
            messagebox.showwarning("Warning", "API key is empty")
            return
        
        self.save_config()
        messagebox.showinfo("Success", "API key saved successfully")
    
    def browse_output_dir(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(initialdir=self.out_dir_var.get())
        if directory:
            self.out_dir_var.set(directory)
    
    def clear_log(self):
        """Clear the log text area"""
        self.log_text.delete(1.0, tk.END)
    
    def append_log(self, line: str):
        """Append a line to the log (thread-safe)"""
        self.root.after(0, self._append_log_main, line)
    
    def _append_log_main(self, line: str):
        """Append log line in main thread"""
        self.log_text.insert("end", line + "\n")
        self.log_text.see("end")
    
    def update_progress(self, current: int, total: int):
        """Update progress bar (thread-safe)"""
        self.root.after(0, self._update_progress_main, current, total)
    
    def _update_progress_main(self, current: int, total: int):
        """Update progress in main thread"""
        if total > 0:
            value = int(current * 100 / total)
            self.progress["value"] = value
            self.progress_label.config(text=f"{current}/{total}")
        self.root.update_idletasks()
    
    def validate_inputs(self) -> bool:
        """Validate form inputs"""
        if not self.api_key_var.get().strip():
            messagebox.showerror("Error", "API key is required")
            return False
        
        if not self.keywords_var.get().strip():
            messagebox.showerror("Error", "Keywords are required")
            return False
        
        try:
            min_subs = int(self.min_subs_var.get())
            max_subs = int(self.max_subs_var.get())
            
            if min_subs < 0 or max_subs < 0:
                messagebox.showerror("Error", "Subscriber counts must be positive")
                return False
            
            if min_subs > max_subs:
                messagebox.showerror("Error", "Min subscribers cannot be greater than max subscribers")
                return False
        except ValueError:
            messagebox.showerror("Error", "Subscriber counts must be valid integers")
            return False
        
        return True
    
    def run_leadgen(self):
        """Start the lead generation process"""
        if self.is_running:
            messagebox.showwarning("Warning", "LeadGen is already running")
            return
        
        if not self.validate_inputs():
            return
        
        # Save config before running
        self.save_config()
        
        # Prepare arguments
        out_file = os.path.join(self.out_dir_var.get(), "youtube_results.csv")
        if self.test_mode_var.get():
            out_file = os.path.join(self.out_dir_var.get(), "test_results.csv")
        
        args = {
            "api_key": self.api_key_var.get().strip(),
            "keywords": self.keywords_var.get().strip(),
            "min_subs": int(self.min_subs_var.get()),
            "max_subs": int(self.max_subs_var.get()),
            "bio_key": self.bio_key_var.get().strip() or None,
            "country": self.country_var.get().strip() or None,
            "require_email": self.require_email_var.get(),
            "out_file": out_file,
            "test_mode": self.test_mode_var.get(),
            "headless": self.headless_var.get(),
            "gui_log_func": self.append_log,
            "gui_progress_func": self.update_progress
        }
        
        # Disable button
        self.run_button.config(state="disabled")
        self.is_running = True
        
        # Clear log and reset progress
        self.clear_log()
        self.progress["value"] = 0
        self.progress_label.config(text="Starting...")
        
        # Start worker thread
        thread = threading.Thread(target=self._run_worker, args=(args,), daemon=True)
        thread.start()
    
    def _run_worker(self, args):
        """Worker thread for running lead generation"""
        try:
            saved_count = run_leadgen_core(**args)
            self.append_log(f"\n{'='*50}")
            self.append_log(f"COMPLETED: {saved_count} channels saved")
            self.append_log(f"Output file: {args['out_file']}")
            messagebox.showinfo("Success", f"Lead generation completed!\n{saved_count} channels saved to:\n{args['out_file']}")
        except Exception as e:
            self.append_log(f"\nERROR: {str(e)}")
            messagebox.showerror("Error", f"Lead generation failed:\n{str(e)}")
        finally:
            # Re-enable button
            self.root.after(0, self._finish_run)
    
    def _finish_run(self):
        """Clean up after worker finishes"""
        self.run_button.config(state="normal")
        self.is_running = False
        self.progress_label.config(text="Finished")


def main():
    root = tk.Tk()
    app = YouTubeLeadGenGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
