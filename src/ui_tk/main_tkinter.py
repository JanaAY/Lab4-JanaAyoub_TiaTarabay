"""School Management System (Tkinter + SQLite)

This module implements a simple school management system GUI built with
Tkinter/ttk. It manages three entities: **students**, **instructors**, and
**courses**, with persistence in an SQLite database and optional JSON import/
export for backups.

The code follows Sphinx-style docstrings (``:param``, ``:type``, ``:return:``,
``:rtype:``) to support automatic documentation generation with Sphinx
``autodoc`` and ``napoleon`` extensions.

Typical documentation workflow (see lab handout):

- Put your code docstrings in Sphinx/Napoleon style.
- Inside ``docs/`` run ``sphinx-quickstart`` and enable ``autodoc`` & ``napoleon``.
- From the project root: ``sphinx-apidoc -o docs .``
- Inside ``docs/`` run ``make html`` to generate HTML documentation.

Note:
    The GUI is created at module import and started via ``root.mainloop()`` at
    the end of the file. Database path is configurable via ``DB_PATH``.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json

from src.core.models.student import Student
from src.core.models.instructor import Instructor
from src.core.models.course import Course

from src.core.data_manager import DataManager

from src.ui_tk.tkinter_forms_student import build_student_tab
from src.ui_tk.tkinter_forms_instructor import build_instructor_tab
from src.ui_tk.tkinter_forms_course import build_course_tab

import src.core.db_manager as db

DB_PATH = "school.db"

# In-memory collections (kept in sync with DB)
students = []
instructors = []
courses = []


def find_student_by_id(sid):
    """Find a student in memory by ID.

    :param sid: Student unique identifier.
    :type sid: str
    :return: Matching ``Student`` instance if found, otherwise ``None``.
    :rtype: Student | None
    """
    for s in students:
        if s.student_id == sid:
            return s
    return None


def find_instructor_by_id(iid):
    """Find an instructor in memory by ID.

    :param iid: Instructor unique identifier.
    :type iid: str
    :return: Matching ``Instructor`` instance if found, otherwise ``None``.
    :rtype: Instructor | None
    """
    for i in instructors:
        if i.instructor_id == iid:
            return i
    return None


def find_course_by_id(cid):
    """Find a course in memory by ID.

    :param cid: Course unique identifier.
    :type cid: str
    :return: Matching ``Course`` instance if found, otherwise ``None``.
    :rtype: Course | None
    """
    for c in courses:
        if c.course_id == cid:
            return c
    return None


def load_all_from_db():
    """Load students, instructors, courses, and rosters from the database.

    This refreshes the in-memory lists (``students``, ``instructors``, ``courses``)
    by reading from the SQLite database, and wires their relationships
    (assigned courses, enrollments).

    :raises Exception: Propagates database exceptions from ``db_manager`` if any.
    :return: ``None``
    :rtype: None
    """
    students.clear(); instructors.clear(); courses.clear()

    # students
    for sid, name, age, email in db.list_students(DB_PATH):
        students.append(Student(name, int(age), email, sid))

    # instructors
    for iid, name, age, email in db.list_instructors(DB_PATH):
        instructors.append(Instructor(name, int(age), email, iid))

    # courses with instructor
    for cid, cname, iid, _enrolled in db.list_courses(DB_PATH):
        inst = next((x for x in instructors if x.instructor_id == iid), None) if iid else None
        c = Course(cid, cname, inst)
        courses.append(c)
        if inst and c not in inst.assigned_courses:
            inst.assigned_courses.append(c)

    # rosters
    for c in courses:
        for sid, _sname in db.list_course_roster(DB_PATH, c.course_id):
            s = next((x for x in students if x.student_id == sid), None)
            if s:
                if s not in c.enrolled_students:
                    c.enrolled_students.append(s)
                if c not in s.registered_courses:
                    s.registered_courses.append(c)


def register_student_to_course():
    """Register the selected student to the selected course (GUI action).

    Reads combobox selections, updates DB via ``db.register_student``, and
    mirrors changes in the in-memory objects.

    :raises ValueError: If the combobox selection format is invalid.
    :return: ``None``
    :rtype: None
    """
    stu_sel = reg_student_cb.get().strip()
    crs_sel = reg_course_cb.get().strip()
    if not stu_sel or not crs_sel:
        messagebox.showerror("Error", "Pick a student and a course.")
        return
    try:
        sid = stu_sel.split("|", 1)[1].strip()
        cid = crs_sel.split("|", 1)[1].strip()
    except Exception as _:
        messagebox.showerror("Error", "Invalid selection.")
        return
    s = find_student_by_id(sid)
    c = find_course_by_id(cid)
    if not s or not c:
        messagebox.showerror("Error", "Student or course not found.")
        return
    if c in s.registered_courses or s in c.enrolled_students:
        messagebox.showinfo("Already registered",
                            f"{s.name} is already registered in {c.course_name} (ID: {c.course_id}).")
        reg_student_cb.set("")
        reg_course_cb.set("")
        reg_student_cb.focus_set()
        return
    db.register_student(DB_PATH, s.student_id, c.course_id)
    if c not in s.registered_courses:
        s.registered_courses.append(c)
    if s not in c.enrolled_students:
        c.enrolled_students.append(s)
    messagebox.showinfo("OK", f"{s.name} registered in {c.course_name} (ID: {c.course_id}).")
    reg_student_cb.set("")
    reg_course_cb.set("")
    refresh_all_views()


def assign_instructor_to_course():
    """Assign the selected instructor to the selected course (GUI action).

    Updates DB via ``db.set_course_instructor`` and syncs in-memory links.

    :return: ``None``
    :rtype: None
    """
    ins_sel = asg_instructor_cb.get().strip()
    crs_sel = asg_course_cb.get().strip()
    if not ins_sel or not crs_sel:
        messagebox.showerror("Error", "Pick an instructor and a course.")
        return
    try:
        iid = ins_sel.split("|", 1)[1].strip()
        cid = crs_sel.split("|", 1)[1].strip()
    except Exception as _:
        messagebox.showerror("Error", "Invalid selection.")
        return
    inst = find_instructor_by_id(iid)
    c = find_course_by_id(cid)
    if not inst or not c:
        messagebox.showerror("Error", "Instructor or course not found.")
        return
    # --- Duplicate check ---
    if c.instructor is inst:
        messagebox.showinfo("Already assigned",
                            f"{inst.name} is already assigned to {c.course_name} (ID: {c.course_id}).")
        asg_instructor_cb.set("")
        asg_course_cb.set("")
        asg_instructor_cb.focus_set()
        return
    c.instructor = inst
    db.set_course_instructor(DB_PATH, c.course_id, inst.instructor_id)
    if c not in inst.assigned_courses:
        inst.assigned_courses.append(c)
    messagebox.showinfo("OK", f"{inst.name} assigned to {c.course_name} (ID: {c.course_id}).")
    # --- Clear comboboxes after success ---
    asg_instructor_cb.set("")
    asg_course_cb.set("")
    # (Optional) focus first field
    asg_instructor_cb.focus_set()
    refresh_all_views()

def show_all_and_clear_search():
    """Reset search box and repopulate all views."""
    search_var.set("")       # clear the entry box
    refresh_all_views()      # repopulate tables/combos


# --- Search & Filter ---

def do_search():
    """Filter treeviews by a free-text query from the search entry.

    The query is matched case-insensitively against the concatenated values of
    each row in the students, instructors, and courses tables.

    :return: ``None``
    :rtype: None
    """
    q = search_var.get().strip().lower()
    refresh_all_views()
    if not q:
        return

    # filter students
    for iid in students_tree.get_children():
        vals = students_tree.item(iid, "values")
        if q not in " ".join(map(str, vals)).lower():
            students_tree.detach(iid)

    # filter instructors
    for iid in instructors_tree.get_children():
        vals = instructors_tree.item(iid, "values")
        if q not in " ".join(map(str, vals)).lower():
            instructors_tree.detach(iid)

    # filter courses
    for iid in courses_tree.get_children():
        vals = courses_tree.item(iid, "values")
        if q not in " ".join(map(str, vals)).lower():
            courses_tree.detach(iid)


# --- Student CRUD ---

def delete_selected_student():
    """Delete the currently selected student from DB and UI.

    If the student is enrolled in any course, remove their references from
    in-memory collections and DB via ``db.delete_student``.

    :return: ``None``
    :rtype: None
    """
    sel = students_tree.selection()
    if not sel:
        messagebox.showerror("Error", "Select a student row.")
        return
    sid = students_tree.item(sel[0], "values")[1]
    s = find_student_by_id(sid)
    if not s:
        return

    try:
        db.delete_student(DB_PATH, s.student_id)
    except Exception as e:
        messagebox.showerror("DB Error", f"Could not delete student:\n{e}")
        return

    for c in courses:
        if s in c.enrolled_students:
            c.enrolled_students.remove(s)
    students.remove(s)
    refresh_all_views()


def edit_selected_student():
    """Edit fields of the currently selected student (interactive dialogs).

    Prompts for new name, age, and email, validates input, updates DB via
    ``db.update_student`` and mirrors values in memory.

    :return: ``None``
    :rtype: None
    """
    sel = students_tree.selection()
    if not sel:
        messagebox.showerror("Error", "Select a student row.")
        return

    sid = students_tree.item(sel[0], "values")[1]
    s = find_student_by_id(sid)
    if not s:
        return

    new_name = simpledialog.askstring("Edit Student", "New name:", initialvalue=s.name)
    if new_name is None:
        return
    new_name = new_name.strip()
    if not new_name:
        messagebox.showerror("Error", "Name cannot be empty.")
        return

    new_age = simpledialog.askinteger("Edit Student", "New age (>= 0):", initialvalue=s.age, minvalue=0)
    if new_age is None:
        return

    new_email = simpledialog.askstring("Edit Student", "New email:", initialvalue=s._email)
    if new_email is None:
        return
    new_email = new_email.strip()
    if "@" not in new_email or "." not in new_email.rsplit("@", 1)[-1]:
        messagebox.showerror("Error", "Invalid email.")
        return

    try:
        db.update_student(DB_PATH, s.student_id, new_name, int(new_age), new_email)
    except Exception as e:
        messagebox.showerror("DB Error", f"Could not update student:\n{e}")
        return

    s.name = new_name
    s.age = int(new_age)
    s._email = new_email

    refresh_all_views()


# --- Instructor CRUD ---

def delete_selected_instructor():
    """Delete the currently selected instructor from DB and UI.

    Also clears the ``instructor`` field of any courses they were assigned to,
    and persists that change in DB via ``db.set_course_instructor``.

    :return: ``None``
    :rtype: None
    """
    sel = instructors_tree.selection()
    if not sel:
        messagebox.showerror("Error", "Select an instructor row.")
        return
    iid = instructors_tree.item(sel[0], "values")[1]
    inst = find_instructor_by_id(iid)
    if not inst:
        return
    for c in courses:
        if c.instructor is inst:
            c.instructor = None
            db.set_course_instructor(DB_PATH, c.course_id, None)

    db.delete_instructor(DB_PATH, inst.instructor_id)
    instructors.remove(inst)
    refresh_all_views()


def edit_selected_instructor():
    """Edit fields of the currently selected instructor (interactive dialogs).

    Prompts for new name, age, and email, validates input, updates DB via
    ``db.update_instructor`` and mirrors values in memory.

    :return: ``None``
    :rtype: None
    """
    sel = instructors_tree.selection()
    if not sel:
        messagebox.showerror("Error", "Select an instructor row.")
        return

    iid = instructors_tree.item(sel[0], "values")[1]
    inst = find_instructor_by_id(iid)
    if not inst:
        return

    new_name = simpledialog.askstring("Edit Instructor", "New name:", initialvalue=inst.name)
    if new_name is None:
        return
    new_name = new_name.strip()
    if not new_name:
        messagebox.showerror("Error", "Name cannot be empty.")
        return

    new_age = simpledialog.askinteger("Edit Instructor", "New age (>= 0):", initialvalue=inst.age, minvalue=0)
    if new_age is None:
        return

    new_email = simpledialog.askstring("Edit Instructor", "New email:", initialvalue=inst._email)
    if new_email is None:
        return
    new_email = new_email.strip()
    if "@" not in new_email or "." not in new_email.rsplit("@", 1)[-1]:
        messagebox.showerror("Error", "Invalid email.")
        return

    try:
        db.update_instructor(DB_PATH, inst.instructor_id, new_name, int(new_age), new_email)
    except Exception as e:
        messagebox.showerror("DB Error", f"Could not update instructor:\n{e}")
        return

    inst.name = new_name
    inst.age = int(new_age)
    inst._email = new_email

    refresh_all_views()


# --- Course CRUD ---

def delete_selected_course():
    """Delete the currently selected course from DB and UI.

    Unlinks the course from registered students and from the assigned instructor,
    then removes the row from DB via ``db.delete_course``.

    :return: ``None``
    :rtype: None
    """
    sel = courses_tree.selection()
    if not sel:
        messagebox.showerror("Error", "Select a course row.")
        return
    cid = courses_tree.item(sel[0], "values")[0]
    c = find_course_by_id(cid)
    if not c:
        return
    db.delete_course(DB_PATH, c.course_id)
    for s in students:
        if c in s.registered_courses:
            s.registered_courses.remove(c)
    if c.instructor and c in c.instructor.assigned_courses:
        c.instructor.assigned_courses.remove(c)
    courses.remove(c)
    refresh_all_views()


def edit_selected_course():
    """Rename the currently selected course after validating input.

    Persists the new name via ``db.update_course_name`` and updates the
    in-memory ``Course`` object.

    :return: ``None``
    :rtype: None
    """
    sel = courses_tree.selection()
    if not sel:
        messagebox.showerror("Error", "Select a course row.")
        return

    cid = courses_tree.item(sel[0], "values")[0]
    c = find_course_by_id(cid)
    if not c:
        return

    new_name = simpledialog.askstring("Edit Course", "New course name:", initialvalue=c.course_name)
    if new_name is None:
        return
    new_name = new_name.strip()
    if not new_name:
        messagebox.showerror("Error", "Course name cannot be empty.")
        return

    try:
        db.update_course_name(DB_PATH, c.course_id, new_name)
    except Exception as e:
        messagebox.showerror("DB Error", f"Could not update course:\n{e}")
        return

    c.course_name = new_name
    refresh_all_views()


# --- JSON & DB Utilities ---

def save_json():
    """Serialize entities to a JSON file selected by the user.

    Uses ``DataManager.save_obj_into_json`` to dump ``students``, ``instructors``,
    and ``courses`` to disk for backup or transfer.

    :return: ``None``
    :rtype: None
    """
    fn = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
    if not fn:
        return
    DataManager.save_obj_into_json(fn, students, instructors, courses)
    messagebox.showinfo("Saved", f"Data saved to {fn}")


def load_json():
    """Load entities from a JSON file and refresh the UI.

    Replaces in-memory collections with the loaded ones and calls
    :func:`refresh_all_views`.

    :return: ``None``
    :rtype: None
    """
    fn = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
    if not fn:
        return
    loaded_students, loaded_instructors, loaded_courses = DataManager.load_obj_from_json(
        fn, Student, Instructor, Course
    )

    students.clear(); students.extend(loaded_students)
    instructors.clear(); instructors.extend(loaded_instructors)
    courses.clear(); courses.extend(loaded_courses)

    refresh_all_views()
    messagebox.showinfo("Loaded", f"Data loaded from {fn}")


def backup_db():
    """Create a copy of the SQLite database to a user-chosen path.

    :return: ``None``
    :rtype: None
    """
    fn = filedialog.asksaveasfilename(defaultextension=".db", filetypes=[("SQLite DB", "*.db")])
    if not fn:
        return
    db.backup_db(DB_PATH, fn)
    messagebox.showinfo("Backup", f"Database copied to {fn}")


# --- Refresh helpers ---

def refresh_students_tree():
    """Rebuild the students treeview from the ``students`` list.

    :return: ``None``
    :rtype: None
    """
    for i in students_tree.get_children():
        students_tree.delete(i)
    for s in students:
        course_list = ", ".join(c.course_id for c in s.registered_courses) or "-"
        students_tree.insert("", tk.END, values=(s.name, s.student_id, s.age, s._email, course_list))


def refresh_instructors_tree():
    """Rebuild the instructors treeview from the ``instructors`` list.

    :return: ``None``
    :rtype: None
    """
    for i in instructors_tree.get_children():
        instructors_tree.delete(i)
    for inst in instructors:
        course_list = ", ".join(c.course_id for c in inst.assigned_courses) or "-"
        instructors_tree.insert("", tk.END, values=(inst.name, inst.instructor_id, inst.age, inst._email, course_list))


def refresh_courses_tree():
    """Rebuild the courses treeview from the ``courses`` list.

    :return: ``None``
    :rtype: None
    """
    for i in courses_tree.get_children():
        courses_tree.delete(i)
    for c in courses:
        ins_name = c.instructor.name if c.instructor else "-"
        enrolled = len(c.enrolled_students)
        courses_tree.insert("", tk.END, values=(c.course_id, c.course_name, ins_name, enrolled))


def refresh_dropdowns():
    """Refresh combobox values for registration/assignment tabs.

    Keeps prior selections when still valid.

    :return: ``None``
    :rtype: None
    """
    stu_values = [f"{s.name} | {s.student_id}" for s in students]
    crs_values = [f"{c.course_name} | {c.course_id}" for c in courses]
    ins_values = [f"{i.name} | {i.instructor_id}" for i in instructors]

    def set_combo(combo, values):
        """Set a combobox's value list and try to preserve previous selection.

        :param combo: The ttk ``Combobox`` widget.
        :type combo: ttk.Combobox
        :param values: New values list to set on the combobox.
        :type values: list[str]
        :return: ``None``
        :rtype: None
        """
        old = combo.get()
        combo["values"] = values
        if old not in values:
            combo.set("")

    set_combo(reg_student_cb, stu_values)
    set_combo(reg_course_cb, crs_values)
    set_combo(asg_instructor_cb, ins_values)
    set_combo(asg_course_cb, crs_values)


def refresh_all_views():
    """Refresh all treeviews and comboboxes.

    :return: ``None``
    :rtype: None
    """
    refresh_students_tree()
    refresh_instructors_tree()
    refresh_courses_tree()
    refresh_dropdowns()


def build_ui(root: tk.Tk) -> None:
    """Create all Tkinter widgets and wire callbacks.

    :param root: The root Tk window.
    :type root: tk.Tk
    """
    global nb, reg_student_cb, reg_course_cb, asg_instructor_cb, asg_course_cb
    global students_tree, instructors_tree, courses_tree, search_var

    # Notebook
    nb = ttk.Notebook(root)
    nb.pack(fill="both", expand=True, padx=10, pady=10)

    # Tabs from modules
    build_student_tab(nb, students, find_student_by_id, refresh_all_views)
    build_instructor_tab(nb, instructors, find_instructor_by_id, refresh_all_views)
    build_course_tab(nb, courses, refresh_all_views, find_course_by_id)

    # Register Student tab
    reg_frame = ttk.Frame(nb, padding=12)
    nb.add(reg_frame, text="Register Student")
    ttk.Label(reg_frame, text="Student").grid(row=0, column=0, sticky="w")
    reg_student_cb = ttk.Combobox(reg_frame, width=40, state="readonly")
    reg_student_cb.grid(row=0, column=1, pady=4)
    ttk.Label(reg_frame, text="Course").grid(row=1, column=0, sticky="w")
    reg_course_cb = ttk.Combobox(reg_frame, width=40, state="readonly")
    reg_course_cb.grid(row=1, column=1, pady=4)
    ttk.Button(reg_frame, text="Register",
               command=register_student_to_course).grid(row=2, column=0, columnspan=2, pady=8)

    # Assign Instructor tab
    asg_frame = ttk.Frame(nb, padding=12)
    nb.add(asg_frame, text="Assign Instructor")
    ttk.Label(asg_frame, text="Instructor").grid(row=0, column=0, sticky="w")
    asg_instructor_cb = ttk.Combobox(asg_frame, width=40, state="readonly")
    asg_instructor_cb.grid(row=0, column=1, pady=4)
    ttk.Label(asg_frame, text="Course").grid(row=1, column=0, sticky="w")
    asg_course_cb = ttk.Combobox(asg_frame, width=40, state="readonly")
    asg_course_cb.grid(row=1, column=1, pady=4)
    ttk.Button(asg_frame, text="Assign",
               command=assign_instructor_to_course).grid(row=2, column=0, columnspan=2, pady=8)

    # Records tab
    records = ttk.Frame(nb, padding=12)
    nb.add(records, text="Records & Search")
    records.grid_columnconfigure(0, weight=1)
    records.grid_columnconfigure(1, weight=1)
    records.grid_columnconfigure(2, weight=1)
    records.grid_columnconfigure(3, weight=1)
    records.grid_rowconfigure(2, weight=1)
    records.grid_rowconfigure(5, weight=1)
    records.grid_rowconfigure(8, weight=1)

    ttk.Label(records, text="Search (name / id / course):").grid(row=0, column=0, sticky="w")
    search_var = tk.StringVar()
    ttk.Entry(records, textvariable=search_var, width=40).grid(row=0, column=1, sticky="w")
    ttk.Button(records, text="Search", command=do_search).grid(row=0, column=2, padx=6)
    ttk.Button(records, text="Show All", command=show_all_and_clear_search).grid(row=0, column=3)

    # Students tree
    ttk.Label(records, text="Students").grid(row=1, column=0, sticky="w", pady=(10, 2))
    students_tree = ttk.Treeview(
        records, columns=("name", "sid", "age", "email", "courses"),
        show="headings", height=7
    )
    for i, t in enumerate(("Name", "ID", "Age", "Email", "Courses")):
        students_tree.heading(students_tree["columns"][i], text=t)
    students_tree.grid(row=2, column=0, columnspan=4, sticky="nsew")
    stu_scroll = ttk.Scrollbar(records, orient="vertical", command=students_tree.yview)
    students_tree.configure(yscrollcommand=stu_scroll.set)
    stu_scroll.grid(row=2, column=4, sticky="ns")
    ttk.Button(records, text="Edit Selected Student",
               command=edit_selected_student).grid(row=3, column=0, pady=6, sticky="w")
    ttk.Button(records, text="Delete Selected Student",
               command=delete_selected_student).grid(row=3, column=1, pady=6, sticky="w")

    # Instructors tree
    ttk.Label(records, text="Instructors").grid(row=4, column=0, sticky="w", pady=(12, 2))
    instructors_tree = ttk.Treeview(
        records, columns=("name", "iid", "age", "email", "courses"),
        show="headings", height=7
    )
    for i, t in enumerate(("Name", "ID", "Age", "Email", "Courses")):
        instructors_tree.heading(instructors_tree["columns"][i], text=t)
    instructors_tree.grid(row=5, column=0, columnspan=4, sticky="nsew")
    ins_scroll = ttk.Scrollbar(records, orient="vertical", command=instructors_tree.yview)
    instructors_tree.configure(yscrollcommand=ins_scroll.set)
    ins_scroll.grid(row=5, column=4, sticky="ns")
    ttk.Button(records, text="Edit Selected Inst.",
               command=edit_selected_instructor).grid(row=6, column=0, pady=6, sticky="w")
    ttk.Button(records, text="Delete Selected Inst.",
               command=delete_selected_instructor).grid(row=6, column=1, pady=6, sticky="w")

    # Courses tree
    ttk.Label(records, text="Courses").grid(row=7, column=0, sticky="w", pady=(12, 2))
    courses_tree = ttk.Treeview(
        records, columns=("cid", "name", "instructor", "enrolled"),
        show="headings", height=7
    )
    for i, t in enumerate(("ID", "Course", "Instructor", "Enrolled#")):
        courses_tree.heading(courses_tree["columns"][i], text=t)
    courses_tree.grid(row=8, column=0, columnspan=4, sticky="nsew")
    crs_scroll = ttk.Scrollbar(records, orient="vertical", command=courses_tree.yview)
    courses_tree.configure(yscrollcommand=crs_scroll.set)
    crs_scroll.grid(row=8, column=4, sticky="ns")
    ttk.Button(records, text="Edit Selected Course",
               command=edit_selected_course).grid(row=9, column=0, pady=6, sticky="w")
    ttk.Button(records, text="Delete Selected Course",
               command=delete_selected_course).grid(row=9, column=1, pady=6, sticky="w")

    # Persistence buttons
    ttk.Button(records, text="Save to JSON", command=save_json).grid(row=10, column=0, pady=10, sticky="w")
    ttk.Button(records, text="Load from JSON", command=load_json).grid(row=10, column=1, pady=10, sticky="w")
    ttk.Button(records, text="Backup DB", command=backup_db).grid(row=10, column=2, pady=10, sticky="w")

    # Double-click bindings
    students_tree.bind("<Double-1>", on_student_double_click)
    instructors_tree.bind("<Double-1>", on_instructor_double_click)
    courses_tree.bind("<Double-1>", on_course_double_click)

# --- Double-click handlers ---

def on_student_double_click(event):
    """Show a messagebox with the selected student's registered courses.

    :param event: Tkinter event carrying the originating treeview widget.
    :type event: tkinter.Event
    :return: ``None``
    :rtype: None
    """
    tree = event.widget
    sel = tree.selection()
    if not sel:
        return
    vals = tree.item(sel[0], "values")
    sid = vals[1]
    s = find_student_by_id(sid)
    if not s:
        return
    courses_list = [f"{c.course_name} ({c.course_id})" for c in s.registered_courses]
    if not courses_list:
        messagebox.showinfo("Student Details", f"{s.name} ({s.student_id})\n\nNo registered courses yet.")
    else:
        messagebox.showinfo("Student Details", f"{s.name} ({s.student_id})\n\nRegistered courses:\n- " + "\n- ".join(courses_list))


def on_instructor_double_click(event):
    """Show a messagebox with the selected instructor's assigned courses.

    :param event: Tkinter event carrying the originating treeview widget.
    :type event: tkinter.Event
    :return: ``None``
    :rtype: None
    """
    tree = event.widget
    sel = tree.selection()
    if not sel:
        return
    vals = tree.item(sel[0], "values")
    iid = vals[1]
    inst = find_instructor_by_id(iid)
    if not inst:
        return
    courses_list = [f"{c.course_name} ({c.course_id})" for c in inst.assigned_courses]
    if not courses_list:
        messagebox.showinfo("Instructor Details", f"{inst.name} ({inst.instructor_id})\n\nNo assigned courses yet.")
    else:
        messagebox.showinfo("Instructor Details", f"{inst.name} ({inst.instructor_id})\n\nAssigned courses:\n- " + "\n- ".join(courses_list))


def on_course_double_click(event):
    """Show a messagebox with a course's roster and instructor.

    :param event: Tkinter event carrying the originating treeview widget.
    :type event: tkinter.Event
    :return: ``None``
    :rtype: None
    """
    tree = event.widget
    sel = tree.selection()
    if not sel:
        return
    vals = tree.item(sel[0], "values")
    cid = vals[0]
    c = find_course_by_id(cid)
    if not c:
        return
    roster = [f"{s.name} ({s.student_id})" for s in c.enrolled_students]
    inst_name = c.instructor.name if c.instructor else "—"
    if not roster:
        messagebox.showinfo("Course Details", f"{c.course_name} ({c.course_id})\nInstructor: {inst_name}\n\nNo students enrolled yet.")
    else:
        messagebox.showinfo("Course Details", f"{c.course_name} ({c.course_id})\nInstructor: {inst_name}\n\nEnrolled students:\n- " + "\n- ".join(roster))


def main() -> None:
    """Entry point to run the Tkinter application.

    Initializes the database, builds the UI, loads data, and starts the event loop.
    """
    db.init_db(DB_PATH)
    root = tk.Tk()
    root.state("zoomed")
    root.title("School Management System")

    build_ui(root)          # create widgets
    load_all_from_db()      # load data from DB
    refresh_all_views()     # paint tables/combos

    root.mainloop()

if __name__ == "__main__":
    main()

def run():
    main()