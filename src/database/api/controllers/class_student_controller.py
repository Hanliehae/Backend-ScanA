from flask import Blueprint, request
from src.database.api.services import class_student_service
from src.utils.jwt_helper import admin_required, login_required

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
    students = class_student_service.get_students_in_class(class_id)
    student_list = [{
        "id": s.id,
        "nim": s.nim,
        "name": s.name,
        "email": s.email,
        "phone": s.phone
    } for s in students]

    return {"students": student_list}, 200
