from flask import Blueprint, request
from src.database.api.services import auth_service
from src.utils.jwt_helper import login_required, admin_required
import os
import uuid

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    token, error = auth_service.login(username, password)
    if error:
        return {"message": error}, 401

    return {"access_token": token}, 200


@auth_bp.route('/register-student', methods=['POST'])
@admin_required
def register_student():
    nim = request.form.get('nim')
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')

    hand_left = request.files.get('hand_left')
    hand_right = request.files.get('hand_right')

    if not hand_left or not hand_right:
        return {"message": "Both hand_left and hand_right images are required"}, 400

    # Simpan file upload
    left_filename = f"{nim}_left_{uuid.uuid4().hex}.jpg"
    right_filename = f"{nim}_right_{uuid.uuid4().hex}.jpg"

    left_path = os.path.join(f'storage/hands/{nim}/left', left_filename)
    right_path = os.path.join(f'storage/hands/{nim}/right', right_filename)

    # Pastikan foldernya ada
    os.makedirs(os.path.dirname(left_path), exist_ok=True)
    os.makedirs(os.path.dirname(right_path), exist_ok=True)

    hand_left.save(left_path)
    hand_right.save(right_path)

    # Daftarkan mahasiswa
    result, error = auth_service.register_student(
        nim, name, email, phone, hand_left_path=left_path, hand_right_path=right_path
    )

    if error:
        return {"message": error}, 400

    return {"message": "Student registered successfully", "credentials": result}, 201
