"""Tkinter GUI fragment for managing instructors.

This module defines :func:`build_instructor_tab`, which builds the
*Instructor* tab of the main application notebook. The tab includes entry
fields for name, age, email, and instructor ID, and a button to add a new
instructor to both memory and the SQLite database.

Docstrings follow Sphinx/Napoleon style.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import re
from src.core.models.instructor import Instructor

import src.core.db_manager as db

DB_PATH = "school.db"

# Precompiled regex for validating email addresses
email_format = re.compile(r"[^@]+@[^@]+\.[^@]+")


def build_instructor_tab(notebook, instructors: list, find_instructor_by_id, refresh_all_views):
    """Construct the *Instructor* tab in the Tkinter notebook.

    The tab allows users to add new instructors by specifying name, age,
    email, and instructor ID. When submitted, an :class:`Instructor`
    object is created, appended to the in-memory list, and inserted into
the database.

    :param notebook: The ttk Notebook widget where the tab will be added.
    :type notebook: ttk.Notebook
    :param instructors: The shared list of Instructor objects to append to.
    :type instructors: list[Instructor]
    :param find_instructor_by_id: Lookup helper for existing instructors.
    :type find_instructor_by_id: Callable[[str], Instructor | None]
    :param refresh_all_views: Callback to refresh all treeviews and combos.
    :type refresh_all_views: Callable[[], None]
    :return: The constructed ttk.Frame for the tab.
    :rtype: ttk.Frame
    """
    frame = ttk.Frame(notebook, padding=12)
    notebook.add(frame, text="Instructor")

    ttk.Label(frame, text="Name").grid(row=0, column=0, sticky="w")
    name_e = ttk.Entry(frame, width=28)
    name_e.grid(row=0, column=1, pady=4)

    ttk.Label(frame, text="Age").grid(row=1, column=0, sticky="w")
    age_e = ttk.Entry(frame, width=28)
    age_e.grid(row=1, column=1, pady=4)

    ttk.Label(frame, text="Email").grid(row=2, column=0, sticky="w")
    email_e = ttk.Entry(frame, width=28)
    email_e.grid(row=2, column=1, pady=4)

    ttk.Label(frame, text="Instructor ID").grid(row=3, column=0, sticky="w")
    iid_e = ttk.Entry(frame, width=28)
    iid_e.grid(row=3, column=1, pady=4)

    def add_instructor() -> None:
        """Callback to add a new instructor based on entry field values.

        - Validates that all fields are filled.
        - Ensures ``age`` is a non-negative integer.
        - Validates email format with a regex.
        - Prevents duplicate IDs using :func:`find_instructor_by_id`.
        - Appends a new Instructor object to ``instructors``.
        - Persists it via :func:`db.add_instructor`.
        - Clears the entry fields and refreshes views.

        :return: ``None``
        :rtype: None
        """
        name = name_e.get().strip()
        age = age_e.get().strip()
        email = email_e.get().strip()
        iid = iid_e.get().strip()

        if not name or not age or not email or not iid:
            messagebox.showerror("Error", "Fill all instructor fields.")
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
        if find_instructor_by_id(iid):
            messagebox.showerror("Error", "Instructor ID already exists.")
            return

        try:
            # 1) Persist to DB first
            db.add_instructor(DB_PATH, iid, name, int(age), email)

            # 2) Only if DB write succeeds, update in-memory + UI
            instructors.append(Instructor(name, int(age), email, iid))

            name_e.delete(0, tk.END)
            age_e.delete(0, tk.END)
            email_e.delete(0, tk.END)
            iid_e.delete(0, tk.END)

            refresh_all_views()

        except Exception as e:
            messagebox.showerror("DB Error", f"Could not add instructor:\n{e}")


    ttk.Button(frame, text="Add Instructor", command=add_instructor).grid(
        row=4, column=0, columnspan=2, pady=8
    )

    return frame
