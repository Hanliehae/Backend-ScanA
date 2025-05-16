from src.database.config import SessionLocal
from src.database.models import Attendance, Meeting, ClassStudent as StudentClass
from datetime import datetime
from sqlalchemy.orm import joinedload


def mark_attendance(meeting_id, student_id, scan_type):
    session = SessionLocal()

    meeting = session.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        session.close()
        return None, "Meeting not found."

    student_class = session.query(StudentClass).filter(
        StudentClass.student_id == student_id,
        StudentClass.class_id == meeting.class_id
    ).first()

    if not student_class:
        session.close()
        return None, "Student is not assigned to this class."

    attendance = session.query(Attendance).filter(
        Attendance.meeting_id == meeting_id,
        Attendance.class_student_id == student_class.id
    ).first()

    if not attendance:
        attendance = Attendance(
            meeting_id=meeting_id,
            class_student_id=student_class.id
        )
        session.add(attendance)
        session.commit()
        session.refresh(attendance)

    now = datetime.now()

    if scan_type == "in":
        if attendance.check_in_time is None:
            attendance.check_in_time = now
    elif scan_type == "out":
        if attendance.check_out_time is None:
            attendance.check_out_time = now
    else:
        session.close()
        return None, "Invalid scan_type. Must be 'in' or 'out'."

    if attendance.check_in_time:
        attendance.status = "Hadir"

    session.commit()
    session.refresh(attendance)
    session.close()

    return attendance, None


def get_attendance_by_meeting(meeting_id):
    session = SessionLocal()

    attendances = session.query(Attendance).options(
        joinedload(Attendance.class_student)
    ).filter(
        Attendance.meeting_id == meeting_id
    ).all()

    session.close()
    return attendances
