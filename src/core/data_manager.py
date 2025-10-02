# src/models/data_manager.py
from __future__ import annotations

import json
from typing import List, Tuple, Type

from src.core.models.student import Student
from src.core.models.instructor import Instructor
from src.core.models.course import Course


class DataManager:
    """
    Unified data serialization helpers (Tk + PyQt compatible).

    Save:
      - save_to_file(filename, students, instructors, courses)        # uses to_dict()
      - save_obj_into_json(file_name, students, instructors, courses) # uses create_dict_from_obj()

    Load:
      - load_from_file(filename) -> dict                              # raw JSON dict (PyQt helper)
      - load_obj_from_json(file_name, Student, Instructor, Course)
          -> (students, instructors, courses)                         # rebuilds objects & links
    """

    # ------------------------------------------------------------------
    # Save (both styles)
    # ------------------------------------------------------------------
    @staticmethod
    def save_to_file(
        filename: str,
        students: List[Student],
        instructors: List[Instructor],
        courses: List[Course],
    ) -> None:
        """
        Save all data to JSON using each model's `to_dict()` (Tk style).
        """
        data = {
            "students": [s.to_dict() for s in students],
            "instructors": [i.to_dict() for i in instructors],
            "courses": [c.to_dict() for c in courses],
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print("Data saved to", filename)

    @staticmethod
    def save_obj_into_json(
        file_name: str,
        students: List[Student],
        instructors: List[Instructor],
        courses: List[Course],
    ) -> None:
        """
        Save all data to JSON using each model's `create_dict_from_obj()` (PyQt style).
        """
        data = {
            "students": [s.create_dict_from_obj() for s in students],
            "instructors": [i.create_dict_from_obj() for i in instructors],
            "courses": [c.create_dict_from_obj() for c in courses],
        }
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print("Data saved to", file_name)

    # ------------------------------------------------------------------
    # Load (both styles)
    # ------------------------------------------------------------------
    @staticmethod
    def load_from_file(filename: str) -> dict:
        """
        Load and return the raw JSON dict (PyQt-style helper).
        Does NOT rebuild relationships or objects.
        """
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def load_obj_from_json(
        file_name: str,
        Student: Type[Student],
        Instructor: Type[Instructor],
        Course: Type[Course],
    ) -> Tuple[List[Student], List[Instructor], List[Course]]:
        """
        Load from JSON and rebuild objects + relationships (Tk-style full loader).

        Recreates instances using `create_obj_from_dict` (or aliased `from_dict`)
        on the provided classes, then restores:
          - course.instructor  <-> instructor.assigned_courses
          - course.enrolled_students  <-> student.registered_courses
        """
        with open(file_name, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 1) Recreate objects from dictionaries (works with both unified APIs)
        students = [Student.create_obj_from_dict(d) for d in data.get("students", [])]
        instructors = [Instructor.create_obj_from_dict(d) for d in data.get("instructors", [])]
        courses = [Course.create_obj_from_dict(d) for d in data.get("courses", [])]

        # 2) Index by IDs for fast lookup
        stu_by_id = {s.student_id: s for s in students}
        inst_by_id = {i.instructor_id: i for i in instructors}
        crs_by_id = {c.course_id: c for c in courses}

        # 3) Restore relationships from course records
        for cd in data.get("courses", []):
            c = crs_by_id.get(cd.get("course_id"))
            if not c:
                continue

            # Link instructor
            inst_id = cd.get("instructor")
            if inst_id:
                inst = inst_by_id.get(inst_id)
                if inst:
                    c.instructor = inst
                    if c not in inst.assigned_courses:
                        inst.assigned_courses.append(c)

            # Link students (course roster)
            for sid in cd.get("enrolled_students", []):
                s = stu_by_id.get(sid)
                if s:
                    if s not in c.enrolled_students:
                        c.enrolled_students.append(s)
                    if c not in s.registered_courses:
                        s.registered_courses.append(c)

        # 4) Cross-check from student side (ensure symmetry)
        for sd in data.get("students", []):
            s = stu_by_id.get(sd.get("student_id"))
            if not s:
                continue
            for cid in sd.get("registered_courses", []):
                c = crs_by_id.get(cid)
                if c:
                    if c not in s.registered_courses:
                        s.registered_courses.append(c)
                    if s not in c.enrolled_students:
                        c.enrolled_students.append(s)

        # 5) Cross-check from instructor side (ensure symmetry)
        for idata in data.get("instructors", []):
            inst = inst_by_id.get(idata.get("instructor_id"))
            if not inst:
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
