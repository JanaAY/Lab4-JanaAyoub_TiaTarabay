"""
Main entry point for the School Management System.

Asks the user to choose between Tkinter or PyQt interface and launches
the corresponding UI.
"""

import sys
import tkinter as tk
from tkinter import simpledialog, messagebox


def choose_ui():
    """Ask user which UI framework to run."""
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    choice = simpledialog.askstring(
        "Choose UI",
        "Enter 'tk' for Tkinter or 'qt' for PyQt:",
    )

    root.destroy()
    return choice.strip().lower() if choice else None


if __name__ == "__main__":
    ui_choice = choose_ui()

    if ui_choice == "tk":
        import src.ui_tk.main_tkinter
        src.ui_tk.main_tkinter.run()  # <-- define run() inside your main_tkinter.py
    elif ui_choice == "qt":
        import src.ui_qt.qt_app
        src.ui_qt.qt_app.run()  # <-- define run() inside your qt_app.py
    else:
        messagebox.showerror("Error", "Invalid choice. Please restart and enter 'tk' or 'qt'.")
        sys.exit(1)
