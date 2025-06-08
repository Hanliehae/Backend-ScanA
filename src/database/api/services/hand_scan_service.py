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
class_names = []


def load_hand_model():
    global model, class_names
    try:
        logger.info("Starting model loading process")
        model_path = os.path.join('src', 'storage', 'models', 'palm_lines_model(4dts).keras')
        logger.info(f"Looking for model at: {model_path}")
        
        if os.path.exists(model_path):
            logger.info("Model file found, attempting to load")
            # Load model dengan custom_objects untuk menangani kompatibilitas
            
            # Load model dengan custom_objects dan compile=False
            model = tf.keras.models.load_model(
                model_path
            )
            logger.info("Model loaded successfully")

            # Asumsikan model Anda memiliki informasi kelas dalam atribut
            if hasattr(model, 'class_names'):
                class_names = model.class_names

            logger.info(f"Model loaded successfully with classes: {class_names}")
            logger.info(f"Total classes: {len(class_names)}")
            
            # # Log model summary
            # logger.info("Model Summary:")
            # model.summary(print_fn=logger.info)
        else:
            logger.error(f"Model file not found at: {model_path}")
            model = None
            class_names = []
            
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        model = None
        class_names = []

# Load model saat modul diimpor
load_hand_model()

def preprocess_image(image):
    try:
        logger.info("Starting image preprocessing")
        
        # Create directory based on current date
        current_date = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        scan_dir = os.path.join('src', 'storage', 'scans', current_date)
        os.makedirs(scan_dir, exist_ok=True)
        
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        
        if isinstance(image, str):
            logger.info(f"Processing image from path: {image}")
            img = cv2.imread(image)
            if img is None:
                logger.error(f"Failed to read image file: {image}")
                raise ValueError(f"Could not read image file: {image}")
            # Save original image
            cv2.imwrite(os.path.join(scan_dir, f"{timestamp}_00_original.jpg"), img)
        else:
            logger.info("Processing image from numpy array")
            if len(image.shape) == 2:  # Grayscale
                img = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            else:
                img = image.copy()
            # Save original image
            cv2.imwrite(os.path.join(scan_dir, f"{timestamp}_00_original.jpg"), img)
        
        # Convert BGR to RGB then to Grayscale
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        cv2.imwrite(os.path.join(scan_dir, f"{timestamp}_01_rgb.jpg"), img_rgb)
        
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
        cv2.imwrite(os.path.join(scan_dir, f"{timestamp}_02_gray.jpg"), img_gray)

        # Apply CLAHE
        clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
        clahe_img = clahe.apply(img_gray)
        cv2.imwrite(os.path.join(scan_dir, f"{timestamp}_03_clahe.jpg"), clahe_img)

        # Apply Denoised
        denoised = cv2.fastNlMeansDenoising(clahe_img, None, h=15, templateWindowSize=7, searchWindowSize=21)
        cv2.imwrite(os.path.join(scan_dir, f"{timestamp}_04_clahe.jpg"), clahe_img)

        # DoG
        gauss1 = cv2.GaussianBlur(denoised, (0, 0), sigmaX=0.5)
        gauss2 = cv2.GaussianBlur(denoised, (0, 0), sigmaX=2.0)
        dog = gauss1 - gauss2
        dog = cv2.normalize(dog, None, 0, 255, cv2.NORM_MINMAX)
        cv2.imwrite(os.path.join(scan_dir, f"{timestamp}_05_DoG.jpg"), dog)
        
        # Resize
        resized = cv2.resize(dog, (224, 224), interpolation=cv2.INTER_CUBIC)
        cv2.imwrite(os.path.join(scan_dir, f"{timestamp}_06_resized.jpg"), resized)
  
        # Normalize and add batch dimension
        normalized = resized / 255.0
        img_array = np.expand_dims(normalized, axis=0)
        
        logger.info(f"Preprocessed image shape: {img_array.shape}")
        return img_array
            
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
        predicted_class = int(np.argmax(predictions))
        confidence = float(np.max(predictions))

        logger.info(f"Predicted class: {predicted_class}, Confidence: {confidence:.2f}")
        
        if confidence < 0.7:
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
            db.refresh(existing_attendance)  # Refresh attendance object before closing session
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
        db.refresh(attendance)  # Refresh attendance object before closing session
        db.close()
        return attendance, None
        
    except Exception as e:
        logger.error(f"Attendance error: {str(e)}")
        if 'db' in locals():
            db.rollback()
            db.close()
        return None, f"Kesalahan database: {str(e)}"