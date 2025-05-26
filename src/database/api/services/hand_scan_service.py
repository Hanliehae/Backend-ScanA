import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from ...models import User, Attendance, Meeting, Class, ClassStudent
from src.database.config import SessionLocal
from datetime import datetime
import os
import logging
import json
import traceback

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hand_scan.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Global variable for model
model = None

def load_hand_model():
    global model
    try:
        logger.info("Starting model loading process")
        model_path = os.path.join('src', 'storage', 'models', 'hand_recognition_model.h5')
        logger.info(f"Looking for model at: {model_path}")
        
        if os.path.exists(model_path):
            logger.info("Model file found, attempting to load")
            # Load model dengan custom_objects untuk menangani kompatibilitas
            custom_objects = {
                'MobileNetV2': tf.keras.applications.MobileNetV2,
                'relu6': tf.keras.layers.ReLU(6.0),
            }
            
            # Load model dengan custom_objects dan compile=False
            model = tf.keras.models.load_model(
                model_path,
                custom_objects=custom_objects,
                compile=False
            )
            logger.info("Model loaded successfully")
            
            # # Log model summary
            # logger.info("Model Summary:")
            # model.summary(print_fn=logger.info)
        else:
            logger.error(f"Model file not found at: {model_path}")
            model = None
            
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        model = None

# Load model saat modul diimpor
load_hand_model()

def preprocess_image(image):
    try:
        logger.info("Starting image preprocessing")
        if isinstance(image, str):
            logger.info(f"Processing image from path: {image}")
            img = cv2.imread(image)
            if img is None:
                logger.error(f"Failed to read image file: {image}")
                raise ValueError(f"Could not read image file: {image}")
        else:
            logger.info("Processing image from numpy array")
            img = image.copy()
        
        # Log image properties
        logger.info(f"Original image shape: {img.shape}")
        
        # Konversi BGR ke RGB
        logger.info("Converting BGR to RGB")
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Resize ke ukuran yang diharapkan model
        logger.info("Resizing image to 224x224")
        img = cv2.resize(img, (224, 224))
        
        # Normalisasi
        logger.info("Normalizing image values")
        img = img / 255.0
        
        # Tambahkan dimensi batch
        logger.info("Adding batch dimension")
        img = np.expand_dims(img, axis=0)
        
        logger.info(f"Preprocessed image shape: {img.shape}")
        return img
            
    except Exception as e:
        logger.error(f"Error in preprocess_image: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None
    
def predict_hand_owner(image):
    global model
    try:
        if model is None:
            return None, 0.0, "Model not loaded"
            
        img_array = preprocess_image(image)
        if img_array is None:
            return None, 0.0, "Gagal memproses gambar"
            
        predictions = model.predict(img_array, verbose=0)
        predicted_class = int(np.argmax(predictions[0]))
        confidence = float(predictions[0][predicted_class])
        
        if confidence < 0.3:
            return None, confidence, f"Tingkat kepercayaan terlalu rendah: {confidence}"
            
        db = SessionLocal()
        user = db.query(User).filter(
            User.hand_scan_class_index == predicted_class
        ).first()
        db.close()
        
        if not user:
            return None, confidence, "Pengguna tidak ditemukan"
            
        return user.id, confidence, None
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return None, 0.0, f"Kesalahan prediksi: {str(e)}"

def record_attendance(user_id, meeting_id, scan_type='in'):
    try:
        db = SessionLocal()
        
        # Check user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            db.close()
            return None, "Mahasiswa tidak ditemukan"
            
        # Check meeting
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting:
            db.close()
            return None, "Pertemuan tidak ditemukan"
            
        # Check class enrollment
        class_student = db.query(ClassStudent).filter(
            ClassStudent.student_id == user_id,
            ClassStudent.class_id == meeting.class_id
        ).first()
        if not class_student:
            db.close()
            return None, f"{user.name} tidak terdaftar di kelas ini"
            
        current_time = datetime.now()
        existing_attendance = db.query(Attendance).filter(
            Attendance.meeting_id == meeting_id,
            Attendance.class_student_id == class_student.id
        ).first()

        if existing_attendance:
            if scan_type == 'in':
                if existing_attendance.check_in_time:
                    db.close()
                    return None, f"{user.name} sudah melakukan check-in sebelumnya"
                existing_attendance.check_in_time = current_time
                existing_attendance.status = "Hadir"
            else:
                if not existing_attendance.check_in_time:
                    db.close()
                    return None, f"{user.name} belum check-in"
                if existing_attendance.check_out_time:
                    db.close()
                    return None, f"{user.name} sudah melakukan check-out sebelumnya"
                existing_attendance.check_out_time = current_time
            
            db.commit()
            db.close()
            return existing_attendance, None
        
        if scan_type == 'out':
            db.close()
            return None, "Tidak bisa check-out sebelum check-in"
            
        attendance = Attendance(
            class_student_id=class_student.id,
            meeting_id=meeting_id,
            check_in_time=current_time,
            status="Hadir"
        )
        db.add(attendance)
        db.commit()
        db.close()
        return attendance, None
        
    except Exception as e:
        logger.error(f"Attendance error: {str(e)}")
        if 'db' in locals():
            db.rollback()
            db.close()
        return None, f"Kesalahan database: {str(e)}"