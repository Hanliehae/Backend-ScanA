from flask import Blueprint, request, jsonify
import os
from werkzeug.utils import secure_filename
from src.database.api.services import hand_scan_service
from src.utils.jwt_helper import admin_required
import logging

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
    
    if not course_id:
        logger.warning("Course ID not provided in request")
        return jsonify({
            "success": False,
            "message": "Course ID is required"
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
            logger.info(f"Recording attendance for student_id: {student_id}")
            success, message = hand_scan_service.record_attendance(student_id, meeting.id)
            logger.info(f"Attendance recording result - Success: {success}, Message: {message}")

            return jsonify({
                "success": success,
                "message": message,
                "data": {
                    "student_id": student_id,
                    "confidence": confidence,
                    "meeting_id": meeting.id
                }
            }), 200 if success else 400

        except Exception as e:
            logger.error(f"Error processing hand scan: {str(e)}")
            # Hapus file jika terjadi error
            if os.path.exists(file_path):
                logger.info(f"Removing file after error: {file_path}")
                os.remove(file_path)
            return jsonify({
                "success": False,
                "message": f"Terjadi kesalahan: {str(e)}"
            }), 500

    logger.warning(f"Invalid file type: {file.filename}")
    return jsonify({
        "success": False,
        "message": "Tipe file tidak valid"
    }), 400
