from flask import Blueprint, request
from src.database.api.services import user_service
from src.utils.jwt_helper import admin_required, login_required
from src.database.config import SessionLocal
from src.database.models import User

user_bp = Blueprint('user', __name__, url_prefix='/api/user')


@user_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    user = request.current_user  # Diambil dari JWT token via login_required decorator

    if not user:
        return {"message": "User not found"}, 404

    return {
        "id": user.id,
        "username": user.username,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "role": user.role.value
    }, 200


@user_bp.route('/', methods=['GET'])
@admin_required
def list_users():
    users = user_service.get_users()
    user_list = [{
        "id": u.id,
        "nim": u.nim,
        "name": u.name,
        "email": u.email,
        "phone": u.phone
    } for u in users]

    return {"users": user_list}, 200


@user_bp.route('/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    user = user_service.get_user(user_id)
    if not user:
        return {"message": "User not found"}, 404

    user_dict = {
        "id": user.id,
        "nim": user.nim,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "role": user.role.value if hasattr(user.role, 'value') else user.role,
        "username": user.username,
        "password": f"{user.name.split()[0]}{user.nim[-5:]}"
    }

    return {"user": user_dict}, 200


