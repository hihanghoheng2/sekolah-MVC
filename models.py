from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from database import Base

class User(Base, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(120), nullable=False)
    role = Column(String(20), default='student') # 'student' atau 'teacher'

    exams_taken = relationship('Answer', back_populates='user')

    def __repr__(self):
        return f'<User {self.username}>'

class Exam(Base):
    __tablename__ = 'exams'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(String(255))

    questions = relationship('Question', back_populates='exam', cascade='all, delete-orphan')
    answers = relationship('Answer', back_populates='exam', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Exam {self.title}>'

class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    exam_id = Column(Integer, ForeignKey('exams.id'), nullable=False)
    text = Column(String(255), nullable=False)

    exam = relationship('Exam', back_populates='questions')
    options = relationship('Option', back_populates='question', cascade='all, delete-orphan')
    answers = relationship('Answer', back_populates='question', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Question {self.text}>'

class Option(Base):
    __tablename__ = 'options'
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    text = Column(String(255), nullable=False)
    is_correct = Column(Boolean, default=False)

    question = relationship('Question', back_populates='options')
    selected_answers = relationship('Answer', back_populates='selected_option')

    def __repr__(self):
        return f'<Option {self.text} (Correct: {self.is_correct})>'

class Answer(Base):
    __tablename__ = 'answers'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    exam_id = Column(Integer, ForeignKey('exams.id'), nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    selected_option_id = Column(Integer, ForeignKey('options.id'), nullable=True) # Bisa null jika tidak memilih

    user = relationship('User', back_populates='exams_taken')
    exam = relationship('Exam', back_populates='answers')
    question = relationship('Question', back_populates='answers')
    selected_option = relationship('Option', back_populates='selected_answers')

    def __repr__(self):
        return f'<Answer by User {self.user_id} for Exam {self.exam_id}>'