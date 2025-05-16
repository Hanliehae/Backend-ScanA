from src.database.config import SessionLocal
from src.database.models import Class, User, ClassStudent


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


def get_students_in_class(class_id):
    session = SessionLocal()
    students = (
        session.query(User)
        .join(ClassStudent, ClassStudent.student_id == User.id)
        .filter(ClassStudent.class_id == class_id)
        .all()
    )
    session.close()
    return students
