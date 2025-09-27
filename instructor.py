"""Instructor class module.

This module defines the :class:`Instructor` class, representing an
instructor in the school management system. It extends
:class:`person.Person` with a unique instructor ID and assigned courses.
"""

from person import Person


class Instructor(Person):
    """Represents an instructor in the school system.

    Inherits from :class:`person.Person`.

    Attributes
    ----------
    instructor_id : str
        Unique identifier for the instructor.
    assigned_courses : list
        List of courses the instructor is assigned to teach.
    """

    def __init__(self, name: str, age: int, email: str, instructor_id: str):
        """Initialize an Instructor object.

        :param name: Instructor's full name.
        :type name: str
        :param age: Instructor's age (must be non-negative).
        :type age: int
        :param email: Instructor's email (must follow valid email format).
        :type email: str
        :param instructor_id: Unique identifier for the instructor.
        :type instructor_id: str
        """
        super().__init__(name, age, email)
        self.instructor_id = instructor_id
        self.assigned_courses = []

    def assign_course(self, course) -> None:
        """Assign this instructor to teach a course.

        :param course: The course object to assign.
        :type course: Course
        :return: ``None``
        :rtype: None

        .. note::
            - Adds the course to the instructor's ``assigned_courses``.
            - Sets this instructor as the course's ``instructor``.
        """
        self.assigned_courses.append(course)
        course.instructor = self
        print(f"Instructor {self.name} has been successfully assigned to {course.course_name}.")

    def introduce(self) -> None:
        """Print a self-introduction message.

        :return: ``None``
        :rtype: None
        """
        print(
            f"Hey, I am {self.name}, an instructor, {self.age} years old. "
            f"\nMy email is {self._email} and my ID is {self.instructor_id}."
        )

    def create_dict_from_obj(self) -> dict:
        """Convert this Instructor instance into a dictionary.

        Example output::

            {
                "name": "Alice",
                "age": 40,
                "email": "alice@uni.edu",
                "instructor_id": "I100",
                "assigned_courses": ["C101", "C102"]
            }

        :return: Dictionary with instructor details.
        :rtype: dict[str, str | int | list]
        """
        return {
            "name": self.name,
            "age": self.age,
            "email": self._email,
            "instructor_id": self.instructor_id,
            "assigned_courses": [c.course_id for c in self.assigned_courses],
        }

    @classmethod
    def create_obj_from_dict(cls, data: dict) -> "Instructor":
        """Reconstruct an Instructor object from a dictionary.

        :param data: Dictionary with keys ``name``, ``age``, ``email``, ``instructor_id``.
        :type data: dict
        :return: A new Instructor instance.
        :rtype: Instructor
        """
        return cls(data["name"], data["age"], data["email"], data["instructor_id"])