# models/course.py
from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

# Only for type checkers / IDEs; avoids circular imports at runtime
if TYPE_CHECKING:
    from .instructor import Instructor
    from .student import Student


class Course:
    """
    Course domain entity.

    Stores a course identifier, a human-readable name, an optional instructor,
    and a list of enrolled students. Relationships are kept as object references.

    Compatibility:
    - Tk-style: `to_dict()` and `from_dict()`, unique add (no duplicates).
    - PyQt-style: `create_dict_from_obj()` and `create_obj_from_dict()`,
      optional verbose print on enrollment.

    :ivar course_id: Unique course identifier (e.g., "EECE431")
    :vartype course_id: str
    :ivar course_name: Descriptive course name (e.g., "Control Systems")
    :vartype course_name: str
    :ivar instructor: Assigned instructor, or ``None`` if unassigned
    :vartype instructor: Optional[Instructor]
    :ivar enrolled_students: Students registered in this course
    :vartype enrolled_students: list[Student]
    """

    def __init__(self, course_id: str, course_name: str, instructor: Optional["Instructor"] = None) -> None:
        """
        Construct a course.

        :param course_id: Unique course identifier
        :type course_id: str
        :param course_name: Human-readable course name
        :type course_name: str
        :param instructor: Assigned instructor (optional)
        :type instructor: Optional[Instructor]
        """
        self.course_id: str = course_id
        self.course_name: str = course_name
        self.instructor: Optional["Instructor"] = instructor   # may be None
        self.enrolled_students: List["Student"] = []           # list of Student objects

    # ---------------------------------------------------------------------
    # Behavior
    # ---------------------------------------------------------------------
    def add_student(self, student: "Student", *, unique: bool = True, verbose: bool = False) -> None:
        """
        Enroll a student in this course.

        TK behavior (default): avoid duplicates (``unique=True``).
        PyQt behavior: print confirmation (set ``verbose=True``).

        :param student: The student to enroll
        :type student: Student
        :param unique: If True, do nothing when the student is already enrolled
        :type unique: bool
        :param verbose: If True, print a confirmation message
        :type verbose: bool
        :return: ``None``
        :rtype: None
        """
        if unique and student in self.enrolled_students:
            return
        if not unique or student not in self.enrolled_students:
            self.enrolled_students.append(student)
        if verbose:
            print(f"{student.name} has been successfully enrolled in {self.course_name} ({self.course_id}).")

    # ---------------------------------------------------------------------
    # Serialization (both styles)
    # ---------------------------------------------------------------------
    def to_dict(self) -> dict:
        """
        Serialize to a JSON-ready dictionary (Tk style).

        Fields:
            - ``course_id`` (str)
            - ``course_name`` (str)
            - ``instructor`` (str or ``None``): instructor ID if assigned
            - ``enrolled_students`` (list[str]): IDs of enrolled students

        :return: JSON-ready mapping for this course
        :rtype: dict
        """
        return {
            "course_id": self.course_id,
            "course_name": self.course_name,
            "instructor": self.instructor.instructor_id if self.instructor else None,
            "enrolled_students": [s.student_id for s in self.enrolled_students],
        }

    # PyQt-compatible alias
    def create_dict_from_obj(self) -> dict:
        """
        PyQt-style dictionary export.

        :return: Dictionary with course info, instructor ID, and enrolled students.
        :rtype: dict[str, str | list | None]
        """
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: dict) -> "Course":
        """
        Construct a course from a dict (relations not wired here).

        :param data: Mapping with at least ``course_id`` and ``course_name``.
        :type data: dict
        :return: A new Course instance
        :rtype: Course
        """
        return cls(data["course_id"], data["course_name"])

    # PyQt-compatible alias
    @classmethod
    def create_obj_from_dict(cls, data: dict) -> "Course":
        """
        PyQt-style constructor from dict (alias of :meth:`from_dict`).

        :param data: Mapping with at least ``course_id`` and ``course_name``.
        :type data: dict
        :return: A new Course instance
        :rtype: Course
        """
        return cls.from_dict(data)
