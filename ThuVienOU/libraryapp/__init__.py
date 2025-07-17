from flask import Flask
from urllib.parse import quote
import cloudinary
from libraryapp.extensions import db, login_manager
from libraryapp.models import User
from libraryapp.extensions import db



def create_app():
    app = Flask(__name__, template_folder='../templates')
    app.secret_key = '@dhuhuigugsusrbfberbsdfghjkjghrg4'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:%s@localhost/librarydb?charset=utf8mb4' % quote("Admin@123")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['PAGE_SIZE'] = 8
    app.config['COMMENT_SIZE'] = 20
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

    # Cloudinary config
    cloudinary.config(
        cloud_name='dfgnoyf71',
        api_key='993678569624556',
        api_secret='coCHzmBGd-KVX1ZJxbecKfrETog',
    )

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app


app = create_app()