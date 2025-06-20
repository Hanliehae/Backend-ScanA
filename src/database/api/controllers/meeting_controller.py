from flask import Blueprint, request
from src.database.api.services import meeting_service
from src.utils.jwt_helper import admin_required, login_required, student_required

meeting_bp = Blueprint('meeting', __name__, url_prefix='/api/meetings')


@meeting_bp.route('/create', methods=['POST'])
@admin_required
def create_meeting():
    data = request.get_json()
    class_id = data.get('class_id')
    date = data.get('date')  # format: YYYY-MM-DD
    start_time = data.get('start_time')  # format: HH:MM
    end_time = data.get('end_time')  # format: HH:MM

    if not all([class_id, date, start_time, end_time]):
        return {"message": "All fields are required."}, 400

    meeting, error = meeting_service.create_meeting(
        class_id, date, start_time, end_time)
    if error:
        return {"message": error}, 400

    return {
        "message": "Meeting created successfully.",
        "meeting": {
            "id": meeting.id,
            "date": meeting.date.strftime('%Y-%m-%d'),
            "start_time": meeting.start_time,
            "end_time": meeting.end_time
        }
    }, 201


@meeting_bp.route('/by-class/<int:class_id>', methods=['GET'])
@login_required
def get_meetings_by_class(class_id):
    meetings_data = meeting_service.get_meetings_by_class(class_id)
    
    meeting_list = []
    for meeting, attendance_count, total_students in meetings_data:
        # Pastikan attendance_count tidak melebihi total_students
        attendance_count = min(attendance_count, total_students) if total_students > 0 else 0
        
        meeting_list.append({
            "id": meeting.id,
            "date": meeting.date.strftime('%Y-%m-%d'),
            "start_time": meeting.start_time,
            "end_time": meeting.end_time,
            "attendance_count": attendance_count,
            "total_students": total_students,
            "attendance_percentage": round((attendance_count / total_students * 100), 2) if total_students > 0 else 0
        })

    return {"meetings": meeting_list}, 200


@meeting_bp.route('/all', methods=['GET'])
@login_required
def get_all_meetings():
    try:
        meetings = meeting_service.get_all_meetings()
        return {
            "status": "success",
            "data": {
                "meetings": meetings
            }
        }, 200
    except Exception as e:
        print(f"Error in get_all_meetings endpoint: {str(e)}")
        return {
            "status": "error",
            "message": "Internal server error"
        }, 500
    
@meeting_bp.route('/by-student/<int:student_id>', methods=['GET'])
@student_required
def get_meetings(student_id):
    try:
        meetings = meeting_service.get_meetings_by_student(student_id)
        return {
            "status": "success",
            "data": {
                "meetings": meetings
            }
        }, 200
    except Exception as e:
        print(f"Error in get_all_meetings endpoint: {str(e)}")
        return {
            "status": "error",
            "message": "Internal server error"
        }, 500
