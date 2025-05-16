from flask import Blueprint, request
from src.database.api.services import attendance_service
from src.utils.jwt_helper import admin_required, login_required
import base64
import cv2
import numpy as np
from datetime import datetime
import os

attendance_bp = Blueprint('attendance', __name__, url_prefix='/api/attendance')

def process_hand_image(image_data):
    try:
        # Decode base64 image
        nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply threshold
        _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None, "Tidak dapat mendeteksi telapak tangan"
            
        # Get the largest contour (should be the hand)
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Get hand features
        area = cv2.contourArea(largest_contour)
        perimeter = cv2.arcLength(largest_contour, True)
        
        # Calculate hand features
        features = {
            'area': float(area),
            'perimeter': float(perimeter),
            'circularity': float(4 * np.pi * area / (perimeter * perimeter)) if perimeter > 0 else 0
        }
        
        return features, None
        
    except Exception as e:
        return None, str(e)

@attendance_bp.route('/mark', methods=['POST'])
@admin_required
def mark_attendance():
    data = request.get_json()
    meeting_id = data.get('meeting_id')
    student_id = data.get('student_id')
    scan_type = data.get('scan_type')  # "in" atau "out"

    if not all([meeting_id, student_id, scan_type]):
        return {"message": "All fields are required."}, 400

    attendance, error = attendance_service.mark_attendance(
        meeting_id, student_id, scan_type)
    if error:
        return {"message": error}, 400

    return {
        "message": "Attendance recorded successfully.",
        "attendance": {
            "id": attendance.id,
            "check_in_time": attendance.check_in_time.strftime('%Y-%m-%d %H:%M:%S') if attendance.check_in_time else None,
            "check_out_time": attendance.check_out_time.strftime('%Y-%m-%d %H:%M:%S') if attendance.check_out_time else None,
            "status": attendance.status
        }
    }, 200


@attendance_bp.route('/by-meeting/<int:meeting_id>', methods=['GET'])
@login_required
def get_attendance_by_meeting(meeting_id):
    attendances = attendance_service.get_attendance_by_meeting(meeting_id)

    attendance_list = [{
        "student_id": a.class_student.student_id,  # << akses lewat relasi
        "check_in_time": a.check_in_time.strftime('%Y-%m-%d %H:%M:%S') if a.check_in_time else None,
        "check_out_time": a.check_out_time.strftime('%Y-%m-%d %H:%M:%S') if a.check_out_time else None,
        "status": a.status
    } for a in attendances]

    return {"attendances": attendance_list}, 200


@attendance_bp.route('/scan', methods=['POST'])
@admin_required
def scan_hand_for_attendance():
    try:
        data = request.get_json()
        if not data:
            return {"message": "No data provided"}, 400
            
        meeting_id = data.get('meeting_id')
        student_id = data.get('student_id')
        hand_data = data.get('hand_data')
        scan_type = data.get('type')  # 'check_in' or 'check_out'
        
        if not all([meeting_id, student_id, hand_data, scan_type]):
            return {"message": "Missing required fields"}, 400
            
        # Process hand image
        features, error = process_hand_image(hand_data)
        if error:
            return {"message": error}, 400
            
        # Mark attendance
        attendance, error = attendance_service.mark_attendance(
            meeting_id=int(meeting_id),
            student_id=int(student_id),
            scan_type=scan_type
        )
        
        if error:
            return {"message": error}, 400
            
        return {
            "message": "Attendance marked successfully",
            "attendance": {
                "id": attendance.id,
                "check_in_time": attendance.check_in_time.strftime('%Y-%m-%d %H:%M:%S') if attendance.check_in_time else None,
                "check_out_time": attendance.check_out_time.strftime('%Y-%m-%d %H:%M:%S') if attendance.check_out_time else None,
                "status": attendance.status
            }
        }, 200
        
    except Exception as e:
        return {"message": str(e)}, 500
