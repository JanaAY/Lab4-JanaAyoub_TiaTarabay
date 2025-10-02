"""Student class module.

This module defines the :class:`Student` class, which inherits from
:class:`person.Person` and represents a student in the school
management system.

It extends the base class with a unique student identifier and a list
of registered courses.
"""

from person import Person


class Student(Person):
    """Represents a student in the school management system.

    Inherits from :class:`person.Person`.

    Attributes
    ----------
    student_id : str
        Unique identifier for the student.
    registered_courses : list
        List of courses the student has registered for.
    """

    def __init__(self, name: str, age: int, email: str, student_id: str):
        """Initialize a Student object.

        :param name: Student's name.
        :type name: str
        :param age: Student's age (must be non-negative).
        :type age: int
        :param email: Student's email (must follow valid email format).
        :type email: str
        :param student_id: Unique identifier for the student.
        :type student_id: str
        """
        super().__init__(name, age, email)
        self.student_id = student_id
        self.registered_courses = []

    def register_course(self, course) -> None:
        """Register the student for a given course.

        :param course: The course object to register.
        :type course: Course
        :return: ``None``
        :rtype: None
        """
        self.registered_courses.append(course)
        print(f"{self.name} has successfully registered for {course.course_name}.")

    def introduce(self) -> None:
        """Print a short introduction message for the student.

        :return: ``None``
        :rtype: None
        """
        print(
            f"Hey, I am {self.name}, a student, {self.age} years old. \n"
            f"My email is {self._email} and my student ID is {self.student_id}."
        )

    def create_dict_from_obj(self) -> dict:
        """Convert this Student instance into a dictionary.

        :return: Dictionary with student information and registered courses.
        :rtype: dict[str, str | int | list]
        """
        return {
            "name": self.name,
            "age": self.age,
            "email": self._email,
            "student_id": self.student_id,
            "registered_courses": [c.course_id for c in self.registered_courses],
        }

    @classmethod
    def create_obj_from_dict(cls, data: dict) -> "Student":
        """Create a Student object from a dictionary.

        :param data: Dictionary containing student information.
        :type data: dict
        :return: A new Student object.
        :rtype: Student
        """
        return cls(data["name"], data["age"], data["email"], data["student_id"])