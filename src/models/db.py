import os
import sqlite3
import shutil
import datetime
from contextlib import contextmanager

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "school.db"))

@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def create_tables():
    with get_conn() as c:
        c.execute("""
        CREATE TABLE IF NOT EXISTS students(
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL CHECK(age >= 0),
            email TEXT NOT NULL
        )""")
        c.execute("""
        CREATE TABLE IF NOT EXISTS instructors(
            instructor_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL CHECK(age >= 0),
            email TEXT NOT NULL
        )""")
        c.execute("""
        CREATE TABLE IF NOT EXISTS courses(
            course_id TEXT PRIMARY KEY,
            course_name TEXT NOT NULL,
            instructor_id TEXT,
            FOREIGN KEY(instructor_id) REFERENCES instructors(instructor_id) ON DELETE SET NULL
        )""")
        c.execute("""
        CREATE TABLE IF NOT EXISTS registrations(
            student_id TEXT NOT NULL,
            course_id TEXT NOT NULL,
            PRIMARY KEY(student_id, course_id),
            FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE CASCADE,
            FOREIGN KEY(course_id) REFERENCES courses(course_id) ON DELETE CASCADE
        )""")

def add_student(student_id, name, age, email):
    with get_conn() as c:
        c.execute("INSERT INTO students(student_id, name, age, email) VALUES (?,?,?,?)",
                  (student_id, name, age, email))

def update_student(student_id, name, age, email):
    with get_conn() as c:
        c.execute("UPDATE students SET name=?, age=?, email=? WHERE student_id=?",
                  (name, age, email, student_id))

def delete_student(student_id):
    with get_conn() as c:
        c.execute("DELETE FROM students WHERE student_id=?", (student_id,))

def get_all_students():
    with get_conn() as c:
        return c.execute(
            "SELECT student_id, name, age, email FROM students ORDER BY student_id"
        ).fetchall()

def add_instructor(instructor_id, name, age, email):
    with get_conn() as c:
        c.execute("INSERT INTO instructors(instructor_id, name, age, email) VALUES (?,?,?,?)",
                  (instructor_id, name, age, email))

def update_instructor(instructor_id, name, age, email):
    with get_conn() as c:
        c.execute("UPDATE instructors SET name=?, age=?, email=? WHERE instructor_id=?",
                  (name, age, email, instructor_id))

def delete_instructor(instructor_id):
    with get_conn() as c:
        c.execute("DELETE FROM instructors WHERE instructor_id=?", (instructor_id,))

def get_all_instructors():
    with get_conn() as c:
        return c.execute(
            "SELECT instructor_id, name, age, email FROM instructors ORDER BY instructor_id"
        ).fetchall()

def add_course(course_id, course_name, instructor_id):
    with get_conn() as c:
        c.execute("INSERT INTO courses(course_id, course_name, instructor_id) VALUES (?,?,?)",
                  (course_id, course_name, instructor_id))

def update_course(course_id, course_name, instructor_id):
    with get_conn() as c:
        c.execute("UPDATE courses SET course_name=?, instructor_id=? WHERE course_id=?",
                  (course_name, instructor_id, course_id))

def delete_course(course_id):
    with get_conn() as c:
        c.execute("DELETE FROM courses WHERE course_id=?", (course_id,))

def assign_instructor(course_id, instructor_id):
    with get_conn() as c:
        c.execute("UPDATE courses SET instructor_id=? WHERE course_id=?",
                  (instructor_id, course_id))

def get_all_courses():
    with get_conn() as c:
        return c.execute("""
            SELECT c.course_id, c.course_name, c.instructor_id, i.name AS instructor_name
            FROM courses c
            LEFT JOIN instructors i ON i.instructor_id = c.instructor_id
            ORDER BY c.course_id
        """).fetchall()

def register_student(student_id, course_id):
    with get_conn() as c:
        c.execute("INSERT OR IGNORE INTO registrations(student_id, course_id) VALUES (?,?)",
                  (student_id, course_id))

def unregister_student(student_id, course_id):
    with get_conn() as c:
        c.execute("DELETE FROM registrations WHERE student_id=? AND course_id=?",
                  (student_id, course_id))

def get_students_in_course(course_id):
    with get_conn() as c:
        return c.execute("""
            SELECT s.student_id, s.name
            FROM registrations r
            JOIN students s ON s.student_id = r.student_id
            WHERE r.course_id=?
            ORDER BY s.student_id
        """, (course_id,)).fetchall()

def get_courses_of_student(student_id):
    with get_conn() as c:
        return c.execute("""
            SELECT c.course_id, c.course_name
            FROM registrations r
            JOIN courses c ON c.course_id = r.course_id
            WHERE r.student_id=?
            ORDER BY c.course_id
        """, (student_id,)).fetchall()

def backup_db(dst_folder="backup"):
    os.makedirs(dst_folder, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    dst = os.path.join(dst_folder, f"school-{ts}.db")
    shutil.copyfile(DB_PATH, dst)
    return dst
