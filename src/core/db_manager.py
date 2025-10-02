"""
SQLite database utilities for the School Management System (Unified).

This module provides:
- Stateless API (requires db_path explicitly).
- Global convenience API using DB_PATH.
- High-level object reconstruction into Student/Instructor/Course objects.

Schema
------
- students(sid TEXT PK, name TEXT, age INTEGER, email TEXT)
- instructors(iid TEXT PK, name TEXT, age INTEGER, email TEXT)
- courses(cid TEXT PK, name TEXT, iid TEXT NULL REFERENCES instructors(iid))
- enrollments(cid TEXT, sid TEXT, PRIMARY KEY(cid, sid))
"""

import os
import sqlite3
import shutil
import datetime
from contextlib import contextmanager
from typing import Iterator, Optional, Tuple

# ---------------------------------------------------------------------
# Global DB path
# ---------------------------------------------------------------------
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "school.db"))
Row = Tuple

# ---------------------------------------------------------------------
# Connection helper
# ---------------------------------------------------------------------
@contextmanager
def get_conn(db_path: Optional[str] = None):
    """Context manager for SQLite connection with FK enabled."""
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

# ---------------------------------------------------------------------
# Setup & maintenance
# ---------------------------------------------------------------------
def init_db(db_path: str) -> bool:
    """Create the unified schema if not exists."""
    with get_conn(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS students (
                sid   TEXT PRIMARY KEY,
                name  TEXT NOT NULL,
                age   INTEGER NOT NULL CHECK(age >= 0),
                email TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS instructors (
                iid   TEXT PRIMARY KEY,
                name  TEXT NOT NULL,
                age   INTEGER NOT NULL CHECK(age >= 0),
                email TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS courses (
                cid  TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                iid  TEXT NULL REFERENCES instructors(iid) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS enrollments (
                cid TEXT NOT NULL REFERENCES courses(cid) ON DELETE CASCADE,
                sid TEXT NOT NULL REFERENCES students(sid) ON DELETE CASCADE,
                PRIMARY KEY (cid, sid)
            );
            """
        )
    return True

def backup_db(db_path: str, dest_path: str) -> None:
    """Copy database to another path."""
    src = sqlite3.connect(db_path)
    try:
        dst = sqlite3.connect(dest_path)
        with dst:
            src.backup(dst)
        dst.close()
    finally:
        src.close()

def backup_db_to_folder(dst_folder="backup") -> str:
    """Backup DB_PATH into a folder with timestamp."""
    os.makedirs(dst_folder, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    dst = os.path.join(dst_folder, f"school-{ts}.db")
    shutil.copyfile(DB_PATH, dst)
    return dst

# ---------------------------------------------------------------------
# Stateless Queries
# ---------------------------------------------------------------------
def list_students(db_path: str) -> Iterator[Tuple[str, str, int, str]]:
    """Yield (sid, name, age, email)."""
    with get_conn(db_path) as conn:
        cur = conn.execute("SELECT sid, name, age, email FROM students ORDER BY name ASC")
        yield from cur

def list_instructors(db_path: str) -> Iterator[Tuple[str, str, int, str]]:
    """Yield (iid, name, age, email)."""
    with get_conn(db_path) as conn:
        cur = conn.execute("SELECT iid, name, age, email FROM instructors ORDER BY name ASC")
        yield from cur

def list_courses(db_path: str) -> Iterator[Tuple[str, str, Optional[str], int]]:
    """Yield (cid, name, iid, enrolled_count)."""
    q = (
        "SELECT c.cid, c.name, c.iid, "
        "COALESCE((SELECT COUNT(*) FROM enrollments e WHERE e.cid=c.cid), 0) AS enrolled "
        "FROM courses c ORDER BY c.cid ASC"
    )
    with get_conn(db_path) as conn:
        cur = conn.execute(q)
        yield from cur

def list_course_roster(db_path: str, cid: str) -> Iterator[Tuple[str, str]]:
    """Yield (sid, name) for students in a course."""
    q = (
        "SELECT s.sid, s.name FROM enrollments e "
        "JOIN students s ON s.sid=e.sid "
        "WHERE e.cid=? ORDER BY s.name ASC"
    )
    with get_conn(db_path) as conn:
        cur = conn.execute(q, (cid,))
        yield from cur

def list_student_courses(db_path: str, sid: str) -> Iterator[Tuple[str, str]]:
    """Yield (cid, name) for courses a student is enrolled in."""
    q = (
        "SELECT c.cid, c.name FROM enrollments e "
        "JOIN courses c ON c.cid = e.cid "
        "WHERE e.sid = ? "
        "ORDER BY c.name ASC"
    )
    with get_conn(db_path) as conn:
        cur = conn.execute(q, (sid,))
        yield from cur

# ---------------------------------------------------------------------
# Stateless Mutations
# ---------------------------------------------------------------------
def add_student(db_path: str, sid: str, name: str, age: int, email: str) -> None:
    with get_conn(db_path) as conn:
        conn.execute("INSERT INTO students (sid, name, age, email) VALUES (?,?,?,?)", (sid, name, age, email))

def update_student(db_path: str, sid: str, name: str, age: int, email: str) -> None:
    with get_conn(db_path) as conn:
        conn.execute("UPDATE students SET name=?, age=?, email=? WHERE sid=?", (name, age, email, sid))

def delete_student(db_path: str, sid: str) -> None:
    with get_conn(db_path) as conn:
        conn.execute("DELETE FROM enrollments WHERE sid=?", (sid,))
        conn.execute("DELETE FROM students WHERE sid=?", (sid,))

def register_student(db_path: str, sid: str, cid: str) -> None:
    with get_conn(db_path) as conn:
        conn.execute("INSERT OR IGNORE INTO enrollments(cid, sid) VALUES (?,?)", (cid, sid))

def unregister_student(db_path: str, sid: str, cid: str) -> None:
    with get_conn(db_path) as conn:
        conn.execute("DELETE FROM enrollments WHERE sid=? AND cid=?", (sid, cid))

def add_instructor(db_path: str, iid: str, name: str, age: int, email: str) -> None:
    with get_conn(db_path) as conn:
        conn.execute("INSERT INTO instructors (iid, name, age, email) VALUES (?,?,?,?)", (iid, name, age, email))

def update_instructor(db_path: str, iid: str, name: str, age: int, email: str) -> None:
    with get_conn(db_path) as conn:
        conn.execute("UPDATE instructors SET name=?, age=?, email=? WHERE iid=?", (name, age, email, iid))

def delete_instructor(db_path: str, iid: str) -> None:
    with get_conn(db_path) as conn:
        conn.execute("UPDATE courses SET iid=NULL WHERE iid=?", (iid,))
        conn.execute("DELETE FROM instructors WHERE iid=?", (iid,))

def set_course_instructor(db_path: str, cid: str, iid: Optional[str]) -> None:
    with get_conn(db_path) as conn:
        conn.execute("UPDATE courses SET iid=? WHERE cid=?", (iid, cid))

def add_course(db_path: str, cid: str, name: str, iid: Optional[str] = None) -> None:
    with get_conn(db_path) as conn:
        conn.execute("INSERT INTO courses (cid, name, iid) VALUES (?,?,?)", (cid, name, iid))

def update_course_name(db_path: str, cid: str, new_name: str) -> None:
    with get_conn(db_path) as conn:
        conn.execute("UPDATE courses SET name=? WHERE cid=?", (new_name, cid))

def delete_course(db_path: str, cid: str) -> None:
    with get_conn(db_path) as conn:
        conn.execute("DELETE FROM enrollments WHERE cid=?", (cid,))
        conn.execute("DELETE FROM courses WHERE cid=?", (cid,))

# ---------------------------------------------------------------------
# Global convenience wrappers (DB_PATH)
# ---------------------------------------------------------------------
def create_tables() -> None:
    init_db(DB_PATH)

def get_all_students(): return list(list_students(DB_PATH))
def get_all_instructors(): return list(list_instructors(DB_PATH))
def get_all_courses(): return list(list_courses(DB_PATH))
def get_courses_of_student(student_id: str): return list(list_student_courses(DB_PATH, student_id))

# ---------------------------------------------------------------------
# High-level object reconstruction
# ---------------------------------------------------------------------
from src.core.models.student import Student
from src.core.models.instructor import Instructor
from src.core.models.course import Course

def load_all():
    """Load all objects into memory and wire relationships."""
    students, instructors, courses = [], [], []

    # instructors
    inst_map = {}
    for iid, name, age, email in get_all_instructors():
        ins = Instructor(name, int(age), email, iid)
        instructors.append(ins)
        inst_map[iid] = ins

    # courses
    course_map = {}
    for cid, cname, instr_id, _enrolled in get_all_courses():
        ins = inst_map.get(instr_id) if instr_id else None
        c = Course(cid, cname, ins)
        if ins:
            ins.assign_course(c)
        courses.append(c)
        course_map[cid] = c

    # students
    for sid, name, age, email in get_all_students():
        s = Student(name, int(age), email, sid)
        students.append(s)
        for cid, _ in get_courses_of_student(sid):
            course = course_map.get(cid)
            if course:
                s.register_course(course)
                course.add_student(s)

    return students, instructors, courses

def add_student_global(sid, name, age, email):
    add_student(DB_PATH, sid, name, age, email)

def update_student_global(sid, name, age, email):
    update_student(DB_PATH, sid, name, age, email)

def delete_student_global(sid):
    delete_student(DB_PATH, sid)

def add_instructor_global(iid, name, age, email):
    add_instructor(DB_PATH, iid, name, age, email)

def update_instructor_global(iid, name, age, email):
    update_instructor(DB_PATH, iid, name, age, email)

def delete_instructor_global(iid):
    delete_instructor(DB_PATH, iid)

def add_course_global(cid, name, iid=None):
    add_course(DB_PATH, cid, name, iid)

def set_course_instructor_global(cid, iid):
    set_course_instructor(DB_PATH, cid, iid)

def register_student_global(sid, cid):
    register_student(DB_PATH, sid, cid)

def unregister_student_global(sid, cid):
    unregister_student(DB_PATH, sid, cid)

def delete_course_global(cid):
    delete_course(DB_PATH, cid)

def backup_db_global(dest_path: str | None = None) -> str:
    if not dest_path:
        dest_path = os.path.abspath(f"school-backup.db")
    backup_db(DB_PATH, dest_path)
    return dest_path
