from src.database.config import SessionLocal
from src.database.models import Course, Class, ClassStudent, Meeting, Attendance


def create_course(semester, course_id, academic_year, name):
    session = SessionLocal()

    existing_course = session.query(Course).filter(
        Course.course_id == course_id, Course.academic_year == academic_year).first()
    if existing_course:
        session.close()
        return None, "Course with this code and academic year already exists."

    new_course = Course(
        semester=semester,
        course_id=course_id,
        academic_year=academic_year,
        name=name
    )

    session.add(new_course)
    session.commit()
    session.refresh(new_course)
    session.close()

    return new_course, None


def get_all_courses():
    session = SessionLocal()
    courses = session.query(Course).order_by(
        Course.academic_year.desc(), Course.name.asc()).all()
    session.close()
    return courses

def get_courses_by_student(student_id):
    session = SessionLocal()
    courses = session.query(Course).join(
        Class, Course.id == Class.course_id
    ).join(
        ClassStudent, Class.id == ClassStudent.class_id
    ).filter(
        ClassStudent.student_id == student_id
    ).all()
    session.close()
    return courses


def get_courses_detail_by_student(student_id, semester, academic_year):
    session = SessionLocal()
    try:
        print(f"Fetching courses for student_id: {student_id}, semester: {semester}, academic_year: {academic_year}")
        
        # Get all courses for the student with their classes
        courses = session.query(Course).join(
            Class, Course.id == Class.course_id
        ).join(
            ClassStudent, Class.id == ClassStudent.class_id
        ).filter(
            ClassStudent.student_id == student_id,
            Course.semester == semester,
            Course.academic_year == academic_year
        ).all()
        
        print(f"Found {len(courses)} courses for student")

        # For each course, get attendance information
        course_list = []
        for course in courses:
            print(f"Processing course: {course.name} (ID: {course.id})")
            
            # Get all classes for this course where student is enrolled
            classes = session.query(Class).join(
                ClassStudent, Class.id == ClassStudent.class_id
            ).filter(
                Class.course_id == course.id,
                ClassStudent.student_id == student_id
            ).all()
            
            print(f"Found {len(classes)} enrolled classes for course {course.name}")
            
            for class_ in classes:
                print(f"Processing class: {class_.name} (ID: {class_.id})")
                
                # Count total meetings for this class
                meetings = session.query(Meeting).filter(Meeting.class_id == class_.id).count()
                print(f"Total meetings for class {class_.name}: {meetings}")
                
                # Get the class_student record for this student and class
                class_student = session.query(ClassStudent).filter(
                    ClassStudent.class_id == class_.id,
                    ClassStudent.student_id == student_id
                ).first()
                
                if class_student:
                    print(f"Found class_student record (ID: {class_student.id})")
                    # Count student's attendance for this class
                    attendance = session.query(Attendance).filter(
                        Attendance.class_student_id == class_student.id,
                        Attendance.status == 'Hadir'
                    ).count()
                    
                    print(f"Attendance count for class {class_.name}: {attendance}")
                    
                    course_data = {
                        "id": course.id,
                        "semester": course.semester,
                        "course_id": course.course_id,
                        "class": class_.name,
                        "class_id": class_.id,
                        "academic_year": course.academic_year,
                        "name": course.name,
                        "attendance": attendance,
                        "total_meetings": meetings,
                        "attendance_rate": attendance / meetings * 100 if meetings > 0 else 0
                    }
                    print(f"Course data prepared: {course_data}")
                    course_list.append(course_data)
                else:
                    print(f"No class_student record found for student {student_id} in class {class_.id}")

        print(f"Returning {len(course_list)} course entries with attendance data")
        return course_list
    except Exception as e:
        print(f"Error in get_courses_detail_by_student: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return []
    finally:
        session.close()

def get_course_by_id(course_id):
    session = SessionLocal()
    course = session.query(Course).filter(Course.id == course_id).first()
    session.close()
    return course

def delete_course(course_id):
    session = SessionLocal()
    try:
        print(f"Checking if course {course_id} exists...")
        # Check if course exists
        course = session.query(Course).get(course_id)
        if not course:
            print(f"Course {course_id} not found")
            return False, "Course not found"

        print(f"Getting all classes for course {course_id}...")
        # Get all classes for this course
        classes = session.query(Class).filter(Class.course_id == course_id).all()
        
        # For each class, delete its related records
        for class_obj in classes:
            print(f"Processing class {class_obj.id}...")
            
            # Get all class_student records for this class
            class_students = session.query(ClassStudent).filter(ClassStudent.class_id == class_obj.id).all()
            
            # Delete attendance records for each class_student
            for cs in class_students:
                print(f"Deleting attendance records for class_student {cs.id}...")
                session.query(Attendance).filter(Attendance.class_student_id == cs.id).delete()
            
            # Delete class_students and meetings
            deleted_students = session.query(ClassStudent).filter(ClassStudent.class_id == class_obj.id).delete()
            deleted_meetings = session.query(Meeting).filter(Meeting.class_id == class_obj.id).delete()
            print(f"Deleted {deleted_students} student records and {deleted_meetings} meeting records")
            
            # Delete the class
            session.delete(class_obj)
        
        print(f"Deleting course {course_id}...")
        # Finally delete the course
        session.delete(course)
        session.commit()
        print(f"Successfully deleted course {course_id}")
        return True, None
    except Exception as e:
        print(f"Error in delete_course service: {str(e)}")
        session.rollback()
        return False, str(e)
    finally:
        session.close()
