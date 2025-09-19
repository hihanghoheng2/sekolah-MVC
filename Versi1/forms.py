from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from models import User

from database import db_session
from models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Konfirmasi Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Daftar')

    def validate_username(self, username):
        # Menggunakan db_session.query(User) secara eksplisit
        user = db_session.query(User).filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username sudah ada. Silakan pilih username lain.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ExamForm(FlaskForm):
    title = StringField('Judul Ujian', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Deskripsi')
    submit = SubmitField('Buat Ujian')

class QuestionForm(FlaskForm):
    text = TextAreaField('Teks Pertanyaan', validators=[DataRequired()])
    # Asumsi 4 opsi untuk setiap pertanyaan
    option_1 = StringField('Opsi 1', validators=[DataRequired()])
    is_correct_1 = BooleanField('Benar')
    option_2 = StringField('Opsi 2', validators=[DataRequired()])
    is_correct_2 = BooleanField('Benar')
    option_3 = StringField('Opsi 3', validators=[DataRequired()])
    is_correct_3 = BooleanField('Benar')
    option_4 = StringField('Opsi 4', validators=[DataRequired()])
    is_correct_4 = BooleanField('Benar')
    submit = SubmitField('Tambah Pertanyaan')
