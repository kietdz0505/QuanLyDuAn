from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary
from urllib.parse import quote

# Tạo app với template_folder trỏ về thư mục templates cùng cấp
app = Flask(__name__, template_folder='../templates')
app.secret_key = '@dhuhuigugsusrbfberbđsdfghjkjghrg4'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:%s@localhost/librarydb?charset=utf8mb4' % quote("Admin@123")
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = True
app.config['PAGE_SIZE'] = 8
app.config['COMMENT_SIZE'] = 20

db = SQLAlchemy(app=app)

cloudinary.config(
    cloud_name = 'dfgnoyf71',
    api_key = '993678569624556',
    api_secret ='coCHzmBGd-KVX1ZJxbecKfrETog',
)

login = LoginManager(app=app)