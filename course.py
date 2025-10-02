"""Course class module.

This module defines the :class:`Course` class, representing a course in
the school management system. Each course has a unique identifier, a
name, an optional instructor, and a list of enrolled students.
"""


class Course:
    """Represents a course in the school management system.

    Attributes
    ----------
    course_id : str
        Unique identifier for the course.
    course_name : str
        Name of the course.
    instructor : Instructor | None
        Instructor assigned to this course, if any.
    enrolled_students : list
        List of students enrolled in this course.
    """

    def __init__(self, course_id: str, course_name: str, instructor=None):
        """Initialize a Course object.

        :param course_id: Unique identifier for the course.
        :type course_id: str
        :param course_name: Name of the course.
        :type course_name: str
        :param instructor: Instructor assigned to this course, optional.
        :type instructor: Instructor | None
        """
        self.course_id = course_id
        self.course_name = course_name
        self.instructor = instructor
        self.enrolled_students = []

    def add_student(self, student) -> None:
        """Enroll a student into the course.

        :param student: The student object to enroll.
        :type student: Student
        :return: ``None``
        :rtype: None
        """
        self.enrolled_students.append(student)
        print(
            f"{student.name} has been successfully enrolled in {self.course_name} ({self.course_id})."
        )

    def create_dict_from_obj(self) -> dict:
        """Convert this Course instance into a dictionary.

        :return: Dictionary with course information, instructor ID, and enrolled students.
        :rtype: dict[str, str | list | None]
        """
        return {
            "course_id": self.course_id,
            "course_name": self.course_name,
            "instructor": self.instructor.instructor_id if self.instructor else None,
            "enrolled_students": [s.student_id for s in self.enrolled_students],
        }

    @classmethod
    def create_obj_from_dict(cls, data: dict) -> "Course":
        """Create a Course object from a dictionary.

        :param data: Dictionary containing course information.
        :type data: dict
        :return: A new Course instance.
        :rtype: Course
        """
        return cls(data["course_id"], data["course_name"])