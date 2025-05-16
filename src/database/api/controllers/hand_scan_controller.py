from flask import Blueprint, request, jsonify
import os
from werkzeug.utils import secure_filename
from src.database.api.services.hand_scan_service import HandScanService
from src.database.database import get_db
from src.utils.jwt_helper import student_required

UPLOAD_FOLDER = 'src/storage/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

hand_scan_bp = Blueprint('hand_scan', __name__, url_prefix='/api/hand-scan')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@hand_scan_bp.route('/scan-palm', methods=['POST'])
@student_required
def scan_palm():
    if 'image' not in request.files:
        return jsonify({
            "success": False,
            "message": "No image file provided"
        }), 400
    
    file = request.files['image']
    course_id = request.form.get('course_id')
    
    if not course_id:
        return jsonify({
            "success": False,
            "message": "Course ID is required"
        }), 400
    
    if file.filename == '':
        return jsonify({
            "success": False,
            "message": "No selected file"
        }), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        # Buat direktori jika belum ada
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file.save(file_path)

        try:
            # Inisialisasi service
            db = next(get_db())
            service = HandScanService(db)

            # Cek meeting aktif
            meeting = service.get_active_meeting(course_id)
            if not meeting:
                return jsonify({
                    "success": False,
                    "message": "Tidak ada pertemuan aktif untuk mata kuliah ini"
                }), 400

            # Prediksi pemilik telapak tangan
            student_id, confidence = service.predict_hand_owner(file_path)

            # Hapus file setelah prediksi
            os.remove(file_path)

            if student_id is None:
                return jsonify({
                    "success": False,
                    "message": "Telapak tangan tidak dikenali"
                }), 404

            # Record kehadiran
            success, message = service.record_attendance(student_id, meeting.id)

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
            # Hapus file jika terjadi error
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({
                "success": False,
                "message": f"Terjadi kesalahan: {str(e)}"
            }), 500

    return jsonify({
        "success": False,
        "message": "Tipe file tidak valid"
    }), 400
