from models.student import Student
from models.instructor import Instructor
from models.course import Course
from models import db

def load_all():
    students=[]
    instructors=[]
    courses=[]

    #instructors
    inst_map={}
    for iid, name, age, email in db.get_all_instructors():
        ins=Instructor(name, int(age), email, iid)
        instructors.append(ins)
        inst_map[iid]=ins

    #courses 
    course_map={}
    for cid, cname, instr_id, _instr_name in db.get_all_courses():
        ins=inst_map.get(instr_id) if instr_id else None
        c = Course(cid, cname, ins)
        if ins:
            ins.assign_course(c)
        courses.append(c)
        course_map[cid] = c

    #students + their registrations
    for sid, name, age, email in db.get_all_students():
        s = Student(name, int(age), email, sid)
        students.append(s)
        for cid, _ in db.get_courses_of_student(sid):
            course=course_map.get(cid)
            if course:
                s.register_course(course)
                course.add_student(s)

    return students, instructors, courses
