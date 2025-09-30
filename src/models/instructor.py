from __future__ import annotations

from typing import List, TYPE_CHECKING

from .person import Person
# Only for type checkers / IDEs; not executed at runtime (avoids circular import)
if TYPE_CHECKING:
    from .course import Course


class Instructor(Person):
    """
    Instructor domain entity.

    Extends :class:`.person.Person` with a unique ``instructor_id`` and a list of
    assigned courses. Courses are stored as object references and exported
    to JSON as a list of course IDs via :meth:`to_dict`.

    :ivar instructor_id: Unique instructor identifier
    :vartype instructor_id: str
    :ivar assigned_courses: Courses this instructor is assigned to
    :vartype assigned_courses: list[Course]
    """

    def __init__(self, name: str, age: int, email: str, instructor_id: str) -> None:
        """
        Construct an instructor.

        :param name: Full name
        :type name: str
        :param age: Non-negative age in years
        :type age: int
        :param email: Contact email address
        :type email: str
        :param instructor_id: Unique instructor identifier
        :type instructor_id: str
        """
        super().__init__(name, age, email)
        self.instructor_id: str = instructor_id
        self.assigned_courses: List["Course"] = []

    def assign_course(self, course: "Course") -> None:
        """
        Assign the instructor to a course, if not already assigned.

        :param course: The course to assign
        :type course: Course
        """
        if course not in self.assigned_courses:
            self.assigned_courses.append(course)

    def to_dict(self) -> dict:
        """
        Serialize the instructor to a JSON-ready dictionary.

        The resulting dict extends :meth:`.person.Person.to_dict` with:
        - ``instructor_id`` (str)
        - ``assigned_courses`` (list[str]): IDs of assigned courses

        :return: JSON-ready mapping for this instructor
        :rtype: dict
        """
        d = super().to_dict()
        d["instructor_id"] = self.instructor_id
        d["assigned_courses"] = [c.course_id for c in self.assigned_courses]
        return d
