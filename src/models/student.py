from __future__ import annotations

from typing import List, TYPE_CHECKING

from .person import Person
# Only for type checkers / IDEs; not executed at runtime (avoids circular import)
if TYPE_CHECKING:
    from .course import Course


class Student(Person):
    """
    Student domain entity.

    Extends :class:`.person.Person` with a unique ``student_id`` and a list of
    registered courses. Courses are stored as object references and exported
    to JSON as a list of course IDs via :meth:`to_dict`.

    :ivar student_id: Unique student identifier
    :vartype student_id: str
    :ivar registered_courses: Courses this student is registered in
    :vartype registered_courses: list[Course]
    """

    def __init__(self, name: str, age: int, email: str, student_id: str) -> None:
        """
        Construct a student.

        :param name: Full name
        :type name: str
        :param age: Non-negative age in years
        :type age: int
        :param email: Contact email address
        :type email: str
        :param student_id: Unique student identifier
        :type student_id: str
        """
        super().__init__(name, age, email)
        self.student_id: str = student_id
        self.registered_courses: List["Course"] = []

    def register_course(self, course: "Course") -> None:
        """
        Register the student in a course, if not already registered.

        :param course: The course to register
        :type course: Course
        """
        if course not in self.registered_courses:
            self.registered_courses.append(course)

    def to_dict(self) -> dict:
        """
        Serialize the student to a JSON-ready dictionary.

        The resulting dict extends :meth:`.person.Person.to_dict` with:
        - ``student_id`` (str)
        - ``registered_courses`` (list[str]): the IDs of registered courses

        :return: JSON-ready mapping for this student
        :rtype: dict
        """
        d = super().to_dict()
        d["student_id"] = self.student_id
        d["registered_courses"] = [c.course_id for c in self.registered_courses]
        return d
