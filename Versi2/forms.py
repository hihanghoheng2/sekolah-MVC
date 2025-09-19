from flask_wtf import FlaskForm # Import FlaskForm untuk membuat formulir
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, BooleanField, FieldList, FormField # Import berbagai jenis field dari WTForms
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError # Import validator untuk validasi input
 
from database import db_session # Pastikan db_session diimpor dari database.py
from models import User # Pastikan model User diimpor dari models.py

class LoginForm(FlaskForm): # Formulir login
    username = StringField('Nama Pengguna', validators=[DataRequired()]) # Field untuk nama pengguna
    password = PasswordField('Kata Sandi', validators=[DataRequired()]) # Field untuk kata sandi
    submit = SubmitField('Login') # Tombol submit

class RegisterForm(FlaskForm): # Formulir pendaftaran
    username = StringField('Nama Pengguna', validators=[DataRequired(), Length(min=4, max=25)]) # Field untuk nama pengguna
    password = PasswordField('Kata Sandi', validators=[DataRequired(), Length(min=6)]) # Field untuk kata sandi
    role = SelectField('Daftar Sebagai', choices=[('student', 'Siswa'), ('teacher', 'Guru')], validators=[DataRequired()]) # Field untuk memilih peran
    submit = SubmitField('Daftar') # Tombol submit

    def validate_username(self, username): # Validasi khusus untuk memastikan username unik
        user = db_session.query(User).filter_by(username=username.data).first() # Periksa apakah username sudah ada di database
        if user: # Jika ada, lemparkan error validasi
            raise ValidationError('Username sudah ada. Silakan pilih username lain.') # Pesan error

class ExamForm(FlaskForm): # Formulir untuk membuat ujian
    title = StringField('Judul Ujian', validators=[DataRequired(), Length(max=100)]) # Field untuk judul ujian
    description = TextAreaField('Deskripsi') # Field untuk deskripsi ujian
    submit = SubmitField('Buat Ujian') # Tombol submit

class OptionForm(FlaskForm): # Formulir untuk opsi jawaban
    # Menonaktifkan validasi CSRF untuk sub-formulir ini 
    class Meta: # Meta class untuk konfigurasi formulir
        csrf = False  # Nonaktifkan CSRF untuk sub-formulir ini   
        
    text = StringField('Teks Opsi', validators=[DataRequired()]) # Field untuk teks opsi
    is_correct = BooleanField('Jawaban Benar') # Field untuk menandai apakah opsi ini jawaban yang benar

class QuestionForm(FlaskForm): # Formulir untuk pertanyaan
    text = TextAreaField('Teks Pertanyaan', validators=[DataRequired()]) # Field untuk teks pertanyaan
    options = FieldList(FormField(OptionForm), min_entries=4, max_entries=4) # Daftar opsi jawaban
    submit = SubmitField('Tambah Pertanyaan') # Tombol submit