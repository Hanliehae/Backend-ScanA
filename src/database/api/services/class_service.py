from src.database.config import SessionLocal
from src.database.models import Class, Course, ClassStudent, Meeting, Attendance
import string


def generate_class_name(existing_classes):
    """Generate nama kelas A, B, C, dst sesuai urutan"""
    alphabet = string.ascii_uppercase  # A-Z
    return alphabet[len(existing_classes)]


def create_class(course_id):
    session = SessionLocal()
    try:
        course = session.query(Course).get(course_id)
        if not course:
            return None, "Course not found"

        # Generate class name based on course name and existing classes
        existing_classes = session.query(Class).filter_by(course_id=course_id).all()
        class_number = len(existing_classes) + 1
        class_name = f"{course.name} - Kelas {class_number}"

        new_class = Class(name=class_name, course_id=course_id)
        session.add(new_class)
        session.commit()
        session.refresh(new_class)  # Refresh to get the ID
        return new_class, None
    except Exception as e:
        session.rollback()
        return None, str(e)
    finally:
        session.close()


def get_all_classes():
    session = SessionLocal()
    try:
        return session.query(Class).all()
    except Exception as e:
        print(f"Error in get_all_classes: {str(e)}")
        return []
    finally:
        session.close()


def get_classes_by_student(student_id):
    session = SessionLocal()
    try:
        classes = session.query(Class).join(
            ClassStudent, Class.id == ClassStudent.class_id
        ).filter(
            ClassStudent.student_id == student_id
        ).all()
        return classes
    except Exception as e:
        print(f"Error in get_classes_by_student: {str(e)}")
        return []
    finally:
        session.close()


def get_classes_by_course(course_id):
    session = SessionLocal()
    try:
        classes = session.query(Class).filter_by(course_id=course_id).all()
        # Get counts for each class
        for class_obj in classes:
            class_obj.student_count = session.query(ClassStudent).filter_by(class_id=class_obj.id).count()
            class_obj.meeting_count = session.query(Meeting).filter_by(class_id=class_obj.id).count()
        return classes
    except Exception as e:
        print(f"Error in get_classes_by_course: {str(e)}")
        return []
    finally:
        session.close()


def get_class_by_id(class_id):
    session = SessionLocal()
    try:
        return session.query(Class).get(class_id)
    except Exception as e:
        print(f"Error in get_class_by_id: {str(e)}")
        return None
    finally:
        session.close()

def delete_class(class_id):
    session = SessionLocal()
    try:
        print(f"Checking if class {class_id} exists...")
        # Check if class exists
        class_obj = session.query(Class).get(class_id)
        if not class_obj:
            print(f"Class {class_id} not found")
            return False, "Class not found"

        print(f"Deleting related records for class {class_id}...")
        
        # Get all class_student records for this class
        class_students = session.query(ClassStudent).filter(ClassStudent.class_id == class_id).all()
        
        # Delete attendance records for each class_student
        for cs in class_students:
            print(f"Deleting attendance records for class_student {cs.id}...")
            session.query(Attendance).filter(Attendance.class_student_id == cs.id).delete()
        
        # Now we can safely delete class_students and meetings
        deleted_students = session.query(ClassStudent).filter(ClassStudent.class_id == class_id).delete()
        deleted_meetings = session.query(Meeting).filter(Meeting.class_id == class_id).delete()
        print(f"Deleted {deleted_students} student records and {deleted_meetings} meeting records")

        print(f"Deleting class {class_id}...")
        # Delete the class
        session.delete(class_obj)
        session.commit()
        print(f"Successfully deleted class {class_id}")
        return True, None
    except Exception as e:
        print(f"Error in delete_class service: {str(e)}")
        session.rollback()
        return False, str(e)
    finally:
        session.close()