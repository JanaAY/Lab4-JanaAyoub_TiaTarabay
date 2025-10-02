"""Data serialization helpers for the School Management System.

This module exposes :class:`DataManager`, a small utility for exporting
and importing the in-memory *Student*, *Instructor*, and *Course* objects
as JSON files. Relationships (enrollments and instructor assignments) are
reconstructed on load.

Docstrings follow Sphinx/Napoleon style for clean API documentation.
"""

from __future__ import annotations

import json
from typing import Tuple, List, Type
from student import Student
from course import Course
from instructor import Instructor


class DataManager:
    """Save and load student, instructor, and course data to/from JSON.

    Methods
    -------
    save_obj_into_json(file_name, students, instructors, courses)
        Serialize entities and write them to a JSON file.
    load_obj_from_json(file_name, Student, Instructor, Course)
        Read a JSON file and rebuild entities and their relationships.
    """

    @staticmethod
    def save_obj_into_json(
        file_name: str,
        students: List["Student"],
        instructors: List["Instructor"],
        courses: List["Course"],
    ) -> None:
        """Save all data into a JSON file.

        :param file_name: Path where data will be saved.
        :type file_name: str
        :param students: List of ``Student`` objects to save.
        :type students: list[Student]
        :param instructors: List of ``Instructor`` objects to save.
        :type instructors: list[Instructor]
        :param courses: List of ``Course`` objects to save.
        :type courses: list[Course]
        :return: ``None``
        :rtype: None
        """
        data = {
            "students": [s.create_dict_from_obj() for s in students],
            "instructors": [i.create_dict_from_obj() for i in instructors],
            "courses": [c.create_dict_from_obj() for c in courses],
        }
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print("Data saved to", file_name)

    @staticmethod
    def load_obj_from_json(
        file_name: str,
        Student: Type["Student"],
        Instructor: Type["Instructor"],
        Course: Type["Course"],
    ) -> Tuple[List["Student"], List["Instructor"], List["Course"]]:
        """Load data from JSON and rebuild objects & relationships.

        Recreates instances using ``create_obj_from_dict`` on the provided
        classes, then restores links (course rosters and instructor
        assignments).

        :param file_name: Path to the JSON file to read.
        :type file_name: str
        :param Student: The ``Student`` class (factory for reconstruction).
        :type Student: type[Student]
        :param Instructor: The ``Instructor`` class (factory for reconstruction).
        :type Instructor: type[Instructor]
        :param Course: The ``Course`` class (factory for reconstruction).
        :type Course: type[Course]
        :return: Tuple of lists ``(students, instructors, courses)``.
        :rtype: tuple[list[Student], list[Instructor], list[Course]]
        """
        with open(file_name, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Step 1: Recreate objects from dictionaries
        students = [Student.create_obj_from_dict(d) for d in data.get("students", [])]
        instructors = [Instructor.create_obj_from_dict(d) for d in data.get("instructors", [])]
        courses = [Course.create_obj_from_dict(d) for d in data.get("courses", [])]

        # Step 2: Indexing by ID for quick lookup
        stu_by_id = {s.student_id: s for s in students}
        inst_by_id = {i.instructor_id: i for i in instructors}
        crs_by_id = {c.course_id: c for c in courses}

        # Step 3: Restore relationships on Course side
        for cd in data.get("courses", []):
            c = crs_by_id.get(cd["course_id"])
            if c is None:
                continue

            # Link instructor
            inst_id = cd.get("instructor")
            if inst_id:
                inst = inst_by_id.get(inst_id)
                if inst:
                    c.instructor = inst
                    if c not in inst.assigned_courses:
                        inst.assigned_courses.append(c)

            # Link students (roster)
            for sid in cd.get("enrolled_students", []):
                s = stu_by_id.get(sid)
                if s:
                    if s not in c.enrolled_students:
                        c.enrolled_students.append(s)
                    if c not in s.registered_courses:
                        s.registered_courses.append(c)

        # Step 4: Cross-check Student and Instructor lists for consistency
        for sd in data.get("students", []):
            s = stu_by_id.get(sd.get("student_id"))
            if s is None:
                continue
            for cid in sd.get("registered_courses", []):
                c = crs_by_id.get(cid)
                if c:
                    if c not in s.registered_courses:
                        s.registered_courses.append(c)
                    if s not in c.enrolled_students:
                        c.enrolled_students.append(s)

        for idata in data.get("instructors", []):
            inst = inst_by_id.get(idata.get("instructor_id"))
            if inst is None:
                continue
            for cid in idata.get("assigned_courses", []):
                c = crs_by_id.get(cid)
                if c:
                    if c not in inst.assigned_courses:
                        inst.assigned_courses.append(c)
                    if c.instructor is None:
                        c.instructor = inst

        print("Data loaded from", file_name)
        return students, instructors, courses
