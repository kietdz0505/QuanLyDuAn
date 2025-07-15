from libraryapp import app, db
from libraryapp.models import User, UserRole
import hashlib

# Hàm mã hóa password
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

def create_tables():
    db.create_all()

    # Tạo admin mặc định nếu chưa có
    if not User.query.filter_by(username='admin').first():
        admin_user = User(
            name='Administrator',
            username='admin',
            password=hash_password('admin123'),
            email='admin@gmail.com',
            user_role=UserRole.ADMIN
        )
        db.session.add(admin_user)
        db.session.commit()
        print("✅ Đã tạo tài khoản admin: admin / admin123")

if __name__ == '__main__':
    with app.app_context():
        create_tables()
