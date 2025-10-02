"""
Demo usage for School Management models.

This module demonstrates how to instantiate :class:`Student`,
:class:`Instructor`, and :class:`Course`, link them together,
and persist/load the project data via :class:`models.data_manager.DataManager`.

Run directly to see console output and JSON save/load behavior.
"""

from typing import Optional
from core.models.student import Student
from core.models.instructor import Instructor
from core.models.course import Course
from core.data_manager import DataManager


def show_course_info(course: Course) -> None:
    """
    Pretty-print a course summary to the console.

    :param course: The course to display, including its instructor (if any)
                   and enrolled students.
    :type course: models.course.Course
    :return: None
    :rtype: None
    """
    print("\nCourse:", course.course_id, "-", course.course_name)
    if course.instructor:
        print("Instructor:", course.instructor.instructor_id, f"({course.instructor.name})")
    else:
        print("Instructor: None")

    print("Students:")
    if not course.enrolled_students:
        print("  (none)")
    else:
        for s in course.enrolled_students:
            print("  -", s.student_id, f"({s.name})")


if __name__ == "__main__":
    #Construct sample objects
    tia = Student("Tia", 20, "twt00@mail.aub.edu", "202308794")
    prof = Instructor("Dr. Khraiche", 40, "mkhraiche@aub.edu.lb", "939238298")
    dsp = Course("BMEN610", "Neural Interfaces", prof)

    # Link relationships
    prof.assign_course(dsp)     # instructor -> course
    tia.register_course(dsp)    # student -> course
    dsp.add_student(tia)        # course -> student

    # Use model methods
    tia.introduce()
    prof.introduce()

    # Persist to JSON
    try:
        DataManager.save_to_file("school.json", [tia], [prof], [dsp])
        print("\nSaved to school.json")
    except Exception as e:
        print("Save failed:", e)

    # Load from JSON
    try:
        data = DataManager.load_from_file("school.json")
        print("Loaded keys:", list(data.keys()))
    except Exception as e:
        print("Load failed:", e)

    # Print a human-readable course summary
    show_course_info(dsp)
