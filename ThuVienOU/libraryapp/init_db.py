from werkzeug.security import generate_password_hash
from libraryapp import create_app
from libraryapp.extensions import db
from libraryapp.models import User, UserRole

def hash_password(password):
    return generate_password_hash(password)

def create_tables():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin_user = User(
            name='Administrator',
            username='admin',
            password=hash_password('admin123'),  # Đảm bảo đã dùng scrypt
            email='admin@gmail.com',
            user_role=UserRole.ADMIN
        )
        db.session.add(admin_user)
        db.session.commit()
        print("✅ Đã tạo tài khoản admin: admin / admin123")


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        create_tables()
