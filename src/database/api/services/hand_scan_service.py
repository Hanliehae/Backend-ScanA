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
from tensorflow.keras.models import load_model
from ...models import User, Attendance, Meeting, Class, ClassStudent
from sqlalchemy.orm import Session
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

class HandScanService:
    def __init__(self, db):
        logger.info("Initializing HandScanService")
        self.db = db
        self.model = None
        self.class_indices = None
        self.load_model()
        logger.info("HandScanService initialized")

    def load_model(self):
        try:
            logger.info("Starting model loading process")
            model_path = os.path.join('src', 'storage', 'models', 'hand_recognition_model.h5')
            logger.info(f"Looking for model at: {model_path}")
            
            if os.path.exists(model_path):
                logger.info("Model file found, attempting to load")
                # Load model dengan compile=False untuk menghindari masalah kompilasi
                self.model = load_model(model_path, compile=False)
                logger.info("Model loaded successfully without compilation")
                
                # Recompile model dengan konfigurasi yang sesuai
                logger.info("Recompiling model with configuration")
                self.model.compile(
                    optimizer='adam',
                    loss='categorical_crossentropy',
                    metrics=['accuracy']
                )
                logger.info("Model recompiled successfully")
                
                # Log model summary
                logger.info("Model Summary:")
                self.model.summary(print_fn=logger.info)
            else:
                logger.error(f"Model file not found at: {model_path}")
                self.model = None
                
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            self.model = None

    def preprocess_image(self, image):
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

    def predict_hand_owner(self, image):
        try:
            logger.info("Starting hand owner prediction")
            if self.model is None:
                logger.error("Model not loaded, cannot make prediction")
                return None, 0.0

            # Preprocess image
            logger.info("Preprocessing image for prediction")
            img_array = self.preprocess_image(image)
            if img_array is None:
                logger.error("Image preprocessing failed")
                return None, 0.0

            # Make prediction
            logger.info("Making prediction with model")
            predictions = self.model.predict(img_array, verbose=0)
            logger.info(f"Raw predictions shape: {predictions.shape}")
            logger.info(f"Raw predictions: {predictions}")

            # Get the highest confidence prediction
            predicted_class = np.argmax(predictions[0])
            confidence = float(predictions[0][predicted_class])
            
            logger.info(f"Predicted class: {predicted_class} with confidence: {confidence:.4f}")

            # Check if confidence is high enough
            if confidence < 0.2:  # 20% confidence threshold
                logger.warning(f"Confidence too low: {confidence:.4f}")
                return None, confidence

            # Get user with matching hand_scan_class_index
            logger.info(f"Looking for user with hand_scan_class_index: {predicted_class}")
            user = self.db.query(User).filter(
                User.hand_scan_class_index == predicted_class
            ).first()
            
            if not user:
                logger.warning(f"No user found with hand_scan_class_index: {predicted_class}")
                return None, confidence

            logger.info(f"Found matching user: {user.name} (ID: {user.id})")
            return user.id, confidence

        except Exception as e:
            logger.error(f"Error in predict_hand_owner: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None, 0.0

    def record_attendance(self, user_id, meeting_id):
        try:
            logger.info(f"Starting attendance recording process for user_id: {user_id}, meeting_id: {meeting_id}")
            
            # 1. Check if user exists
            logger.info(f"Checking if user exists with id: {user_id}")
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.error(f"User not found with id: {user_id}")
                return None
            logger.info(f"Found user: {user.name} (ID: {user.id})")

            # 2. Check if meeting exists
            logger.info(f"Checking if meeting exists with id: {meeting_id}")
            meeting = self.db.query(Meeting).filter(Meeting.id == meeting_id).first()
            if not meeting:
                logger.error(f"Meeting not found: {meeting_id}")
                return None
            logger.info(f"Found meeting: {meeting.id} for class_id: {meeting.class_id}")

            # 3. Get class_student record
            logger.info(f"Looking for class_student record for student {user.name} in class {meeting.class_id}")
            class_student = self.db.query(ClassStudent).filter(
                ClassStudent.student_id == user_id,
                ClassStudent.class_id == meeting.class_id
            ).first()

            if not class_student:
                logger.error(f"Student {user.name} (ID: {user.id}) is not enrolled in class {meeting.class_id}")
                return None
            logger.info(f"Found class_student record: {class_student.id}")

            # 4. Check if attendance already exists
            logger.info(f"Checking for existing attendance record")
            existing_attendance = self.db.query(Attendance).filter(
                Attendance.meeting_id == meeting_id,
                Attendance.class_student_id == class_student.id
            ).first()

            if existing_attendance:
                logger.info(f"Found existing attendance record: {existing_attendance.id}")
                # Update check_out_time if already checked in
                if existing_attendance.check_in_time and not existing_attendance.check_out_time:
                    logger.info(f"Updating check-out time for attendance: {existing_attendance.id}")
                    existing_attendance.check_out_time = datetime.now()
                    existing_attendance.status = "Hadir"
                    self.db.commit()
                    logger.info(f"Successfully updated check-out time")
                    return existing_attendance
                logger.info(f"Attendance already exists and is complete")
                return existing_attendance

            # 5. Create new attendance record
            logger.info("Creating new attendance record")
            current_time = datetime.now()
            attendance = Attendance(
                class_student_id=class_student.id,
                meeting_id=meeting_id,
                check_in_time=current_time,
                status="Hadir"
            )

            self.db.add(attendance)
            self.db.commit()
            logger.info(f"Successfully created new attendance record: {attendance.id}")

            return attendance

        except Exception as e:
            logger.error(f"Error in record_attendance: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            self.db.rollback()
            return None
