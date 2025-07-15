from sqlalchemy import Column, Boolean, Enum, ForeignKey, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import relationship, backref
from libraryapp import db, app
from datetime import datetime
from flask_login import UserMixin
from enum import Enum as UserEnum

class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)

class UserRole(UserEnum):
    ADMIN = 1
    USER = 2

class User(BaseModel, UserMixin):
    name = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    avatar = Column(String(100))
    email = Column(String(50))
    active = Column(Boolean, default=True)
    joined_date = Column(DateTime, default=datetime.now)
    user_role = Column(Enum(UserRole), default=UserRole.USER)
    borrowrequest = relationship('BorrowRequest', backref='user', lazy=True)

    def __str__(self):
        return self.name

class Author(BaseModel):
    first_name = Column(String(15), nullable=False)
    last_name = Column(String(50), nullable=False)
    books = relationship('Book', backref='author', lazy=True)

    def __str__(self):
        return self.first_name + ' '+ self.last_name

class Publisher(BaseModel):
    name = Column(String(50), nullable=False, unique=True)
    books = relationship('Book', backref='publisher', lazy=True)

    def __str__(self):
        return self.name

class Category(BaseModel):
    name = Column(String(50), nullable=False, unique=True)
    books = relationship('Book', backref='category', lazy=True)

    def __str__(self):
        return self.name

class Book(BaseModel):
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, default=0)
    active = Column(Boolean, default=True)
    image = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey(Category.id), nullable=False)
    created_date = Column(DateTime, default=datetime.now)
    borrowrequest = relationship('BorrowRequest', backref='book', lazy=True)
    author_id = Column(Integer, ForeignKey(Author.id), nullable=False)
    publisher_id = Column(Integer, ForeignKey(Publisher.id), nullable=False)
    quantity = Column(Integer, default=150, nullable=False)

    def __str__(self):
        return self.name

class BorrowRequest(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    request_date = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    return_date = db.Column(db.DateTime, nullable=True)