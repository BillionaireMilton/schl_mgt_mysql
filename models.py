import os
from dotenv import load_dotenv
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, create_engine
from flask_sqlalchemy import SQLAlchemy
import json
from flask_migrate import Migrate
from datetime import datetime, timezone
from flask_bcrypt import Bcrypt
# from flaskr import create_app

load_dotenv()
database_name = 'schl_mgt'
# database_path = "postgresql://{}:{}@{}/{}".format("postgres", "postgres", "localhost:5432", database_name)
database_path = "mysql+pymysql://root:password@localhost/schl_mgt"
# database_path = os.getenv("DATABASE_URL")
# database_path = 'sqllite3:///'

bcrypt = Bcrypt()
db = SQLAlchemy()
migrate = Migrate()



"""
setup_db(app)
    binds a flask application and a SQLAlchemy service
"""
def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    bcrypt.init_app(app)
    db.app = app
    db.init_app(app)
    migrate.init_app(app, db)
    with app.app_context():
        db.create_all()

"""
School
"""
class School(db.Model):
    __tablename__ = 'schools'

    id = db.Column(db.Integer, primary_key=True)
    school_name = db.Column(db.String(20))
    school_owner = db.Column(db.String(20))
    school_email = db.Column(db.String(25))
    school_phone = db.Column(db.String(20))
    school_address = db.Column(db.String(100))
    school_password = db.Column(db.String(200))
    school_type = db.Column(db.String(20))
    school_status = db.Column(db.String(20))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    teachers = db.relationship("Teacher", backref=db.backref("teacher", uselist=False))


    def __init__(self, school_name, school_owner, school_email, school_phone, school_address, school_password, school_type, school_status, date_added):
        self.school_name = school_name
        self.school_owner = school_owner
        self.school_email = school_email
        self.school_phone = school_phone
        self.school_address = school_address
        self.school_password = bcrypt.generate_password_hash(school_password).decode('UTF-8')
        self.school_type = school_type
        self.school_status = school_status
        self.date_added = date_added

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'school_name': self.school_name,
            'school_owner': self.school_owner,
            'school_email': self.school_email,
            'school_phone': self.school_phone,
            'school_address': self.school_address,
            'school_password': self.school_password,
            'school_type': self.school_type,
            'school_status': self.school_status,
            'date_added': self.date_added,
            # "teachers": self.teachers
            "teachers": [teacher.format() for teacher in self.teachers]
            # "teachers": [teacher.to_dict() for teacher in self.teachers]
            }

"""
Teachers
"""
class Teacher(db.Model):
    __tablename__ = 'teachers'

    id = Column(Integer, primary_key=True)
    school_id = Column(Integer, ForeignKey('schools.id'))
    date_of_joining = Column(DateTime, default=datetime.utcnow)
    teacher_first_name = Column(String(25))
    teacher_last_name = Column(String(25))
    teacher_course = Column(String(25))
    teacher_gender = Column(String(6))
    date_of_birth = Column(DateTime, default=datetime.utcnow)
    teacher_phone = Column(Integer, default="0000000")
    teacher_type = Column(String(15), default="full-time")
    teacher_status = Column(String(20), default="probation")
    teacher_address = Column(String(50), default="Not Set")
    is_teaching = Column(Boolean, default=True)
    profile_image = Column(String(100))
    teacher_email = Column(String(50))
    teacher_password = Column(String(200))


    def __init__(self, school_id, date_of_joining, teacher_first_name, teacher_last_name, teacher_course, teacher_gender, date_of_birth, teacher_phone, teacher_type, teacher_status, teacher_address, is_teaching, profile_image, teacher_email, teacher_password):
        self.school_id = school_id
        self.date_of_joining = date_of_joining
        self.teacher_first_name = teacher_first_name
        self.teacher_last_name = teacher_last_name
        self.teacher_course = teacher_course
        self.teacher_gender = teacher_gender
        self.date_of_birth = date_of_birth
        self.teacher_phone = teacher_phone
        self.teacher_type = teacher_type
        self.teacher_status = teacher_status
        self.teacher_address = teacher_address
        self.is_teaching = is_teaching
        self.profile_image = profile_image
        self.teacher_email = teacher_email
        self.teacher_password = bcrypt.generate_password_hash(teacher_password).decode('UTF-8')

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'school_id': self.school_id,
            'date_of_joining': self.date_of_joining,
            'teacher_first_name': self.teacher_first_name,
            'teacher_last_name': self.teacher_last_name,
            'teacher_course': self.teacher_course,
            'teacher_gender': self.teacher_gender,
            'date_of_birth': self.date_of_birth,
            'teacher_phone': self.teacher_phone,
            'teacher_type': self.teacher_type,
            'teacher_status': self.teacher_status,
            'teacher_address': self.teacher_address,
            'is_teaching': self.is_teaching,
            'profile_image': self.profile_image,
            'teacher_email': self.teacher_email,
            'teacher_password': self.teacher_password
            }