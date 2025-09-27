"""SQLite database utilities for the School Management System.

This module provides a small functional API for creating and interacting
with the application's SQLite database. It is intentionally **stateless**:
all functions accept the database path explicitly.

Docstrings follow Sphinx/Napoleon style to integrate with autodoc/napoleon.

Schema (suggested)
------------------
- ``students(sid TEXT PRIMARY KEY, name TEXT, age INTEGER, email TEXT)``
- ``instructors(iid TEXT PRIMARY KEY, name TEXT, age INTEGER, email TEXT)``
- ``courses(cid TEXT PRIMARY KEY, name TEXT, iid TEXT NULL REFERENCES instructors(iid))``
- ``enrollments(cid TEXT REFERENCES courses(cid), sid TEXT REFERENCES students(sid),
                PRIMARY KEY(cid, sid))``
"""

from __future__ import annotations

import sqlite3
from typing import Iterable, Iterator, Optional, Tuple

Row = Tuple


# -----------------------------------------------------------
# Setup & maintenance
# -----------------------------------------------------------

def init_db(db_path: str) -> bool:
    """Create the database (tables) if they do not exist.

    :param db_path: Path to the SQLite database file.
    :type db_path: str
    :return: ``True`` if initialization succeeded.
    :rtype: bool
    """
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS students (
                sid   TEXT PRIMARY KEY,
                name  TEXT NOT NULL,
                age   INTEGER NOT NULL,
                email TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS instructors (
                iid   TEXT PRIMARY KEY,
                name  TEXT NOT NULL,
                age   INTEGER NOT NULL,
                email TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS courses (
                cid  TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                iid  TEXT NULL REFERENCES instructors(iid)
            );

            CREATE TABLE IF NOT EXISTS enrollments (
                cid TEXT NOT NULL REFERENCES courses(cid),
                sid TEXT NOT NULL REFERENCES students(sid),
                PRIMARY KEY (cid, sid)
            );
            """
        )
        conn.commit()
        return True
    finally:
        conn.close()


def backup_db(db_path: str, dest_path: str) -> None:
    """Copy the SQLite database to another path.

    :param db_path: Source database file.
    :type db_path: str
    :param dest_path: Destination file to create/overwrite.
    :type dest_path: str
    :return: ``None``
    :rtype: None
    """
    src = sqlite3.connect(db_path)
    try:
        dst = sqlite3.connect(dest_path)
        with dst:
            src.backup(dst)
        dst.close()
    finally:
        src.close()


# -----------------------------------------------------------
# Query helpers
# -----------------------------------------------------------

def list_students(db_path: str) -> Iterator[Tuple[str, str, int, str]]:
    """Yield all students as tuples ``(sid, name, age, email)``.

    :param db_path: Database path.
    :type db_path: str
    :return: Iterator of rows.
    :rtype: Iterator[tuple[str, str, int, str]]
    """
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        for row in cur.execute("SELECT sid, name, age, email FROM students ORDER BY name ASC"):
            yield row  # type: ignore[misc]
    finally:
        conn.close()


def list_instructors(db_path: str) -> Iterator[Tuple[str, str, int, str]]:
    """Yield all instructors as tuples ``(iid, name, age, email)``.

    :param db_path: Database path.
    :type db_path: str
    :return: Iterator of rows.
    :rtype: Iterator[tuple[str, str, int, str]]
    """
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        for row in cur.execute("SELECT iid, name, age, email FROM instructors ORDER BY name ASC"):
            yield row  # type: ignore[misc]
    finally:
        conn.close()


def list_courses(db_path: str) -> Iterator[Tuple[str, str, Optional[str], int]]:
    """Yield all courses with a precomputed enrolled count.

    Returns tuples ``(cid, name, iid, enrolled_count)``.

    :param db_path: Database path.
    :type db_path: str
    :return: Iterator of rows.
    :rtype: Iterator[tuple[str, str, str | None, int]]
    """
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        query = (
            "SELECT c.cid, c.name, c.iid,"
            "       COALESCE((SELECT COUNT(*) FROM enrollments e WHERE e.cid=c.cid), 0) AS enrolled "
            "FROM courses c ORDER BY c.cid ASC"
        )
        for row in cur.execute(query):
            yield row  # type: ignore[misc]
    finally:
        conn.close()


def list_course_roster(db_path: str, cid: str) -> Iterator[Tuple[str, str]]:
    """Yield the roster for a given course.

    Each returned row is ``(sid, name)``.

    :param db_path: Database path.
    :type db_path: str
    :param cid: Course identifier.
    :type cid: str
    :return: Iterator of rows in the course roster.
    :rtype: Iterator[tuple[str, str]]
    """
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        query = (
            "SELECT s.sid, s.name FROM enrollments e "
            "JOIN students s ON s.sid=e.sid WHERE e.cid=? ORDER BY s.name ASC"
        )
        for row in cur.execute(query, (cid,)):
            yield row  # type: ignore[misc]
    finally:
        conn.close()


# -----------------------------------------------------------
# Mutations: Students
# -----------------------------------------------------------

def update_student(db_path: str, sid: str, name: str, age: int, email: str) -> None:
    """Update a student's fields.

    :param db_path: Database path.
    :type db_path: str
    :param sid: Student ID to update.
    :type sid: str
    :param name: New name.
    :type name: str
    :param age: New age (>= 0).
    :type age: int
    :param email: New email.
    :type email: str
    :return: ``None``
    :rtype: None
    """
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("UPDATE students SET name=?, age=?, email=? WHERE sid=?", (name, age, email, sid))
        conn.commit()
    finally:
        conn.close()


def delete_student(db_path: str, sid: str) -> None:
    """Delete a student and remove their enrollments.

    :param db_path: Database path.
    :type db_path: str
    :param sid: Student ID to delete.
    :type sid: str
    :return: ``None``
    :rtype: None
    """
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM enrollments WHERE sid=?", (sid,))
        cur.execute("DELETE FROM students WHERE sid=?", (sid,))
        conn.commit()
    finally:
        conn.close()


def register_student(db_path: str, sid: str, cid: str) -> None:
    """Register a student in a course (idempotent).

    :param db_path: Database path.
    :type db_path: str
    :param sid: Student ID.
    :type sid: str
    :param cid: Course ID.
    :type cid: str
    :return: ``None``
    :rtype: None
    """
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO enrollments(cid, sid) VALUES(?, ?)", (cid, sid))
        conn.commit()
    finally:
        conn.close()


# -----------------------------------------------------------
# Mutations: Instructors
# -----------------------------------------------------------

def update_instructor(db_path: str, iid: str, name: str, age: int, email: str) -> None:
    """Update an instructor's fields.

    :param db_path: Database path.
    :type db_path: str
    :param iid: Instructor ID to update.
    :type iid: str
    :param name: New name.
    :type name: str
    :param age: New age (>= 0).
    :type age: int
    :param email: New email.
    :type email: str
    :return: ``None``
    :rtype: None
    """
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("UPDATE instructors SET name=?, age=?, email=? WHERE iid=?", (name, age, email, iid))
        conn.commit()
    finally:
        conn.close()


def delete_instructor(db_path: str, iid: str) -> None:
    """Delete an instructor and detach them from courses.

    Courses with this instructor will have their ``iid`` set to ``NULL``.

    :param db_path: Database path.
    :type db_path: str
    :param iid: Instructor ID to delete.
    :type iid: str
    :return: ``None``
    :rtype: None
    """
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("UPDATE courses SET iid=NULL WHERE iid=?", (iid,))
        cur.execute("DELETE FROM instructors WHERE iid=?", (iid,))
        conn.commit()
    finally:
        conn.close()


def set_course_instructor(db_path: str, cid: str, iid: Optional[str]) -> None:
    """Set or clear a course's instructor.

    :param db_path: Database path.
    :type db_path: str
    :param cid: Course ID.
    :type cid: str
    :param iid: Instructor ID to set, or ``None`` to clear.
    :type iid: str | None
    :return: ``None``
    :rtype: None
    """
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("UPDATE courses SET iid=? WHERE cid=?", (iid, cid))
        conn.commit()
    finally:
        conn.close()


# -----------------------------------------------------------
# Mutations: Courses
# -----------------------------------------------------------

def update_course_name(db_path: str, cid: str, new_name: str) -> None:
    """Rename a course.

    :param db_path: Database path.
    :type db_path: str
    :param cid: Course ID to rename.
    :type cid: str
    :param new_name: New course name.
    :type new_name: str
    :return: ``None``
    :rtype: None
    """
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("UPDATE courses SET name=? WHERE cid=?", (new_name, cid))
        conn.commit()
    finally:
        conn.close()


def delete_course(db_path: str, cid: str) -> None:
    """Delete a course and its enrollments.

    :param db_path: Database path.
    :type db_path: str
    :param cid: Course ID to delete.
    :type cid: str
    :return: ``None``
    :rtype: None
    """
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM enrollments WHERE cid=?", (cid,))
        cur.execute("DELETE FROM courses WHERE cid=?", (cid,))
        conn.commit()
    finally:
        conn.close()
