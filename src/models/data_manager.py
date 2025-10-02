import json
from typing import List
from .student import Student
from .instructor import Instructor
from .course import Course

class DataManager:
    @staticmethod
    def save_to_file(filename: str, students: List[Student], instructors: List[Instructor], courses: List[Course]) -> None:
        data={
            "students": [s.to_dict() for s in students],
            "instructors": [i.to_dict() for i in instructors],
            "courses": [c.to_dict() for c in courses]
        }
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def load_from_file(filename: str) -> dict:
        with open(filename, "r") as f:
            return json.load(f)
