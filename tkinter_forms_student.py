"""Tkinter GUI fragment for managing students.

This module defines :func:`build_student_tab`, which builds the *Student*
tab of the main application notebook. The tab includes entry fields for
name, age, email, and student ID, plus a button to add a new student to
both memory and the SQLite database.

Docstrings follow Sphinx/Napoleon style.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import re
from student import Student

import db_manager as db

DB_PATH = "school.db"

# Precompiled regex for validating email addresses
email_format = re.compile(r"[^@]+@[^@]+\.[^@]+")


def build_student_tab(notebook, students: list, find_student_by_id, refresh_all_views):
    """Construct the *Student* tab in the Tkinter notebook.

    The tab allows users to add new students by specifying name, age,
    email, and student ID. When submitted, a :class:`Student` object is
    created, appended to the in-memory list, and inserted into the
    database.

    :param notebook: The ttk Notebook widget where the tab will be added.
    :type notebook: ttk.Notebook
    :param students: The shared list of Student objects to append to.
    :type students: list[Student]
    :param find_student_by_id: Lookup helper for existing students.
    :type find_student_by_id: Callable[[str], Student | None]
    :param refresh_all_views: Callback to refresh all treeviews and combos.
    :type refresh_all_views: Callable[[], None]
    :return: The constructed ttk.Frame for the tab.
    :rtype: ttk.Frame
    """
    frame = ttk.Frame(notebook, padding=12)
    notebook.add(frame, text="Student")

    # Widgets
    ttk.Label(frame, text="Name").grid(row=0, column=0, sticky="w")
    name_e = ttk.Entry(frame, width=28)
    name_e.grid(row=0, column=1, pady=4)

    ttk.Label(frame, text="Age").grid(row=1, column=0, sticky="w")
    age_e = ttk.Entry(frame, width=28)
    age_e.grid(row=1, column=1, pady=4)

    ttk.Label(frame, text="Email").grid(row=2, column=0, sticky="w")
    email_e = ttk.Entry(frame, width=28)
    email_e.grid(row=2, column=1, pady=4)

    ttk.Label(frame, text="Student ID").grid(row=3, column=0, sticky="w")
    sid_e = ttk.Entry(frame, width=28)
    sid_e.grid(row=3, column=1, pady=4)

    def add_student() -> None:
        """Callback to add a new student based on entry field values.

        - Validates that all fields are filled.
        - Ensures ``age`` is a non-negative integer.
        - Validates email format with a regex.
        - Prevents duplicate IDs using :func:`find_student_by_id`.
        - Appends a new Student object to ``students``.
        - Persists it via :func:`db.add_student`.
        - Clears the entry fields and refreshes views.

        :return: ``None``
        :rtype: None
        """
        name = name_e.get().strip()
        age = age_e.get().strip()
        email = email_e.get().strip()
        sid = sid_e.get().strip()

        if not name or not age or not email or not sid:
            messagebox.showerror("Error", "Fill all student fields.")
            return
        try:
            if int(age) < 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "Age must be positive.")
            return
        if not email_format.match(email or ""):
            messagebox.showerror("Error", "Invalid email format.")
            return
        if find_student_by_id(sid):
            messagebox.showerror("Error", "Student ID already exists.")
            return

        try:
            # Write to DB first (commits inside db.add_student)
            db.add_student(DB_PATH, sid, name, int(age), email)

            # If DB insert succeeds, update in-memory + UI
            students.append(Student(name, int(age), email, sid))

            name_e.delete(0, tk.END)
            age_e.delete(0, tk.END)
            email_e.delete(0, tk.END)
            sid_e.delete(0, tk.END)

            refresh_all_views()

        except Exception as e:
            messagebox.showerror("DB Error", f"Could not add student:\n{e}")


    ttk.Button(frame, text="Add Student", command=add_student).grid(
        row=4, column=0, columnspan=2, pady=8
    )

    return frame