from flask import Flask
from flask_cors import CORS
import os

from src.database.api.controllers.auth_controller import auth_bp
from src.database.api.controllers.course_controller import course_bp
from src.database.api.controllers.class_controller import class_bp
from src.database.api.controllers.class_student_controller import class_student_bp
from src.database.api.controllers.meeting_controller import meeting_bp
from src.database.api.controllers.attendance_controller import attendance_bp
from src.database.api.controllers.hand_scan_controller import hand_scan_bp
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

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(class_bp)
    app.register_blueprint(class_student_bp)
    app.register_blueprint(meeting_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(hand_scan_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(admin_history_bp)
    app.register_blueprint(user_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8000, debug=True)
