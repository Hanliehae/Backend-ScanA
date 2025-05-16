# import numpy as np
# import tensorflow as tf
# from PIL import Image
# import os

# # Load model saat pertama kali
# model_path = os.path.join('src', 'storage', 'models',
#                           'hand_recognition_model.h5')
# model = tf.keras.models.load_model(model_path)

# # Mapping ID hasil prediksi ke student_id
# # Note: Ini dummy, nanti idealnya mapping ini di database
# student_mapping = {
#     0: 1,  # id student 1
#     1: 2,  # id student 2
#     # dst
# }


# def preprocess_image(image_path):
#     img = Image.open(image_path).convert('RGB')
#     img = img.resize((224, 224))  # menyesuaikan ukuran input model
#     img_array = np.array(img) / 255.0  # normalisasi
#     img_array = np.expand_dims(img_array, axis=0)  # batch dimension
#     return img_array


# def predict_hand_owner(image_path):
#     img_array = preprocess_image(image_path)

#     predictions = model.predict(img_array)
#     predicted_class = np.argmax(predictions[0])

#     student_id = student_mapping.get(predicted_class, None)
#     confidence = float(np.max(predictions[0]))

#     return student_id, confidence

import cv2
import numpy as np
import tensorflow as tf
from src.database.models import Student, Attendance, Meeting
from sqlalchemy.orm import Session
from datetime import datetime
import os

class HandScanService:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.model = self._load_model()
        
    def _load_model(self):
        # Load model TensorFlow yang sudah dilatih
        # Untuk sementara, kita gunakan model sederhana
        model_path = os.path.join(os.path.dirname(__file__), '../../../ml_models/palm_detection_model')
        try:
            return tf.keras.models.load_model(model_path)
        except:
            # Jika model belum ada, return None
            return None

    def preprocess_image(self, image_path):
        # Baca gambar
        img = cv2.imread(image_path)
        if img is None:
            return None

        # Resize gambar
        img = cv2.resize(img, (224, 224))
        
        # Konversi ke RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Normalisasi
        img = img / 255.0
        
        return img

    def predict_hand_owner(self, image_path):
        try:
            # Preprocess gambar
            img = self.preprocess_image(image_path)
            if img is None:
                return None, 0

            # Jika model belum ada, gunakan deteksi sederhana
            if self.model is None:
                # Implementasi deteksi sederhana menggunakan OpenCV
                return self._simple_detection(img)
            
            # Prediksi menggunakan model
            img = np.expand_dims(img, axis=0)
            predictions = self.model.predict(img)
            
            # Ambil prediksi dengan confidence tertinggi
            student_id = np.argmax(predictions[0])
            confidence = float(predictions[0][student_id])
            
            return student_id, confidence

        except Exception as e:
            print(f"Error in predict_hand_owner: {str(e)}")
            return None, 0

    def _simple_detection(self, img):
        """
        Implementasi deteksi sederhana menggunakan OpenCV
        Ini hanya contoh, sebaiknya gunakan model yang sudah dilatih
        """
        # Konversi ke grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        
        # Deteksi tepi
        edges = cv2.Canny(gray, 100, 200)
        
        # Hitung jumlah pixel tepi
        edge_count = np.sum(edges > 0)
        
        # Jika jumlah tepi dalam range tertentu, anggap sebagai telapak tangan
        if 10000 < edge_count < 50000:
            # Untuk testing, return student_id 1 dengan confidence 0.8
            return 1, 0.8
        
        return None, 0

    def record_attendance(self, student_id, meeting_id):
        try:
            # Cek apakah sudah ada record kehadiran
            existing_attendance = self.db.query(Attendance).filter(
                Attendance.student_id == student_id,
                Attendance.meeting_id == meeting_id
            ).first()

            if existing_attendance:
                return False, "Sudah melakukan absensi"

            # Buat record kehadiran baru
            attendance = Attendance(
                student_id=student_id,
                meeting_id=meeting_id,
                time_in=datetime.now(),
                status="Hadir"
            )
            
            self.db.add(attendance)
            self.db.commit()
            
            return True, "Absensi berhasil"

        except Exception as e:
            self.db.rollback()
            return False, str(e)

    def get_active_meeting(self, course_id):
        try:
            current_time = datetime.now()
            meeting = self.db.query(Meeting).filter(
                Meeting.course_id == course_id,
                Meeting.start_time <= current_time,
                Meeting.end_time >= current_time
            ).first()
            
            return meeting
        except Exception as e:
            print(f"Error in get_active_meeting: {str(e)}")
            return None
