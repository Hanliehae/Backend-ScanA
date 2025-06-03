from src.database.config import SessionLocal
from src.database.models import Class, User, ClassStudent, Attendance
from sqlalchemy import func, and_


def add_students_to_class(class_id, student_ids):
    session = SessionLocal()

    # Cek apakah kelas ada
    class_obj = session.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        session.close()
        return None, "Class not found."

    # Cek semua mahasiswa
    students = session.query(User).filter(
        User.id.in_(student_ids), User.role == 'user').all()

    if not students:
        session.close()
        return None, "No valid students found."

    # Tambahkan mahasiswa satu-satu
    added_students = []
    for student in students:
        # Cek apakah sudah ada
        existing = session.query(ClassStudent).filter_by(
            class_id=class_id, student_id=student.id).first()
        if not existing:
            class_student = ClassStudent(
                class_id=class_id,
                student_id=student.id
            )
            session.add(class_student)
            added_students.append(student)

    session.commit()
    session.close()

    return added_students, None


def get_students_in_class(class_id, meeting_id):
    session = SessionLocal()
    try:
        # Get all students in class with their attendance count and meeting-specific attendance
        students = session.query(
            User,
            func.count(Attendance.id).label('attendance_count'),
            Attendance.check_in_time,
            Attendance.check_out_time,
            Attendance.status
        ).join(
            ClassStudent, ClassStudent.student_id == User.id
        ).outerjoin(
            Attendance, and_(
                Attendance.class_student_id == ClassStudent.id,
                Attendance.meeting_id == meeting_id
            )
        ).filter(
            ClassStudent.class_id == class_id
        ).group_by(User.id, Attendance.check_in_time, Attendance.check_out_time, Attendance.status).all()

        # Format the result
        result = []
        for student, attendance_count, check_in_time, check_out_time, status in students:
            result.append({
                "user": student,
                "attendance_count": attendance_count,
                "check_in_time": check_in_time.strftime("%H:%M") if check_in_time else None,
                "check_out_time": check_out_time.strftime("%H:%M") if check_out_time else None,
                "status": status or "Belum Hadir"
            })

        return result
    finally:
        session.close()


def remove_students_from_class(class_id, student_ids):
    session = SessionLocal()
    try:
        # Check if class exists
        class_obj = session.query(Class).filter(Class.id == class_id).first()
        if not class_obj:
            session.close()
            return None, "Class not found."

        # Remove students from class
        deleted_count = session.query(ClassStudent).filter(
            ClassStudent.class_id == class_id,
            ClassStudent.student_id.in_(student_ids)
        ).delete(synchronize_session=False)

        session.commit()
        session.close()

        return deleted_count, None
    except Exception as e:
        session.rollback()
        session.close()
        return None, str(e)


def get_students_all_in_class(class_id):
    session = SessionLocal()
    try:
        # Get all students in class with their attendance count and meeting-specific attendance
        students = session.query(
            User,
            func.count(Attendance.id).label('attendance_count'),
        ).join(
            ClassStudent, ClassStudent.student_id == User.id
        ).outerjoin(
            Attendance, and_(
                Attendance.class_student_id == ClassStudent.id,
                Attendance.status == 'Hadir'
            )
        ).filter(
            ClassStudent.class_id == class_id
        ).group_by(User.id).all()

        # Format the result
        result = []
        for student, attendance_count in students:
            result.append({
                "user": student,
                "attendance_count": attendance_count,
            })

        return result
    finally:
        session.close()