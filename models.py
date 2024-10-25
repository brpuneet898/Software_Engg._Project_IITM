from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<Student %r>' % self.name
    
class Grades(db.Model):
    __tablename__ = 'grades'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    week_id = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Grades %r>' % self.name


#one to many relationship
#one student can have many grades for different weeks