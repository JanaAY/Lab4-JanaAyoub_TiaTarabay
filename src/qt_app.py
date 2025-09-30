"""
School Management (PyQt5) application.

This module provides the PyQt5 GUI for managing students, instructors, and courses.
It exposes a :class:`MainWindow` with three tabs:
- Students: add/update/delete students and view their registered courses
- Instructors: add/update/delete instructors and view their assigned courses
- Courses: add/clear, assign instructor, and register students

It also includes utilities for saving/loading JSON snapshots and backing up the database.

The code is documented with Sphinx-style docstrings so it can be included in a full
project documentation site using Sphinx autodoc.

Usage (CLI):
    python qt_app.py

Typical build integration:
    - Keep application launch under ``if __name__ == "__main__":`` so Sphinx can import
      the module without executing the GUI.
"""

import sys, os, csv
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QMessageBox,
    QHBoxLayout, QVBoxLayout, QGridLayout, QGroupBox, QFileDialog, QTabWidget, QHeaderView
)
from PyQt5.QtGui import QIntValidator

from models.person import Person
from models.student import Student
from models.instructor import Instructor
from models.course import Course
from models.data_manager import DataManager
from models import db
from models.db_sync import load_all

#: Default JSON path for save/load operations
JSON_PATH = "school.json"

#: In-memory cache of students (populated by :meth:`MainWindow.reload_all`)
STUDENTS = []
#: In-memory cache of instructors (populated by :meth:`MainWindow.reload_all`)
INSTRUCTORS = []
#: In-memory cache of courses (populated by :meth:`MainWindow.reload_all`)
COURSES = []


def text(item):
    """
    Get the text of a :class:`QTableWidgetItem` safely.

    :param item: The table item (may be ``None``).
    :type item: QTableWidgetItem or None
    :return: The item's text, or an empty string if item is ``None``.
    :rtype: str
    """
    return item.text() if item else ""


class MainWindow(QMainWindow):
    """
    Main window for the School Management PyQt5 application.

    Provides tabs for Students, Instructors, and Courses; supports saving/loading
    data to/from JSON, and creating DB backups.

    :ivar tbl_students: Table showing student records with their registered courses
    :vartype tbl_students: QTableWidget
    :ivar tbl_instructors: Table showing instructor records with their assigned courses
    :vartype tbl_instructors: QTableWidget
    :ivar tbl_courses: Table showing course records with instructor and enrolled students
    :vartype tbl_courses: QTableWidget
    """

    def __init__(self):
        """
        Initialize the main window, construct tool buttons (Save/Load/Backup),
        set up the three tabs, and load all data from the database.

        :raises Exception: Propagates unexpected errors during widget construction
        """
        super().__init__()
        self.setWindowTitle("School Management")
        self.resize(900, 600)

        # top row (save / load / backup)
        top = QWidget()
        th = QHBoxLayout(top)
        btn_save = QPushButton("Save JSON"); btn_save.clicked.connect(self.save_json)
        btn_load = QPushButton("Load JSON"); btn_load.clicked.connect(self.load_json)
        btn_backup = QPushButton("Backup DB"); btn_backup.clicked.connect(self.backup_db)
        th.addWidget(btn_save); th.addWidget(btn_load); th.addWidget(btn_backup); th.addStretch(1)

        # tabs
        tabs = QTabWidget()
        tabs.addTab(self.make_students_tab(), "Students")
        tabs.addTab(self.make_instructors_tab(), "Instructors")
        tabs.addTab(self.make_courses_tab(), "Courses")

        # layout
        wrap = QWidget()
        v = QVBoxLayout(wrap)
        v.addWidget(top)
        v.addWidget(tabs)
        self.setCentralWidget(wrap)

        self.reload_all()

    # ----------------------------
    # Students
    # ----------------------------
    def make_students_tab(self):
        """
        Build and return the **Students** tab UI.

        Includes a form (ID, Name, Age, Email), Add/Update/Clear actions,
        and a table with Edit/Delete actions.

        :return: The tab widget for Students management.
        :rtype: QWidget
        """
        page = QWidget(); v = QVBoxLayout(page)

        box = QGroupBox("Student")
        g = QGridLayout(box)
        self.s_id = QLineEdit()
        self.s_name = QLineEdit()
        self.s_age = QLineEdit(); self.s_age.setValidator(QIntValidator(0, 200, self))
        self.s_email = QLineEdit()
        g.addWidget(QLabel("ID"), 0, 0);    g.addWidget(self.s_id, 0, 1)
        g.addWidget(QLabel("Name"), 1, 0);  g.addWidget(self.s_name, 1, 1)
        g.addWidget(QLabel("Age"), 2, 0);   g.addWidget(self.s_age, 2, 1)
        g.addWidget(QLabel("Email"), 3, 0); g.addWidget(self.s_email, 3, 1)
        b_add = QPushButton("Add");    b_add.clicked.connect(self.add_student)
        b_upd = QPushButton("Update"); b_upd.clicked.connect(self.update_student)
        b_clr = QPushButton("Clear");  b_clr.clicked.connect(self.clear_student_form)
        g.addWidget(b_add, 4, 0); g.addWidget(b_upd, 4, 1); g.addWidget(b_clr, 5, 0, 1, 2)

        self.tbl_students = QTableWidget(0, 5)
        self.tbl_students.setHorizontalHeaderLabels(["ID", "Name", "Age", "Email", "Courses"])
        self.tbl_students.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_students.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_students.setSelectionBehavior(QTableWidget.SelectRows)
        self.tbl_students.setSelectionMode(QTableWidget.SingleSelection)

        row = QWidget(); r = QHBoxLayout(row)
        b_edit = QPushButton("Edit");   b_edit.clicked.connect(lambda: self.fill_student_form_from_row())
        b_del  = QPushButton("Delete"); b_del.clicked.connect(lambda: self.delete_selected("student"))
        self.tbl_students.itemDoubleClicked.connect(lambda _: self.fill_student_form_from_row())
        r.addWidget(b_edit); r.addWidget(b_del)

        v.addWidget(box)
        v.addWidget(QLabel("Students"))
        v.addWidget(self.tbl_students)
        v.addWidget(row)
        return page

    def clear_student_form(self):
        """
        Clear all student form fields and focus the **ID** field.
        """
        self.s_id.clear(); self.s_name.clear(); self.s_age.clear(); self.s_email.clear()
        self.s_id.setFocus()

    def add_student(self):
        """
        Validate inputs and add a new student to the database.

        :raises ValueError: If ID missing, age negative, or email invalid.
        :side effects:
            - Calls :func:`models.db.add_student`
            - Refreshes UI via :meth:`reload_all`
            - Clears form via :meth:`clear_student_form`
        """
        sid = self.s_id.text().strip()
        name = self.s_name.text().strip()
        age = self.s_age.text().strip()
        email = self.s_email.text().strip()
        try:
            a = int(age)
            if a < 0: raise ValueError("Age must be non-negative")
            if not sid: raise ValueError("Student ID is required")
            if not Person._is_valid_email(email): raise ValueError("Invalid email")
            db.add_student(sid, name, a, email)
            self.reload_all()
            self.clear_student_form()
        except Exception as e:
            QMessageBox.critical(self, "Add student", str(e))

    def update_student(self):
        """
        Validate inputs and update an existing student in the database.

        :raises ValueError: If ID missing, age negative, or email invalid.
        :side effects:
            - Calls :func:`models.db.update_student`
            - Refreshes UI via :meth:`reload_all`
            - Clears form via :meth:`clear_student_form`
        """
        sid = self.s_id.text().strip()
        name = self.s_name.text().strip()
        age = self.s_age.text().strip()
        email = self.s_email.text().strip()
        try:
            a = int(age)
            if a < 0: raise ValueError("Age must be non-negative")
            if not sid: raise ValueError("Student ID is required")
            if not Person._is_valid_email(email): raise ValueError("Invalid email")
            db.update_student(sid, name, a, email)
            self.reload_all()
            self.clear_student_form()
        except Exception as e:
            QMessageBox.critical(self, "Update student", str(e))

    def fill_student_form_from_row(self):
        """
        Load the currently selected student row from the table into the form.

        No-op if no row is selected.
        """
        row = self.tbl_students.currentRow()
        if row < 0: return
        self.s_id.setText(text(self.tbl_students.item(row, 0)))
        self.s_name.setText(text(self.tbl_students.item(row, 1)))
        self.s_age.setText(text(self.tbl_students.item(row, 2)))
        self.s_email.setText(text(self.tbl_students.item(row, 3)))

    # ----------------------------
    # Instructors
    # ----------------------------
    def make_instructors_tab(self):
        """
        Build and return the **Instructors** tab UI.

        Includes a form (ID, Name, Age, Email), Add/Update/Clear actions,
        and a table with Edit/Delete actions.

        :return: The tab widget for Instructors management.
        :rtype: QWidget
        """
        page = QWidget(); v = QVBoxLayout(page)

        box = QGroupBox("Instructor")
        g = QGridLayout(box)
        self.i_id = QLineEdit()
        self.i_name = QLineEdit()
        self.i_age = QLineEdit(); self.i_age.setValidator(QIntValidator(0, 200, self))
        self.i_email = QLineEdit()
        g.addWidget(QLabel("ID"), 0, 0);    g.addWidget(self.i_id, 0, 1)
        g.addWidget(QLabel("Name"), 1, 0);  g.addWidget(self.i_name, 1, 1)
        g.addWidget(QLabel("Age"), 2, 0);   g.addWidget(self.i_age, 2, 1)
        g.addWidget(QLabel("Email"), 3, 0); g.addWidget(self.i_email, 3, 1)
        b_add = QPushButton("Add");    b_add.clicked.connect(self.add_instructor)
        b_upd = QPushButton("Update"); b_upd.clicked.connect(self.update_instructor)
        b_clr = QPushButton("Clear");  b_clr.clicked.connect(self.clear_instructor_form)
        g.addWidget(b_add, 4, 0); g.addWidget(b_upd, 4, 1); g.addWidget(b_clr, 5, 0, 1, 2)

        self.tbl_instructors = QTableWidget(0, 5)
        self.tbl_instructors.setHorizontalHeaderLabels(["ID", "Name", "Age", "Email", "Courses"])
        self.tbl_instructors.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_instructors.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_instructors.setSelectionBehavior(QTableWidget.SelectRows)
        self.tbl_instructors.setSelectionMode(QTableWidget.SingleSelection)

        row = QWidget(); r = QHBoxLayout(row)
        b_edit = QPushButton("Edit");   b_edit.clicked.connect(lambda: self.fill_instructor_form_from_row())
        b_del  = QPushButton("Delete"); b_del.clicked.connect(lambda: self.delete_selected("instructor"))
        self.tbl_instructors.itemDoubleClicked.connect(lambda _: self.fill_instructor_form_from_row())
        r.addWidget(b_edit); r.addWidget(b_del)

        v.addWidget(box)
        v.addWidget(QLabel("Instructors"))
        v.addWidget(self.tbl_instructors)
        v.addWidget(row)
        return page

    def clear_instructor_form(self):
        """
        Clear all instructor form fields and focus the **ID** field.
        """
        self.i_id.clear(); self.i_name.clear(); self.i_age.clear(); self.i_email.clear()
        self.i_id.setFocus()

    def add_instructor(self):
        """
        Validate inputs and add a new instructor to the database.

        :raises ValueError: If ID missing, age negative, or email invalid.
        :side effects:
            - Calls :func:`models.db.add_instructor`
            - Refreshes UI via :meth:`reload_all`
            - Clears form via :meth:`clear_instructor_form`
        """
        iid = self.i_id.text().strip()
        name = self.i_name.text().strip()
        age = self.i_age.text().strip()
        email = self.i_email.text().strip()
        try:
            a = int(age)
            if a < 0: raise ValueError("Age must be non-negative")
            if not iid: raise ValueError("Instructor ID is required")
            if not Person._is_valid_email(email): raise ValueError("Invalid email")
            db.add_instructor(iid, name, a, email)
            self.reload_all()
            self.clear_instructor_form()
        except Exception as e:
            QMessageBox.critical(self, "Add instructor", str(e))

    def update_instructor(self):
        """
        Validate inputs and update an existing instructor in the database.

        :raises ValueError: If ID missing, age negative, or email invalid.
        :side effects:
            - Calls :func:`models.db.update_instructor`
            - Refreshes UI via :meth:`reload_all`
            - Clears form via :meth:`clear_instructor_form`
        """
        iid = self.i_id.text().strip()
        name = self.i_name.text().strip()
        age = self.i_age.text().strip()
        email = self.i_email.text().strip()
        try:
            a = int(age)
            if a < 0: raise ValueError("Age must be non-negative")
            if not iid: raise ValueError("Instructor ID is required")
            if not Person._is_valid_email(email): raise ValueError("Invalid email")
            db.update_instructor(iid, name, a, email)
            self.reload_all()
            self.clear_instructor_form()
        except Exception as e:
            QMessageBox.critical(self, "Update instructor", str(e))

    def fill_instructor_form_from_row(self):
        """
        Load the currently selected instructor row from the table into the form.

        No-op if no row is selected.
        """
        row = self.tbl_instructors.currentRow()
        if row < 0: return
        self.i_id.setText(text(self.tbl_instructors.item(row, 0)))
        self.i_name.setText(text(self.tbl_instructors.item(row, 1)))
        self.i_age.setText(text(self.tbl_instructors.item(row, 2)))
        self.i_email.setText(text(self.tbl_instructors.item(row, 3)))

    # ----------------------------
    # Courses
    # ----------------------------
    def make_courses_tab(self):
        """
        Build and return the **Courses** tab UI.

        Includes:
            - Add Course (ID + Name)
            - Assign Instructor (by ID)
            - Register Student (by ID)
            - Courses table with Edit/Delete actions

        :return: The tab widget for Courses management.
        :rtype: QWidget
        """
        page = QWidget(); v = QVBoxLayout(page)

        # manage course (id + name only)
        box1 = QGroupBox("Add Course")
        g1 = QGridLayout(box1)
        self.c_id = QLineEdit()
        self.c_name = QLineEdit()
        g1.addWidget(QLabel("Course ID"), 0, 0);   g1.addWidget(self.c_id, 0, 1)
        g1.addWidget(QLabel("Course Name"), 1, 0); g1.addWidget(self.c_name, 1, 1)
        b_add = QPushButton("Add"); b_add.clicked.connect(self.add_course)
        b_clr = QPushButton("Clear"); b_clr.clicked.connect(self.clear_course_form)
        g1.addWidget(b_add, 2, 0); g1.addWidget(b_clr, 2, 1)

        # assign instructor by id
        box2 = QGroupBox("Assign Instructor")
        g2 = QGridLayout(box2)
        self.pick_course_assign = QComboBox()
        self.pick_instr_id = QComboBox()
        g2.addWidget(QLabel("Course"), 0, 0); g2.addWidget(self.pick_course_assign, 0, 1)
        g2.addWidget(QLabel("Instructor ID"), 1, 0); g2.addWidget(self.pick_instr_id, 1, 1)
        b_assign = QPushButton("Assign"); b_assign.clicked.connect(self.assign_instructor)
        g2.addWidget(b_assign, 2, 0, 1, 2)

        # register student by id
        box3 = QGroupBox("Register Student")
        g3 = QGridLayout(box3)
        self.pick_course_reg = QComboBox()
        self.pick_student_id = QComboBox()
        g3.addWidget(QLabel("Course"), 0, 0); g3.addWidget(self.pick_course_reg, 0, 1)
        g3.addWidget(QLabel("Student ID"), 1, 0); g3.addWidget(self.pick_student_id, 1, 1)
        b_reg = QPushButton("Register"); b_reg.clicked.connect(self.register_student)
        g3.addWidget(b_reg, 2, 0, 1, 2)

        self.tbl_courses = QTableWidget(0, 4)
        self.tbl_courses.setHorizontalHeaderLabels(["Course ID", "Course Name", "Instructor", "Students"])
        self.tbl_courses.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_courses.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_courses.setSelectionBehavior(QTableWidget.SelectRows)
        self.tbl_courses.setSelectionMode(QTableWidget.SingleSelection)

        row = QWidget(); r = QHBoxLayout(row)
        b_edit = QPushButton("Edit");   b_edit.clicked.connect(lambda: self.fill_course_form_from_row())
        b_del  = QPushButton("Delete"); b_del.clicked.connect(lambda: self.delete_selected("course"))
        self.tbl_courses.itemDoubleClicked.connect(lambda _: self.fill_course_form_from_row())
        r.addWidget(b_edit); r.addWidget(b_del)

        v.addWidget(box1)
        v.addWidget(box2)
        v.addWidget(box3)
        v.addWidget(QLabel("Courses"))
        v.addWidget(self.tbl_courses)
        v.addWidget(row)
        return page

    def clear_course_form(self):
        """
        Clear the course form fields and focus the **Course ID** field.
        """
        self.c_id.clear(); self.c_name.clear()
        self.c_id.setFocus()

    def add_course(self):
        """
        Add a new course to the database.

        :raises RuntimeError: Surfaces DB-layer errors (e.g., duplicates).
        :side effects:
            - Calls :func:`models.db.add_course`
            - Refreshes UI via :meth:`reload_all`
            - Clears form via :meth:`clear_course_form`
        """
        cid = self.c_id.text().strip()
        cname = self.c_name.text().strip()
        if not cid or not cname:
            QMessageBox.warning(self, "Add course", "Need course id and name")
            return
        try:
            db.add_course(cid, cname, None)
            self.reload_all()
            self.clear_course_form()
        except Exception as e:
            QMessageBox.critical(self, "Add course", str(e))

    def assign_instructor(self):
        """
        Assign the selected instructor to the selected course.

        :raises RuntimeError: Surfaces DB-layer errors.
        :side effects:
            - Calls :func:`models.db.assign_instructor`
            - Refreshes UI via :meth:`reload_all`
        """
        cid = self.pick_course_assign.currentText().strip()
        iid = self.pick_instr_id.currentText().strip()
        if not cid or not iid:
            QMessageBox.warning(self, "Assign", "Pick course and instructor")
            return
        try:
            db.assign_instructor(cid, iid)
            self.reload_all()
        except Exception as e:
            QMessageBox.critical(self, "Assign failed", str(e))

    def register_student(self):
        """
        Register the selected student to the selected course.

        :raises RuntimeError: Surfaces DB-layer errors.
        :side effects:
            - Calls :func:`models.db.register_student`
            - Refreshes UI via :meth:`reload_all`
        """
        cid = self.pick_course_reg.currentText().strip()
        sid = self.pick_student_id.currentText().strip()
        if not cid or not sid:
            QMessageBox.warning(self, "Register", "Pick course and student")
            return
        try:
            db.register_student(sid, cid)
            self.reload_all()
        except Exception as e:
            QMessageBox.critical(self, "Register failed", str(e))

    def fill_course_form_from_row(self):
        """
        Load the currently selected course row into the form fields and set the
        course pickers to that course.

        No-op if no row is selected.
        """
        row = self.tbl_courses.currentRow()
        if row < 0: return
        self.c_id.setText(text(self.tbl_courses.item(row, 0)))
        self.c_name.setText(text(self.tbl_courses.item(row, 1)))
        # also select the course in combos
        cid = text(self.tbl_courses.item(row, 0))
        self.pick_course_assign.setCurrentText(cid)
        self.pick_course_reg.setCurrentText(cid)

    # ----------------------------
    # Shared actions / data reload
    # ----------------------------
    def delete_selected(self, kind):
        """
        Delete the currently selected row of the given kind.

        :param kind: One of ``"student"``, ``"instructor"``, or ``"course"``.
        :type kind: str
        :side effects:
            - Calls the appropriate DB delete function
            - Refreshes UI via :meth:`reload_all`
        """
        table = self.tbl_students if kind == "student" else self.tbl_instructors if kind == "instructor" else self.tbl_courses
        row = table.currentRow()
        if row < 0: return
        key = text(table.item(row, 0))
        if not key: return
        if QMessageBox.question(self, "Confirm", f"Delete this {kind} ({key})?") != QMessageBox.Yes:
            return
        try:
            if kind == "student": db.delete_student(key)
            elif kind == "instructor": db.delete_instructor(key)
            else: db.delete_course(key)
            self.reload_all()
        except Exception as e:
            QMessageBox.critical(self, "Delete failed", str(e))

    def reload_all(self):
        """
        Reload in-memory lists from the database and refresh UI.

        :side effects:
            - Updates global ``STUDENTS``, ``INSTRUCTORS``, ``COURSES``
            - Calls :meth:`fill_tables` and :meth:`fill_pickers`
        """
        global STUDENTS, INSTRUCTORS, COURSES
        STUDENTS, INSTRUCTORS, COURSES = load_all()
        self.fill_tables()
        self.fill_pickers()

    def fill_tables(self):
        """
        Repopulate the three tables (students, instructors, courses) from the
        global in-memory caches.
        """
        # students
        self.tbl_students.setRowCount(0)
        for s in STUDENTS:
            r = self.tbl_students.rowCount(); self.tbl_students.insertRow(r)
            courses = ", ".join([c.course_id for c in s.registered_courses]) or "-"
            vals = [s.student_id, s.name, str(s.age), s._email, courses]
            for i, v in enumerate(vals):
                self.tbl_students.setItem(r, i, QTableWidgetItem(v))
        # instructors
        self.tbl_instructors.setRowCount(0)
        for i in INSTRUCTORS:
            r = self.tbl_instructors.rowCount(); self.tbl_instructors.insertRow(r)
            courses = ", ".join([c.course_id for c in i.assigned_courses]) or "-"
            vals = [i.instructor_id, i.name, str(i.age), i._email, courses]
            for j, v in enumerate(vals):
                self.tbl_instructors.setItem(r, j, QTableWidgetItem(v))
        # courses
        self.tbl_courses.setRowCount(0)
        for c in COURSES:
            r = self.tbl_courses.rowCount(); self.tbl_courses.insertRow(r)
            instr = c.instructor.instructor_id if c.instructor else "None"
            students = ", ".join([s.student_id for s in c.enrolled_students]) or "-"
            vals = [c.course_id, c.course_name, instr, students]
            for k, v in enumerate(vals):
                self.tbl_courses.setItem(r, k, QTableWidgetItem(v))

    def fill_pickers(self):
        """
        Repopulate combo boxes used for registrations and assignments so users
        can only pick valid IDs.
        """
        self.pick_student_id.clear()
        self.pick_instr_id.clear()
        self.pick_course_reg.clear()
        self.pick_course_assign.clear()
        self.pick_student_id.addItems([s.student_id for s in STUDENTS])
        self.pick_instr_id.addItems([i.instructor_id for i in INSTRUCTORS])
        ids = [c.course_id for c in COURSES]
        self.pick_course_reg.addItems(ids)
        self.pick_course_assign.addItems(ids)
        # start with nothing selected
        for cb in (self.pick_student_id, self.pick_instr_id, self.pick_course_reg, self.pick_course_assign):
            cb.setCurrentIndex(-1)

    # ----------------------------
    # Persistence & backup
    # ----------------------------
    def save_json(self):
        """
        Save the current in-memory data to a JSON file at :data:`JSON_PATH`.

        :side effects: Calls :func:`models.data_manager.DataManager.save_to_file`
            and shows a message box on success/failure.
        """
        try:
            DataManager.save_to_file(JSON_PATH, STUDENTS, INSTRUCTORS, COURSES)
            QMessageBox.information(self, "Save", "Saved.")
        except Exception as e:
            QMessageBox.critical(self, "Save failed", str(e))

    def load_json(self):
        """
        Load a JSON snapshot from :data:`JSON_PATH`, rebuild in-memory objects,
        overwrite the database accordingly, and refresh the UI.

        :side effects:
            - Calls :meth:`load_into_memory`
            - Calls :meth:`overwrite_db_from_memory`
            - Calls :meth:`reload_all`
        """
        try:
            data = DataManager.load_from_file(JSON_PATH)
            self.load_into_memory(data)
            self.overwrite_db_from_memory()
            self.reload_all()
            QMessageBox.information(self, "Load", "Loaded.")
        except Exception as e:
            QMessageBox.critical(self, "Load failed", str(e))

    def backup_db(self):
        """
        Create a database backup using :func:`models.db.backup_db` and display the path.
        """
        try:
            path = db.backup_db()
            QMessageBox.information(self, "Backup", f"Backed up to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Backup failed", str(e))

    # ----------------------------
    # JSON → Memory → DB helpers
    # ----------------------------
    def load_into_memory(self, data):
        """
        Convert a JSON-like structure into in-memory objects and link relationships.

        :param data: Parsed JSON dict containing ``students``, ``instructors``, ``courses``.
        :type data: dict
        :side effects:
            - Rebuilds global ``STUDENTS``, ``INSTRUCTORS``, ``COURSES`` lists
            - Recreates object relationships (assigned/registered entities)
        """
        global STUDENTS, INSTRUCTORS, COURSES
        STUDENTS.clear(); INSTRUCTORS.clear(); COURSES.clear()

        instr_by_id = {}
        for i in data.get("instructors", []):
            ins = Instructor(i["name"], int(i["age"]), i["email"], i["instructor_id"])
            INSTRUCTORS.append(ins)
            instr_by_id[ins.instructor_id] = ins

        course_by_id = {}
        for c in data.get("courses", []):
            instr = instr_by_id.get(c.get("instructor")) if c.get("instructor") else None
            course = Course(c["course_id"], c["course_name"], instr)
            COURSES.append(course)
            course_by_id[course.course_id] = course
            if instr: instr.assign_course(course)

        for s in data.get("students", []):
            st = Student(s["name"], int(s["age"]), s["email"], s["student_id"])
            STUDENTS.append(st)
            for cid in s.get("registered_courses", []):
                crs = course_by_id.get(cid)
                if crs:
                    st.register_course(crs)
                    crs.add_student(st)

    def overwrite_db_from_memory(self):
        """
        Rewrite the database from the current in-memory objects.

        Steps:
            1. Clear all DB tables.
            2. Insert instructors and their assigned courses.
            3. Insert courses and link their instructor IDs.
            4. Insert students and their registrations.

        :side effects: Mutates the DB and repopulates rows consistently with memory.
        """
        from models.db import get_conn
        with get_conn() as c:
            c.execute("DELETE FROM registrations;")
            c.execute("DELETE FROM courses;")
            c.execute("DELETE FROM students;")
            c.execute("DELETE FROM instructors;")
        for ins in INSTRUCTORS:
            db.add_instructor(ins.instructor_id, ins.name, int(ins.age), ins._email)
        for crs in COURSES:
            iid = crs.instructor.instructor_id if crs.instructor else None
            db.add_course(crs.course_id, crs.course_name, iid)
        for st in STUDENTS:
            db.add_student(st.student_id, st.name, int(st.age), st._email)
            for c in st.registered_courses:
                db.register_student(st.student_id, c.course_id)


def main():
    """
    Application entry point.

    Ensures DB tables exist, creates a :class:`MainWindow`, shows it, and
    starts the Qt event loop.

    :return: Process exit code from the Qt app exec loop.
    :rtype: int
    """
    db.create_tables()
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
