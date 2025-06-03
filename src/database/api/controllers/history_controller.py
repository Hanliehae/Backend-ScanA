from flask import Blueprint, request
from src.database.api.services import history_service
from src.utils.jwt_helper import student_required
from flask_jwt_extended import get_jwt_identity

history_bp = Blueprint('history', __name__, url_prefix='/api/history')


@history_bp.route('/', methods=['GET'])
@student_required
def attendance_history():
    try:
        # Get query parameters for filtering
        student_id = request.args.get('student_id', type=int)
        course_id = request.args.get('course_id', type=int)
        semester = request.args.get('semester')
        academic_year = request.args.get('academic_year')
        class_id = request.args.get('class_id', type=int)
        status = request.args.get('status')

        # Get attendance history with filters
        results = history_service.get_attendance_history(
            student_id=student_id,
            course_id=course_id,
            semester=semester,
            academic_year=academic_year,
            class_id=class_id,
            status=status
        )

        # Format response
        history = []
        for attendance, meeting, class_, course, user, class_student in results:
            history.append({
                'id': attendance.id,
                'status': attendance.status.value,
                'check_in_time': attendance.check_in_time.strftime('%Y-%m-%d %H:%M:%S') if attendance.check_in_time else None,
                'check_out_time': attendance.check_out_time.strftime('%Y-%m-%d %H:%M:%S') if attendance.check_out_time else None,
                'meeting': {
                    'id': meeting.id,
                    'date': meeting.date.strftime('%Y-%m-%d'),
                    'start_time': meeting.start_time,
                    'end_time': meeting.end_time
                },
                'course': {
                    'id': course.id,
                    'course_id': course.course_id,
                    'name': course.name,
                    'semester': course.semester,
                    'academic_year': course.academic_year
                },
                'class': {
                    'id': class_.id,
                    'name': class_.name
                },
                'student': {
                    'id': user.id,
                    'name': user.name,
                    'nim': user.nim
                }
            })

        return {
            "status": "success",
            "data": {
                "history": history
            }
        }, 200

    except Exception as e:
        print(f"Error in all_attendance_history endpoint: {str(e)}")
        return {
            "status": "error",
            "message": "Internal server error"
        }, 500
