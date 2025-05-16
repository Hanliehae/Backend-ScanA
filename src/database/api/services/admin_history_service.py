from src.database.config import SessionLocal
from src.database.models import Attendance, Meeting, Course, ClassStudent, Class, User
from sqlalchemy.orm import joinedload

db = SessionLocal()


def get_all_attendance_history(course_id=None, student_id=None, semester=None, academic_year=None, class_id=None, status=None):
    try:
        # Base query with joins
        query = db.query(
            Attendance,
            Meeting,
            Class,
            Course,
            User,
            ClassStudent
        ).join(
            Meeting, Attendance.meeting_id == Meeting.id
        ).join(
            Class, Meeting.class_id == Class.id
        ).join(
            Course, Class.course_id == Course.id
        ).join(
            ClassStudent, Attendance.class_student_id == ClassStudent.id
        ).join(
            User, ClassStudent.student_id == User.id
        )

        # Apply filters if provided
        if course_id:
            query = query.filter(Course.id == course_id)
        if student_id:
            query = query.filter(User.id == student_id)
        if semester:
            query = query.filter(Course.semester == semester)
        if academic_year:
            query = query.filter(Course.academic_year == academic_year)
        if class_id:
            query = query.filter(Class.id == class_id)
        if status:
            query = query.filter(Attendance.status == status)

        # Execute query
        results = query.all()

        return results

    except Exception as e:
        print(f"Error in get_all_attendance_history: {str(e)}")
        raise e
    finally:
        db.close()
