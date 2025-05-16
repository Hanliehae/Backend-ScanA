from werkzeug.security import generate_password_hash, check_password_hash
from src.database.models import User, RoleEnum
from src.database.config import SessionLocal
from src.utils.jwt_helper import create_access_token


def login(username, password):
    session = SessionLocal()
    user = session.query(User).filter(User.username == username).first()
    if not user:
        session.close()
        return None, "User not found"

    if not check_password_hash(user.password_hash, password):
        session.close()
        return None, "Incorrect password"

    token = create_access_token({"user_id": user.id, "role": user.role})
    session.close()
    return token, None


def register_student(nim, name, email, phone, hand_left_path=None, hand_right_path=None):
    session = SessionLocal()

    username = nim
    password_raw = f"{name.split()[0]}{nim[-5:]}"
    password_hash = generate_password_hash(password_raw)

    existing_user = session.query(User).filter(
        (User.username == username) | (User.email == email)).first()
    if existing_user:
        session.close()
        return None, "User with this username/email already exists"

    new_student = User(
        username=username,
        password_hash=password_hash,
        name=name,
        nim=nim,
        email=email,
        phone=phone,
        hand_left_path=hand_left_path,
        hand_right_path=hand_right_path,
        role=RoleEnum.user,
    )

    session.add(new_student)
    session.commit()
    session.refresh(new_student)
    session.close()

    return {
        "username": username,
        "password": password_raw
    }, None
