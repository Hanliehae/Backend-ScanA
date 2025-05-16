from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import os
import json
import numpy as np
import tensorflow as tf
from datetime import datetime
import cv2
import base64


from src.database.api.controllers.auth_controller import auth_bp
from src.database.api.controllers.course_controller import course_bp
from src.database.api.controllers.class_controller import class_bp
from src.database.api.controllers.class_student_controller import class_student_bp
from src.database.api.controllers.meeting_controller import meeting_bp
from src.database.api.controllers.attendance_controller import attendance_bp
# from src.database.api.controllers.hand_scan_controller import hand_scan_bp
from src.database.api.controllers.history_controller import history_bp
from src.database.api.controllers.admin_history_controller import admin_history_bp
from src.database.api.controllers.user_controller import user_bp


def create_app():
    app = Flask(__name__)
    CORS(app, resources={
        r"/api/*": {
            "origins": ["*"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    app.register_blueprint(auth_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(class_bp)
    app.register_blueprint(class_student_bp)
    app.register_blueprint(meeting_bp)
    app.register_blueprint(attendance_bp)
    # app.register_blueprint(hand_scan_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(admin_history_bp)
    app.register_blueprint(user_bp)

    # Path ke model CNN
    MODEL_DIR = 'src/ml_models'
    MODEL_PATH = os.path.join(MODEL_DIR, 'hand_recognition_model.h5')

    # Load model saat startup
    model = None
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        print("Model loaded successfully")
    except Exception as e:
        print(f"Error loading model: {e}")

    def preprocess_image(image_data):
        try:
            # Decode base64 image
            nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Convert BGR to RGB (OpenCV uses BGR by default)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Apply Gaussian blur to reduce noise while preserving color
            blurred = cv2.GaussianBlur(img, (5, 5), 0)
            
            # Create a mask using color thresholding
            # Convert to HSV for better color segmentation
            hsv = cv2.cvtColor(blurred, cv2.COLOR_RGB2HSV)
            
            # Define range for skin color in HSV
            lower_skin = np.array([0, 20, 70], dtype=np.uint8)
            upper_skin = np.array([20, 255, 255], dtype=np.uint8)
            
            # Create mask for skin color
            mask = cv2.inRange(hsv, lower_skin, upper_skin)
            
            # Apply morphological operations to clean up the mask
            kernel = np.ones((5,5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(
                mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Find the largest contour (assumed to be the palm)
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(largest_contour)
                
                # Extract palm region with padding
                padding = 20
                x1 = max(0, x - padding)
                y1 = max(0, y - padding)
                x2 = min(img.shape[1], x + w + padding)
                y2 = min(img.shape[0], y + h + padding)
                
                palm_region = img[y1:y2, x1:x2]
                
                # Resize to standard size
                palm_region = cv2.resize(palm_region, (224, 224))
                
                return palm_region
            return img
            
        except Exception as e:
            print(f"Error in preprocessing: {e}")
            return img

    def augment_image(image):
        augmented_images = []
        
        # Original image
        augmented_images.append(image)
        
        # Rotation
        for angle in [-15, 15]:
            matrix = cv2.getRotationMatrix2D(
                (image.shape[1]/2, image.shape[0]/2), angle, 1.0
            )
            rotated = cv2.warpAffine(image, matrix, (image.shape[1], image.shape[0]))
            augmented_images.append(rotated)
        
        # Brightness adjustment (preserving color)
        for alpha in [0.8, 1.2]:  # alpha < 1: darker, alpha > 1: brighter
            bright = cv2.convertScaleAbs(image, alpha=alpha, beta=0)
            augmented_images.append(bright)
        
        # Color jittering (slight color variations)
        for beta in [-10, 10]:  # beta < 0: less saturated, beta > 0: more saturated
            hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
            hsv[:,:,1] = cv2.add(hsv[:,:,1], beta)  # Adjust saturation
            jittered = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
            augmented_images.append(jittered)
        
        return augmented_images

    @app.route('/api/model/metadata', methods=['GET'])
    def get_model_metadata():
        try:
            with open(MODEL_METADATA, 'r') as f:
                model_data = json.load(f)
            return jsonify(model_data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/model/weights', methods=['GET'])
    def get_model_weights():
        try:
            return send_file(
                MODEL_WEIGHTS,
                mimetype='application/octet-stream',
                as_attachment=True,
                download_name='weights.bin'
            )
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/detect', methods=['POST'])
    def detect_palm():
        try:
            data = request.json
            image_data = data.get('image')
            
            if not image_data:
                return jsonify({'error': 'No image data provided'}), 400
            
            # Preprocess image
            processed_image = preprocess_image(image_data)
            
            # Make prediction
            prediction = model.predict(processed_image)
            confidence = float(prediction[0][0])
            is_palm = confidence > 0.5
            
            return jsonify({
                'isPalm': bool(is_palm),
                'confidence': confidence,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/attendance', methods=['POST'])
    def process_attendance():
        try:
            data = request.json
            meeting_id = data.get('meeting_id')
            student_id = data.get('student_id')
            scan_type = data.get('type', 'in')  # Default to 'in' if not specified
            
            if not all([meeting_id, student_id]):
                return jsonify({'error': 'Missing required fields'}), 400
            
            # Use the attendance service to mark attendance
            attendance, error = attendance_service.mark_attendance(
                meeting_id=int(meeting_id),
                student_id=int(student_id),
                scan_type=scan_type
            )
            
            if error:
                return jsonify({'error': error}), 400
            
            return jsonify({
                'status': 'success',
                'message': 'Attendance recorded successfully',
                'data': {
                    'id': attendance.id,
                    'check_in_time': attendance.check_in_time.strftime('%Y-%m-%d %H:%M:%S') if attendance.check_in_time else None,
                    'check_out_time': attendance.check_out_time.strftime('%Y-%m-%d %H:%M:%S') if attendance.check_out_time else None,
                    'status': attendance.status
                }
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/training/collect', methods=['POST'])
    def collect_training_data():
        try:
            data = request.json
            user_id = data.get('userId')
            image_data = data.get('image')
            
            if not user_id or not image_data:
                return jsonify({'error': 'Missing user ID or image data'}), 400
            
            # Preprocess image
            processed_image = preprocess_image(image_data)
            
            # Create directory for user's training data if not exists
            user_dir = os.path.join('training_data', str(user_id))
            os.makedirs(user_dir, exist_ok=True)
            
            # Save original processed image
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_path = os.path.join(user_dir, f'palm_{timestamp}.jpg')
            cv2.imwrite(image_path, processed_image)
            
            # Generate and save augmented images
            augmented_images = augment_image(processed_image)
            for i, aug_img in enumerate(augmented_images):
                aug_path = os.path.join(user_dir, f'palm_{timestamp}_aug_{i}.jpg')
                cv2.imwrite(aug_path, aug_img)
            
            return jsonify({
                'status': 'success',
                'message': 'Training data collected and augmented successfully',
                'data': {
                    'userId': user_id,
                    'timestamp': timestamp,
                    'originalImage': image_path,
                    'augmentedCount': len(augmented_images)
                }
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/training/status/<user_id>', methods=['GET'])
    def get_training_status(user_id):
        try:
            user_dir = os.path.join('training_data', str(user_id))
            if not os.path.exists(user_dir):
                return jsonify({
                    'status': 'not_started',
                    'message': 'No training data collected yet',
                    'data': {
                        'userId': user_id,
                        'imageCount': 0
                    }
                })
            
            # Count collected images
            image_count = len([f for f in os.listdir(user_dir) if f.endswith('.jpg')])
            
            return jsonify({
                'status': 'in_progress' if image_count < 5 else 'completed',
                'message': f'Collected {image_count} training images',
                'data': {
                    'userId': user_id,
                    'imageCount': image_count,
                    'requiredCount': 5
                }
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8000, debug=True)
