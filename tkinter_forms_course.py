"""Tkinter GUI fragment for managing courses.

This module defines a helper function :func:`build_course_tab` that
constructs the *Course* tab of the main application notebook. It
includes entry widgets for course ID and course name, and a button to
add a new course to both memory and the SQLite database.

Docstrings are written in Sphinx/Napoleon style.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from course import Course

import db_manager as db

DB_PATH = "school.db"


def build_course_tab(notebook, courses: list, refresh_all_views, find_course_by_id):
    """Construct the *Course* tab in the Tkinter notebook.

    The tab allows users to add new courses by specifying a course ID and
    name. When submitted, a :class:`Course` object is created, appended to
    the in-memory list, and inserted into the database.

    :param notebook: The ttk Notebook widget where the tab will be added.
    :type notebook: ttk.Notebook
    :param courses: The shared list of Course objects to append to.
    :type courses: list[Course]
    :param refresh_all_views: Callback to refresh all treeviews and combos.
    :type refresh_all_views: Callable[[], None]
    :param find_course_by_id: Lookup helper for existing courses.
    :type find_course_by_id: Callable[[str], Course | None]
    :return: The constructed ttk.Frame for the tab.
    :rtype: ttk.Frame
    """
    frame = ttk.Frame(notebook, padding=12)
    notebook.add(frame, text="Course")

    ttk.Label(frame, text="Course ID").grid(row=0, column=0, sticky="w")
    cid_e = ttk.Entry(frame, width=28)
    cid_e.grid(row=0, column=1, pady=4)

    ttk.Label(frame, text="Course Name").grid(row=1, column=0, sticky="w")
    cname_e = ttk.Entry(frame, width=28)
    cname_e.grid(row=1, column=1, pady=4)

    def add_course() -> None:
        """Callback to add a new course based on entry field values.

        - Validates non-empty ID and name.
        - Prevents duplicate IDs using :func:`find_course_by_id`.
        - Appends a new Course object to ``courses``.
        - Persists it via :func:`db.add_course`.
        - Clears the entry fields and refreshes views.

        :return: ``None``
        :rtype: None
        """
        cid = cid_e.get().strip()
        cname = cname_e.get().strip()
        if not cid or not cname:
            messagebox.showerror("Error", "Fill course ID and name.")
            return
        if find_course_by_id(cid):
            messagebox.showerror("Error", "Course ID already exists.")
            return
        try:
            # 1) Write to DB first (commits inside db.add_course)
            db.add_course(DB_PATH, cid, cname)

            # 2) Only if DB insert succeeds, update memory/UI
            courses.append(Course(cid, cname))
            cid_e.delete(0, tk.END)
            cname_e.delete(0, tk.END)
            refresh_all_views()

        except Exception as e:
            messagebox.showerror("DB Error", f"Could not add course:\n{e}")


    ttk.Button(frame, text="Add Course", command=add_course).grid(row=2, column=0, columnspan=2, pady=8)

    return frame
