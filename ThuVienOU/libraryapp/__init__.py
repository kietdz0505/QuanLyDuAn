from flask import Flask
from urllib.parse import quote
import cloudinary
from libraryapp.extensions import db, login_manager
from libraryapp.models import User
from flask_mail import Mail

# Khởi tạo các extension trước (chưa gắn app)
mail = Mail()


def create_app():
    app = Flask(__name__, template_folder='../templates')
    app.secret_key = 'YOUR_SECRET_KEY'  # Thay bằng một chuỗi bí mật thực sự

    # Database config
    app.config['SQLALCHEMY_DATABASE_URI'] = ({'YOUR_DB_USER'} + ':' +
                                             quote('YOUR_DB_PASSWORD') + '@localhost/librarydb?charset=utf8mb4')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # App config
    app.config['PAGE_SIZE'] = 8
    app.config['COMMENT_SIZE'] = 20
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB upload limit

    # Mail config (dùng Gmail SMTP)
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = ''
    app.config['MAIL_PASSWORD'] = ''  # dùng App Password của Gmail
    app.config['MAIL_DEFAULT_SENDER'] = ''

    # Cloudinary config
    cloudinary.config(
        cloud_name='YOUR_CLOUD_NAME',
        api_key='YOUR_API_KEY',
        api_secret='YOUR_API_SECRET',
    )

    # Init extensions với app
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # Cấu hình user loader cho login_manager
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app


# Tạo app để chạy khi import trực tiếp
app = create_app()
