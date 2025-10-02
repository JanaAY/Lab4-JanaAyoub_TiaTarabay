from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

# Only for type checkers / IDEs; not executed at runtime (avoids circular import)
if TYPE_CHECKING:
    from .instructor import Instructor
    from .student import Student


class Course:
    """
    Course domain entity.

    Stores a course identifier, a human-readable name, an optional instructor,
    and a list of enrolled students. Relationships are kept as object references,
    while :meth:`to_dict` exports lightweight ID lists for JSON.

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

    def add_student(self, student: "Student") -> None:
        """
        Enroll a student in this course (no effect if already enrolled).

        :param student: The student to enroll
        :type student: Student
        """
        if student not in self.enrolled_students:
            self.enrolled_students.append(student)

    def to_dict(self) -> dict:
        """
        Serialize the course to a JSON-ready dictionary.

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
