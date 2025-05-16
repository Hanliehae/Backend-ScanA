import jwt
from datetime import datetime, timedelta
from flask import request
from functools import wraps
from src.database.config import JWT_SECRET_KEY, JWT_ALGORITHM
from src.database.models import User
from src.database.config import SessionLocal

# jwt_helper.py


def student_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        user = request.current_user
        if user.role != "user":
            return {"message": "Student privilege required"}, 403
        return f(*args, **kwargs)
    return decorated


def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=5)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY,
                             algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        decoded_token = jwt.decode(
            token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["exp"] >= datetime.utcnow().timestamp() else None
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Decorator untuk login required


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            bearer = request.headers['Authorization']
            token = bearer.split()[1] if bearer.startswith(
                'Bearer ') else bearer

        if not token:
            return {"message": "Missing token"}, 401

        data = decode_access_token(token)
        if not data:
            return {"message": "Invalid or expired token"}, 401

        session = SessionLocal()
        user = session.query(User).filter(User.id == data["user_id"]).first()
        session.close()

        if not user:
            return {"message": "User not found"}, 404

        request.current_user = user
        return f(*args, **kwargs)
    return decorated

# Decorator untuk admin-only access


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        user = request.current_user
        if user.role != "admin":
            return {"message": "Admin privilege required"}, 403
        return f(*args, **kwargs)
    return decorated
