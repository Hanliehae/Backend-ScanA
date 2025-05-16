from flask import Blueprint, request
from src.database.api.services import history_service
from src.utils.jwt_helper import student_required
from flask_jwt_extended import get_jwt_identity

history_bp = Blueprint('history', __name__, url_prefix='/api/history')


@history_bp.route('/', methods=['GET'])
@student_required
def attendance_history():
    user = request.current_user

    # Bisa menerima filter opsional
    course_id = request.args.get('course_id', type=int)
    semester = request.args.get('semester')
    year = request.args.get('year', type=int)

    attendance_list = history_service.get_attendance_history(
        student_id=user.id,
        course_id=course_id,
        semester=semester,
        year=year
    )

    result = []
    for attendance in attendance_list:
        meeting = attendance.meeting
        class_ = meeting.class_
        course = class_.course

        result.append({
            "course_name": course.name,
            "course_id": course.id,
            "semester": course.semester,
            "academic_year": course.academic_year,
            "meeting_date": meeting.date.strftime('%Y-%m-%d'),
            "meeting_start_time": meeting.start_time,
            "meeting_end_time": meeting.end_time,
            "check_in_time": attendance.check_in_time.strftime('%H:%M') if attendance.check_in_time else None,
            "check_out_time": attendance.check_out_time.strftime('%H:%M') if attendance.check_out_time else None,
            "status": attendance.status
        })

    return {"history": result}, 200
