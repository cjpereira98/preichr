#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk
import subprocess

class BigBrotherApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Big Brother")
        self.geometry("800x500")
        self.minsize(600, 350)

        self._build_ui()

    def _build_ui(self):
        # Sidebar frame
        sidebar = tk.Frame(self, bg="#1e1e1e", width=180)
        sidebar.pack(side="left", fill="y")

        # Main content frame
        self.content = tk.Frame(self, bg="#f4f4f4")
        self.content.pack(side="right", expand=True, fill="both")

        pages = {
            "Dashboard": self.show_dashboard,
            "Logs": self.show_logs,
            "Settings": self.show_settings,
            "About": self.show_about,
        }

        for name, handler in pages.items():
            btn = tk.Button(
                sidebar,
                text=name,
                fg="white",
                bg="#1e1e1e",
                activebackground="#333333",
                activeforeground="white",
                bd=0,
                pady=12,
                anchor="w",
                command=handler,
            )
            btn.pack(fill="x")

        self.show_dashboard()

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    # -------------------------
    # PAGES
    # -------------------------
    def show_dashboard(self):
        self.clear_content()
        tk.Label(self.content, text="👁️  Big Brother Dashboard", font=("Arial", 18), bg="#f4f4f4").pack(pady=20)
        tk.Label(self.content, text="System status will appear here.", bg="#f4f4f4").pack(pady=5)

        # NEW BUTTON (minimal change!)
        run_btn = tk.Button(
            self.content,
            text="Auto Run Bots",
            font=("Arial", 12),
            bg="#2b77e5",
            fg="white",
            activebackground="#1e5cb3",
            activeforeground="white",
            padx=16,
            pady=8,
            command=self.auto_run_bots   # placeholder function
        )
        run_btn.pack(pady=20)

    def show_logs(self):
        self.clear_content()
        tk.Label(self.content, text="📜 Logs", font=("Arial", 18), bg="#f4f4f4").pack(pady=20)
        log_box = tk.Text(self.content, height=15, width=80)
        log_box.pack(pady=10)
        log_box.insert("end", "[LOG] System initialized...\n")

    def show_settings(self):
        self.clear_content()
        tk.Label(self.content, text="⚙️ Settings", font=("Arial", 18), bg="#f4f4f4").pack(pady=20)
        tk.Label(self.content, text="(Here you’ll add config later)", bg="#f4f4f4").pack()

    def show_about(self):
        self.clear_content()
        tk.Label(self.content, text="ℹ️ About Big Brother", font=("Arial", 18), bg="#f4f4f4").pack(pady=20)
        tk.Label(self.content, text="Made with love. And surveillance.\n\n© Big Brother Inc.", bg="#f4f4f4").pack()

    # -------------------------
    # NEW CALLBACK
    # -------------------------
    def auto_run_bots(self):
        # Placeholder action
        print("Auto Run Bots triggered (placeholder).")
        # Later: call your script here
        subprocess.Popen(["python", "main.py"])

if __name__ == "__main__":
    app = BigBrotherApp()
    app.mainloop()
