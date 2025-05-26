from flask import Blueprint, request, jsonify
import os
from werkzeug.utils import secure_filename
from src.database.api.services import hand_scan_service
from src.utils.jwt_helper import admin_required
from src.database.config import SessionLocal
from src.database.models import Course, Class, Meeting, User
from datetime import datetime
import logging
import traceback

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hand_scan_controller.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

UPLOAD_FOLDER = 'src/storage/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

hand_scan_bp = Blueprint('hand_scan', __name__, url_prefix='/api')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_active_meeting(course_id):
    """Get active meeting for the given course"""
    db = SessionLocal()
    try:
        # Get current date and time
        now = datetime.now()
        current_time = now.strftime('%H:%M')
        current_date = now.date()

        # Find active meeting
        meeting = db.query(Meeting).join(Class).join(Course).filter(
            Course.id == course_id,
            Meeting.date == current_date,
            Meeting.start_time <= current_time,
            Meeting.end_time >= current_time
        ).first()

        if not meeting:
            logger.warning(f"No active meeting found for course_id: {course_id}")
            return None

        logger.info(f"Found active meeting: {meeting.id} for course: {course_id}")
        return meeting

    except Exception as e:
        logger.error(f"Error getting active meeting: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None
    finally:
        db.close()

@hand_scan_bp.route('/scan-hand', methods=['POST'])
def scan_hand():
    logger.info("Received hand scan request")
    
    try:
        if 'image' not in request.files:
            logger.warning("No image file provided in request")
            return jsonify({
                "success": False,
                "message": "No image file provided",
                "error": "MISSING_IMAGE_FILE"
            }), 400
        
        file = request.files['image']
        meeting_id = request.form.get('meeting_id')
        scan_type = request.form.get('scan_type', 'in')  # Default to 'in' if not specified
        
        if not meeting_id:
            logger.warning("Meeting ID not provided in request")
            return jsonify({
                "success": False,
                "message": "Meeting ID is required",
                "error": "MISSING_MEETING_ID"
            }), 400
        
        if scan_type not in ['in', 'out']:
            logger.warning(f"Invalid scan type: {scan_type}")
            return jsonify({
                "success": False,
                "message": "Scan type must be either 'in' or 'out'",
                "error": "INVALID_SCAN_TYPE"
            }), 400
        
        if file.filename == '':
            logger.warning("Empty filename provided")
            return jsonify({
                "success": False,
                "message": "No selected file",
                "error": "EMPTY_FILENAME"
            }), 400

        if not (file and allowed_file(file.filename)):
            logger.warning(f"Invalid file type: {file.filename}")
            return jsonify({
                "success": False,
                "message": "Tipe file tidak valid",
                "error": "INVALID_FILE_TYPE"
            }), 400

        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        logger.info(f"Processing file: {filename}")

        # Buat direktori jika belum ada
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        

        file.save(file_path)
        logger.info(f"File saved successfully at: {file_path}")

        # Prediksi pemilik telapak tangan
        student_id, confidence, error = hand_scan_service.predict_hand_owner(file_path)
        if error:
            os.remove(file_path)
            return jsonify({
                "success": False,
                "message": f"{error}",
                "error": "HAND_PREDICTION_ERROR"
            }), 400

        # Hapus file setelah prediksi
        os.remove(file_path)

        if student_id is None:
            return jsonify({
                "success": False,
                "message": "Telapak tangan tidak dikenali",
                "error": "HAND_NOT_RECOGNIZED",
                "confidence": float(confidence)
            }), 404

        # Record kehadiran
        attendance, error = hand_scan_service.record_attendance(student_id, meeting_id, scan_type)
        if error:
            return jsonify({
                "success": False,
                "message": f"{error}",
                "error": "ATTENDANCE_ERROR"
            }), 400

        # Get student name
        db = SessionLocal()
        student = db.query(User).filter(User.id == student_id).first()
        student_name = student.name if student else "Mahasiswa"
        db.close()

        tipe_scan = 'check-out' if scan_type == 'out' else 'check-in'

        return jsonify({
            "success": True,
            "message": f"{student_name} berhasil {tipe_scan}",
            "data": {
                "student_id": student_id,
                "student_name": student_name,
                "confidence": float(confidence),
                "meeting_id": meeting_id,
                "attendance_id": attendance.id,
                "scan_type": scan_type
            }
        }), 200

    except Exception as e:
        logger.error(f"Unexpected error processing hand scan: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({
            "success": False,
            "message": "Terjadi kesalahan tidak terduga saat memproses scan",
            "error": "UNEXPECTED_ERROR",
            "details": str(e)
        }), 500