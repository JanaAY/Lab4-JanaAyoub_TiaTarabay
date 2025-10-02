# models/student.py
from __future__ import annotations

from typing import List, TYPE_CHECKING
from .person import Person

if TYPE_CHECKING:
    from .course import Course


class Student(Person):
    """
    Unified Student domain entity (Tk + PyQt compatible).

    - Extends :class:`.person.Person` with a unique student_id.
    - Tracks registered courses as object references.
    - Provides both Tk-style and PyQt-style dict APIs.
    """

    def __init__(self, name: str, age: int, email: str, student_id: str) -> None:
        """
        Initialize a Student object.

        :param name: Full name
        :param age: Non-negative age in years
        :param email: Contact email address
        :param student_id: Unique student identifier
        """
        super().__init__(name, age, email)
        self.student_id: str = student_id
        self.registered_courses: List["Course"] = []

    # -------------------- behavior --------------------
    def register_course(self, course: "Course") -> None:
        """
        Register the student in a course (avoids duplicates).

        :param course: The course object
        """
        if course not in self.registered_courses:
            self.registered_courses.append(course)
            # PyQt-style feedback print (safe to keep)
            print(f"{self.name} has successfully registered for {course.course_name}.")

    def introduce(self) -> None:
        """Print a short introduction message (PyQt style retained)."""
        print(
            f"Hey, I am {self.name}, a student, {self.age} years old. \n"
            f"My email is {self._email} and my student ID is {self.student_id}."
        )

    # -------------------- serialization (both styles) --------------------
    def to_dict(self) -> dict:
        """
        Tk-style export. Includes a 'type' tag.

        Returns:
            {
              "name": str,
              "age": int,
              "email": str,
              "student_id": str,
              "registered_courses": [course_ids],
              "type": "Student"
            }
        """
        d = super().to_dict()
        d["student_id"] = self.student_id
        d["registered_courses"] = [c.course_id for c in self.registered_courses]
        return d

    def create_dict_from_obj(self) -> dict:
        """
        PyQt-style export (no 'type' field).
        """
        return {
            "name": self.name,
            "age": self.age,
            "email": self._email,
            "student_id": self.student_id,
            "registered_courses": [c.course_id for c in self.registered_courses],
        }

    # -------------------- constructors --------------------
    @classmethod
    def from_dict(cls, data: dict) -> "Student":
        """
        Tk-style constructor from dict (ignores 'type').
        """
        return cls(data["name"], int(data["age"]), data["email"], data["student_id"])

    @classmethod
    def create_obj_from_dict(cls, data: dict) -> "Student":
        """
        PyQt-style constructor from dict (alias).
        """
        return cls.from_dict(data)
