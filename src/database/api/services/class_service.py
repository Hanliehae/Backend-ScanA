from src.database.config import SessionLocal
from src.database.models import Class, Course, ClassStudent, Meeting
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
