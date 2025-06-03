from flask import Blueprint, request
from src.database.api.services import class_service
from src.utils.jwt_helper import admin_required, login_required, student_required

class_bp = Blueprint('class', __name__, url_prefix='/api/classes')


@class_bp.route('/create', methods=['POST'])
@admin_required
def create_class():
    try:
        data = request.get_json()
        course_id = data.get('course_id')

        class_obj, error = class_service.create_class(course_id)
        if error:
            return {
                "status": "error",
                "message": error
            }, 400

        return {
            "status": "success",
            "data": {
                "class": {
                    "id": class_obj.id,
                    "name": class_obj.name,
                    "course_id": class_obj.course_id
                }
            }
        }, 201
    except Exception as e:
        print(f"Error in create_class endpoint: {str(e)}")
        return {
            "status": "error",
            "message": "Internal server error"
        }, 500


@class_bp.route('/', methods=['GET'])
@login_required
def get_all_classes():
    try:
        classes = class_service.get_all_classes()
        class_list = [{
            "id": c.id,
            "name": c.name,
            "course_id": c.course_id
        } for c in classes]

        return {
            "status": "success",
            "data": {
                "classes": class_list
            }
        }, 200
    except Exception as e:
        print(f"Error in get_all_classes endpoint: {str(e)}")
        return {
            "status": "error",
            "message": "Internal server error"
        }, 500
    

@class_bp.route('/by-student/<int:student_id>', methods=['GET'])
@student_required
def get_classes_by_student(student_id):
    try:
        classes = class_service.get_classes_by_student(student_id)
        class_list = [{
            "id": c.id,
            "name": c.name,
            "course_id": c.course_id
        } for c in classes]

        return {
            "status": "success",
            "data": {
                "classes": class_list
            }
        }, 200
    except Exception as e:
        print(f"Error in get_classes_by_student endpoint: {str(e)}")
        return {
            "status": "error",
            "message": "Internal server error"
        }, 500


@class_bp.route('/by-course/<int:course_id>', methods=['GET'])
@login_required
def get_classes_by_course(course_id):
    try:
        classes = class_service.get_classes_by_course(course_id)
        class_list = [{
            "id": c.id,
            "name": c.name,
            "course_id": c.course_id,
            "student_count": getattr(c, 'student_count', 0),
            "meeting_count": getattr(c, 'meeting_count', 0)
        } for c in classes]

        return {
            "status": "success",
            "data": {
                "classes": class_list
            }
        }, 200
    except Exception as e:
        print(f"Error in get_classes_by_course endpoint: {str(e)}")
        return {
            "status": "error",
            "message": "Internal server error"
        }, 500


@class_bp.route('/<int:class_id>', methods=['GET'])
@login_required
def get_class_detail(class_id):
    try:
        class_obj = class_service.get_class_by_id(class_id)
        if not class_obj:
            return {
                "status": "error",
                "message": "Class not found"
            }, 404

        return {
            "status": "success",
            "data": {
                "class": {
                    "id": class_obj.id,
                    "name": class_obj.name,
                    "course_id": class_obj.course_id
                }
            }
        }, 200
    except Exception as e:
        print(f"Error in get_class_detail endpoint: {str(e)}")
        return {
            "status": "error",
            "message": "Internal server error"
        }, 500
