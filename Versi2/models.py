from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, ForeignKey # Import SQLAlchemy core dan tipe data
from sqlalchemy.orm import sessionmaker, relationship # Import ORM dan relationship
from sqlalchemy.ext.declarative import declarative_base # Import declarative_base untuk model
from flask_login import UserMixin # Import UserMixin untuk integrasi Flask-Login
from datetime import datetime # Import datetime untuk timestamp

# Inisialisasi declarative_base untuk model
Base = declarative_base() # Base class untuk semua model

class User(Base, UserMixin): # Integrasi UserMixin untuk Flask-Login
    __tablename__ = 'users' # Nama tabel di database
    id = Column(Integer, primary_key=True) # Kolom ID sebagai primary key
    username = Column(String(80), unique=True, nullable=False) # Kolom username
    password = Column(String(120), nullable=False) # Kolom password
    role = Column(String(20), nullable=False, default='student')  # 'student' atau 'teacher'
    
    exams = relationship("Exam", back_populates="author") # Relasi ke Exam
    answers = relationship("Answer", back_populates="student") # Relasi ke Answer

    def __repr__(self): # Representasi string dari objek User
        return f'<User {self.username}>' # Representasi string dari objek User
    
    def get_id(self): # Metode untuk mendapatkan ID pengguna
        return str(self.id) # Kembalikan ID sebagai string

class Exam(Base): # Model untuk ujian
    __tablename__ = 'exams'  # Nama tabel di database
    id = Column(Integer, primary_key=True) # Kolom ID sebagai primary key
    title = Column(String(100), nullable=False) # Kolom judul ujian
    description = Column(Text, nullable=True) # Kolom deskripsi ujian
    author_id = Column(Integer, ForeignKey('users.id')) # Kolom foreign key ke User
    
    author = relationship("User", back_populates="exams") # Relasi ke User
    questions = relationship("Question", back_populates="exam", cascade="all, delete-orphan") # Relasi ke Question
    answers = relationship("Answer", back_populates="exam", cascade="all, delete-orphan") # Relasi ke Answer

class Question(Base): # Model untuk pertanyaan
    __tablename__ = 'questions' # Nama tabel di database
    id = Column(Integer, primary_key=True) # Kolom ID sebagai primary key
    exam_id = Column(Integer, ForeignKey('exams.id')) # Kolom foreign key ke Exam
    text = Column(Text, nullable=False) # Kolom teks pertanyaan
    
    exam = relationship("Exam", back_populates="questions") # Relasi ke Exam
    options = relationship("Option", back_populates="question", cascade="all, delete-orphan") # Relasi ke Option

class Option(Base): # Model untuk opsi jawaban
    __tablename__ = 'options' # Nama tabel di database
    id = Column(Integer, primary_key=True) # Kolom ID sebagai primary key
    question_id = Column(Integer, ForeignKey('questions.id')) # Kolom foreign key ke Question
    text = Column(Text, nullable=False) # Kolom teks opsi
    is_correct = Column(Boolean, default=False) # Kolom untuk menandai apakah opsi ini jawaban yang benar
    
    question = relationship("Question", back_populates="options") # Relasi ke Question

class Answer(Base): # Model untuk jawaban siswa
    __tablename__ = 'answers' # Nama tabel di database
    id = Column(Integer, primary_key=True) # Kolom ID sebagai primary key
    exam_id = Column(Integer, ForeignKey('exams.id')) # Kolom foreign key ke Exam
    student_id = Column(Integer, ForeignKey('users.id')) # Kolom foreign key ke User (siswa)
    score = Column(Integer) # Kolom skor jawaban
    date_taken = Column(DateTime, default=datetime.now) # Kolom tanggal pengambilan ujian
    submitted_answers = Column(Text) # Kolom untuk menyimpan jawaban yang diajukan (misalnya dalam format JSON)
    
    exam = relationship("Exam", back_populates="answers") # Relasi ke Exam
    student = relationship("User", back_populates="answers") # Relasi ke User (siswa)