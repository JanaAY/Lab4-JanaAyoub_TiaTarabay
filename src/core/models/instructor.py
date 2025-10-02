# models/instructor.py
from __future__ import annotations

from typing import List, TYPE_CHECKING

from .person import Person

# Avoid runtime circular imports; only for type checking
if TYPE_CHECKING:
    from .course import Course


class Instructor(Person):
    """
    Unified Instructor entity (Tk + PyQt compatible).

    - Keeps `instructor_id` and `assigned_courses`.
    - assign_course(): optional duplicate-avoid, link-back, and verbose print.
    - Dict I/O in both styles:
        * Tk style:    to_dict() / from_dict()
        * PyQt style:  create_dict_from_obj() / create_obj_from_dict()
    - introduce(): preserved from PyQt version.
    """

    def __init__(self, name: str, age: int, email: str, instructor_id: str) -> None:
        super().__init__(name, age, email)
        self.instructor_id: str = instructor_id
        self.assigned_courses: List["Course"] = []

    # ---------------------------------------------------------------------
    # Behavior
    # ---------------------------------------------------------------------
    def assign_course(
        self,
        course: "Course",
        *,
        unique: bool = True,
        link_back: bool = True,
        verbose: bool = False,
    ) -> None:
        """
        Assign this instructor to a course.

        :param course: Course to assign.
        :param unique: If True, do nothing if already assigned (Tk behavior).
        :param link_back: If True, set `course.instructor = self` (PyQt behavior).
        :param verbose: If True, print a confirmation (PyQt behavior).
        """
        if unique and course in self.assigned_courses:
            # already assigned; keep idempotent
            pass
        else:
            self.assigned_courses.append(course)

        if link_back:
            course.instructor = self

        if verbose:
            print(f"Instructor {self.name} has been successfully assigned to {course.course_name}.")

    def introduce(self) -> None:
        """Print a self-introduction message (from the PyQt version)."""
        # Support either Person.email or a protected _email field
        email_value = getattr(self, "email", getattr(self, "_email", ""))
        print(
            f"Hey, I am {self.name}, an instructor, {self.age} years old. "
            f"\nMy email is {email_value} and my ID is {self.instructor_id}."
        )

    # ---------------------------------------------------------------------
    # Serialization (both styles)
    # ---------------------------------------------------------------------
    def to_dict(self) -> dict:
        """
        Tk-style export. Extends Person.to_dict() with:
          - instructor_id
          - assigned_courses: list of course_ids
        """
        d = super().to_dict() if hasattr(super(), "to_dict") else {
            "name": self.name,
            "age": self.age,
            # prefer public email if Person exposes it; else fall back
            "email": getattr(self, "email", getattr(self, "_email", "")),
        }
        d["instructor_id"] = self.instructor_id
        d["assigned_courses"] = [c.course_id for c in self.assigned_courses]
        return d

    # PyQt-compatible alias
    def create_dict_from_obj(self) -> dict:
        """PyQt-style dict export (alias to to_dict)."""
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: dict) -> "Instructor":
        """
        Tk-style constructor from dict.
        Expects: name, age, email, instructor_id.
        """
        return cls(data["name"], int(data["age"]), data["email"], data["instructor_id"])

    # PyQt-compatible alias
    @classmethod
    def create_obj_from_dict(cls, data: dict) -> "Instructor":
        """PyQt-style constructor from dict (alias to from_dict)."""
        return cls.from_dict(data)
