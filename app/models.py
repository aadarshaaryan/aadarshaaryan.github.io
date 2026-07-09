from app.extensions import db

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(30), nullable=False)
    gmail = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)