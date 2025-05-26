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
            
            # Log model summary
            logger.info("Model Summary:")
            model.summary(print_fn=logger.info)
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
        logger.info("Starting hand owner prediction")
        if model is None:
            logger.error("Model not loaded, cannot make prediction")
            return None, 0.0
        # Preprocess image
        logger.info("Preprocessing image for prediction")
        img_array = preprocess_image(image)
        if img_array is None:
            logger.error("Image preprocessing failed")
            return None, 0.0
        # Make prediction
        logger.info("Making prediction with model")
        predictions = model.predict(img_array, verbose=0)
        logger.info(f"Raw predictions shape: {predictions.shape}")
        logger.info(f"Raw predictions: {predictions}")
        # Get the highest confidence prediction
        predicted_class = int(np.argmax(predictions[0]))  # Convert to Python int
        confidence = float(predictions[0][predicted_class])
        
        logger.info(f"Predicted class: {predicted_class} with confidence: {confidence:.4f}")
        # Check if confidence is high enough
        if confidence < 0.2:  # 20% confidence threshold
            logger.warning(f"Confidence too low: {confidence:.4f}")
            return None, confidence

        # Get user with matching hand_scan_class_index
        logger.info("Creating new database session for user lookup")
        db = SessionLocal()
        try:
            logger.info(f"Looking for user with hand_scan_class_index: {predicted_class}")
            user = db.query(User).filter(
                User.hand_scan_class_index == predicted_class
            ).first()
            
            if not user:
                logger.warning(f"No user found with hand_scan_class_index: {predicted_class}")
                return None, confidence
            logger.info(f"Found matching user: {user.name} (ID: {user.id})")
            return user.id, confidence
        finally:
            logger.info("Closing database session after user lookup")
            db.close()
    except Exception as e:
        logger.error(f"Error in predict_hand_owner: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None, 0.0
    
def record_attendance(user_id, meeting_id, scan_type='in'):
    logger.info("Creating new database session for attendance recording")
    db = SessionLocal()
    try:
        logger.info(f"Starting attendance recording process for user_id: {user_id}, meeting_id: {meeting_id}, scan_type: {scan_type}")
        
        # 1. Check if user exists
        logger.info(f"Checking if user exists with id: {user_id}")
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User not found with id: {user_id}")
            return None
        logger.info(f"Found user: {user.name} (ID: {user.id})")
        
        # 2. Check if meeting exists
        logger.info(f"Checking if meeting exists with id: {meeting_id}")
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting:
            logger.error(f"Meeting not found: {meeting_id}")
            return None
        logger.info(f"Found meeting: {meeting.id} for class_id: {meeting.class_id}")
        
        # 3. Get class_student record
        logger.info(f"Looking for class_student record for student {user.name} in class {meeting.class_id}")
        class_student = db.query(ClassStudent).filter(
            ClassStudent.student_id == user_id,
            ClassStudent.class_id == meeting.class_id
        ).first()
        if not class_student:
            logger.error(f"Student {user.name} (ID: {user.id}) is not enrolled in class {meeting.class_id}")
            return None
        logger.info(f"Found class_student record: {class_student.id}")
        
        # 4. Check if attendance already exists
        logger.info(f"Checking for existing attendance record")
        existing_attendance = db.query(Attendance).filter(
            Attendance.meeting_id == meeting_id,
            Attendance.class_student_id == class_student.id
        ).first()

        current_time = datetime.now()

        if existing_attendance:
            logger.info(f"Found existing attendance record: {existing_attendance.id}")
            
            if scan_type == 'in':
                if existing_attendance.check_in_time:
                    logger.warning("Student already checked in")
                    return None
                logger.info("Recording check-in time")
                existing_attendance.check_in_time = current_time
                existing_attendance.status = "Hadir"
            else:  # scan_type == 'out'
                if not existing_attendance.check_in_time:
                    logger.warning("Student has not checked in yet")
                    return None
                if existing_attendance.check_out_time:
                    logger.warning("Student already checked out")
                    return None
                logger.info("Recording check-out time")
                existing_attendance.check_out_time = current_time
            
            logger.info("Committing attendance update to database")
            db.commit()
            logger.info(f"Successfully updated attendance record: {existing_attendance.id}")
            return existing_attendance
        
        # 5. Create new attendance record for check-in
        if scan_type == 'out':
            logger.warning("Cannot check out without checking in first")
            return None
            
        logger.info("Creating new attendance record for check-in")
        attendance = Attendance(
            class_student_id=class_student.id,
            meeting_id=meeting_id,
            check_in_time=current_time,
            status="Hadir"
        )
        logger.info("Adding new attendance record to database")
        db.add(attendance)
        logger.info("Committing new attendance record to database")
        db.commit()
        logger.info(f"Successfully created new attendance record: {attendance.id}")
        return attendance
    except Exception as e:
        logger.error(f"Error in record_attendance: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        logger.info("Rolling back database transaction due to error")
        db.rollback()
        return None
    finally:
        logger.info("Closing database session after attendance recording")
        db.close()