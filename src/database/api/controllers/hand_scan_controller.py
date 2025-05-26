from flask import Blueprint, request, jsonify
import os
from werkzeug.utils import secure_filename
from src.database.api.services import hand_scan_service
from src.utils.jwt_helper import admin_required
from src.database.config import SessionLocal
from src.database.models import Course, Class, Meeting
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
    
    if 'image' not in request.files:
        logger.warning("No image file provided in request")
        return jsonify({
            "success": False,
            "message": "No image file provided"
        }), 400
    
    file = request.files['image']
    course_id = request.form.get('course_id')
    scan_type = request.form.get('scan_type')  # Default to 'in' if not specified
    
    if not course_id:
        logger.warning("Course ID not provided in request")
        return jsonify({
            "success": False,
            "message": "Course ID is required"
        }), 400
    
    if scan_type not in ['in', 'out']:
        logger.warning(f"Invalid scan type: {scan_type}")
        return jsonify({
            "success": False,
            "message": "Scan type must be either 'in' or 'out'"
        }), 400
    
    if file.filename == '':
        logger.warning("Empty filename provided")
        return jsonify({
            "success": False,
            "message": "No selected file"
        }), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        logger.info(f"Processing file: {filename}")

        # Buat direktori jika belum ada
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        logger.info(f"Ensuring upload directory exists: {UPLOAD_FOLDER}")
        
        try:
            # Get active meeting for the course
            meeting = get_active_meeting(int(course_id))
            if not meeting:
                return jsonify({
                    "success": False,
                    "message": "Tidak ada pertemuan aktif untuk mata kuliah ini"
                }), 400

            file.save(file_path)
            logger.info(f"File saved successfully at: {file_path}")

            # Prediksi pemilik telapak tangan
            logger.info("Starting hand owner prediction")
            student_id, confidence = hand_scan_service.predict_hand_owner(file_path)
            logger.info(f"Prediction result - Student ID: {student_id}, Confidence: {confidence}")

            # Hapus file setelah prediksi
            os.remove(file_path)
            logger.info(f"Temporary file removed: {file_path}")

            if student_id is None:
                logger.warning("Hand not recognized in the image")
                return jsonify({
                    "success": False,
                    "message": "Telapak tangan tidak dikenali"
                }), 404

            # Record kehadiran
            logger.info(f"Recording attendance for student_id: {student_id} with scan_type: {scan_type}")
            attendance = hand_scan_service.record_attendance(student_id, meeting.id, scan_type)
            
            if attendance is None:
                logger.error("Failed to record attendance")
                return jsonify({
                    "success": False,
                    "message": "Gagal mencatat kehadiran"
                }), 400

            return jsonify({
                "success": True,
                "message": f"Kehadiran {scan_type} berhasil dicatat",
                "data": {
                    "student_id": student_id,
                    "confidence": confidence,
                    "meeting_id": meeting.id,
                    "attendance_id": attendance.id,
                    "scan_type": scan_type
                }
            }), 200

        except Exception as e:
            logger.error(f"Error processing hand scan: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Hapus file jika terjadi error
            if os.path.exists(file_path):
                logger.info(f"Removing file after error: {file_path}")
                os.remove(file_path)
            return jsonify({
                "success": False,
                "message": "Terjadi kesalahan saat memproses scan"
            }), 500

    logger.warning(f"Invalid file type: {file.filename}")
    return jsonify({
        "success": False,
        "message": "Tipe file tidak valid"
    }), 400
