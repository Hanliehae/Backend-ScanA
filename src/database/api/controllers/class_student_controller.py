from flask import Blueprint, request
from src.database.api.services import class_student_service
from src.utils.jwt_helper import admin_required, login_required
from src.database.config import SessionLocal
from src.database.models import Meeting

class_student_bp = Blueprint(
    'class_student', __name__, url_prefix='/api/class-students')


@class_student_bp.route('/add', methods=['POST'])
@admin_required
def add_students():
    data = request.get_json()
    class_id = data.get('class_id')
    student_ids = data.get('student_ids')  # List of student IDs

    if not isinstance(student_ids, list):
        return {"message": "student_ids must be a list"}, 400

    added_students, error = class_student_service.add_students_to_class(
        class_id, student_ids)
    if error:
        return {"message": error}, 400

    return {
        "message": f"Added {len(added_students)} students to class."
    }, 200


@class_student_bp.route('/by-class/<int:class_id>', methods=['GET'])
@login_required
def get_students_by_class(class_id):
    students_data = class_student_service.get_students_in_class(class_id)
    
    # Get total meetings in this class for percentage calculation
    session = SessionLocal()
    total_meetings = session.query(Meeting).filter(
        Meeting.class_id == class_id
    ).count()
    session.close()

    student_list = [{
        "id": data["user"].id,
        "nim": data["user"].nim,
        "name": data["user"].name,
        "email": data["user"].email,
        "phone": data["user"].phone,
        "attendance_count": data["attendance_count"],
        "total_meetings": total_meetings,
        "attendance_percentage": round((data["attendance_count"] / total_meetings * 100), 2) if total_meetings > 0 else 0
    } for data in students_data]

    return {
        "students": student_list,
        "total_meetings": total_meetings
    }, 200


@class_student_bp.route('/remove', methods=['POST'])
@admin_required
def remove_students():
    data = request.get_json()
    class_id = data.get('class_id')
    student_ids = data.get('student_ids')  # List of student IDs

    if not isinstance(student_ids, list):
        return {"message": "student_ids must be a list"}, 400

    deleted_count, error = class_student_service.remove_students_from_class(
        class_id, student_ids)
    if error:
        return {"message": error}, 400

    return {
        "message": f"Removed {deleted_count} students from class."
    }, 200
