from src.database.models import Attendance, Meeting, Class, Course, ClassStudent
from src.database.config import SessionLocal
from sqlalchemy.orm import joinedload

db = SessionLocal()


def get_attendance_history(student_id, course_id=None, semester=None, year=None):
    query = db.query(Attendance).join(Attendance.class_student).join(ClassStudent.class_).join(Class.course).options(
        joinedload(Attendance.meeting).joinedload(
            Meeting.class_).joinedload(Class.course)
    ).filter(ClassStudent.student_id == student_id)

    if course_id:
        query = query.filter(Class.course_id == course_id)
    if semester:
        query = query.filter(Course.semester == semester)
    if year:
        query = query.filter(Course.academic_year == year)

    return query.all()
