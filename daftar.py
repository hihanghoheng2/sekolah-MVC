from app import app
from database import db_session
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Masukkan username dan password guru yang Anda inginkan
    username_guru = "teacher"
    password_guru = "password123"

    hashed_password = generate_password_hash(password_guru, method='pbkdf2:sha256')
    teacher_account = User(username=username_guru, password=hashed_password, role='teacher')
    
    db_session.add(teacher_account)
    db_session.commit()
    print(f"Akun guru '{username_guru}' berhasil dibuat.")