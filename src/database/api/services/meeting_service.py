from src.database.config import SessionLocal
from src.database.models import Meeting, Class, Course
from sqlalchemy import func, and_
from src.database.models import Attendance, ClassStudent
from datetime import datetime
import calendar


def create_meeting(class_id, date, start_time, end_time):
    session = SessionLocal()

    # Pastikan kelas ada
    class_obj = session.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        session.close()
        return None, "Class not found."

    # Buat pertemuan baru
    new_meeting = Meeting(
        class_id=class_id,
        date=date,
        start_time=start_time,
        end_time=end_time
    )
    session.add(new_meeting)
    session.commit()

    session.refresh(new_meeting)
    session.close()

    return new_meeting, None


def get_meetings_by_class(class_id):
    session = SessionLocal()
    try:
        # Subquery untuk menghitung total siswa di kelas
        total_students_subq = session.query(
            func.count(ClassStudent.id)
        ).filter(
            ClassStudent.class_id == class_id
        ).scalar_subquery()

        # Query utama untuk mendapatkan pertemuan dengan jumlah kehadiran
        meetings = session.query(
            Meeting,
            func.count(Attendance.id).label('attendance_count'),
            total_students_subq.label('total_students')
        ).outerjoin(
            Attendance, and_(
                Attendance.meeting_id == Meeting.id,
                Attendance.status == 'Hadir'
            )
        ).filter(
            Meeting.class_id == class_id
        ).group_by(Meeting.id).order_by(Meeting.date.asc()).all()

        return meetings
    finally:
        session.close()



def get_all_meetings():
    session = SessionLocal()
    try:
        # Base query with joins
        query = session.query(
            Meeting,
            Class,
            Course
        ).join(
            Class, Meeting.class_id == Class.id
        ).join(
            Course, Class.course_id == Course.id
        )

        # Execute query
        results = query.all()

        # Format response
        meetings = []
        for meeting, class_, course in results:
            meetings.append({
                'id': meeting.id,
                'date': meeting.date.strftime('%Y-%m-%d'),
                'start_time': meeting.start_time,
                'end_time': meeting.end_time,
                'course': {
                    'id': course.id,
                    'course_id': course.course_id,
                    'name': course.name,
                    'semester': course.semester,
                    'academic_year': course.academic_year
                },
                'class': {
                    'id': class_.id,
                    'name': class_.name
                }
            })

        return meetings
    except Exception as e:
        print(f"Error in get_all_meetings: {str(e)}")
        raise e
    finally:
        session.close()
