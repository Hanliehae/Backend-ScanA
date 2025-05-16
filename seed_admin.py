# seed_admin.py

from src.database.config import SessionLocal
from src.database.models import User
from werkzeug.security import generate_password_hash


def seed_admin():
    db = SessionLocal()
    try:
        existing_admin = db.query(User).filter(
            User.username == 'admin').first()
        if existing_admin:
            print("Admin user already exists.")
        else:
            admin_user = User(
                username='admin',
                password_hash=generate_password_hash(
                    'admin123', method='pbkdf2:sha256'),
                name='Admin',
                nim=None,       # boleh None karena nullable
                email='admin@example.com',  # HARUS ISI karena NOT NULL dan UNIQUE
                phone=None,
                hand_left_path=None,
                hand_right_path=None,
                role='admin'
            )
            db.add(admin_user)
            db.commit()
            print("Admin user created successfully.")
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()
