# File: venv/app.py
# Aplikasi Flask untuk sistem manajemen ujian
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database import init_db, db_session
from models import User, Exam, Question, Option, Answer
from forms import RegistrationForm, LoginForm, ExamForm, QuestionForm

app = Flask(__name__) # Inisialisasi aplikasi Flask
app.config['SECRET_KEY'] = 'your_secret_key_here' # Ganti dengan kunci rahasia yang kuat
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Nonaktifkan tracking modifikasi untuk mengurangi overhead

login_manager = LoginManager() # Inisialisasi Flask-Login
login_manager.init_app(app) #   Menghubungkan Flask-Login dengan aplikasi Flask
login_manager.login_view = 'login' # Halaman login yang akan di-redirect jika pengguna belum login

@login_manager.user_loader
def load_user(user_id):
    return db_session.query(User).get(int(user_id))

@app.before_request
def before_request():
    init_db() # Pastikan database diinisialisasi sebelum setiap permintaan

@app.teardown_request
def teardown_request(exception=None):
    db_session.remove() # Tutup sesi database setelah setiap permintaan

# --- Routes ---

@app.route('/') # Halaman utama
def index(): # Tampilkan halaman utama
    return render_template('index.html') # Ganti dengan template yang sesuai

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(username=form.username.data, password=hashed_password, role='student') # Default role student
        db_session.add(new_user)
        db_session.commit()
        flash('Registrasi berhasil! Silakan login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db_session.query(User).filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login berhasil!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Login gagal. Periksa username dan password Anda.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'teacher':
        exams = db_session.query(Exam).all()
        return render_template('dashboard.html', exams=exams, user=current_user)
    elif current_user.role == 'student':
        # Tampilkan ujian yang tersedia untuk siswa
        exams = db_session.query(Exam).all() # Untuk sementara, tampilkan semua ujian
        return render_template('dashboard.html', exams=exams, user=current_user)
    return redirect(url_for('index')) # Atau halaman error

@app.route('/manage_exams', methods=['GET', 'POST'])
@login_required
def manage_exams():
    if current_user.role != 'teacher':
        flash('Anda tidak memiliki izin untuk mengakses halaman ini.', 'danger')
        return redirect(url_for('dashboard'))

    exam_form = ExamForm()
    question_form = QuestionForm()

    if exam_form.validate_on_submit() and exam_form.submit.data:
        new_exam = Exam(title=exam_form.title.data, description=exam_form.description.data)
        db_session.add(new_exam)
        db_session.commit()
        flash('Ujian berhasil dibuat!', 'success')
        return redirect(url_for('manage_exams'))

    if question_form.validate_on_submit() and question_form.submit.data:
        exam_id = int(request.form.get('exam_id'))
        exam = db_session.query(Exam).get(exam_id)
        if not exam:
            flash('Ujian tidak ditemukan.', 'danger')
            return redirect(url_for('manage_exams'))

        new_question = Question(exam_id=exam.id, text=question_form.text.data)
        db_session.add(new_question)
        db_session.commit()

        # Tambahkan opsi
        for i in range(1, 5): # Asumsi 4 opsi
            option_text = request.form.get(f'option_{i}')
            is_correct = request.form.get(f'is_correct_{i}') == 'on'
            if option_text:
                new_option = Option(question_id=new_question.id, text=option_text, is_correct=is_correct)
                db_session.add(new_option)
        db_session.commit()
        flash('Pertanyaan berhasil ditambahkan!', 'success')
        return redirect(url_for('manage_exams'))

    exams = db_session.query(Exam).all()
    return render_template('manage_exams.html', exam_form=exam_form, question_form=question_form, exams=exams)

@app.route('/take_exam/<int:exam_id>', methods=['GET', 'POST'])
@login_required
def take_exam(exam_id):
    if current_user.role != 'student':
        flash('Anda tidak memiliki izin untuk mengakses halaman ini.', 'danger')
        return redirect(url_for('dashboard'))

    exam = db_session.query(Exam).get(exam_id)
    if not exam:
        flash('Ujian tidak ditemukan.', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST': # Proses pengiriman jawaban
        score = 0
        for question in exam.questions:
            selected_option_id = request.form.get(f'question_{question.id}')
            if selected_option_id:
                selected_option = db_session.query(Option).get(int(selected_option_id))
                if selected_option and selected_option.is_correct:
                    score += 1

                # Simpan jawaban siswa
                new_answer = Answer(
                    user_id=current_user.id,
                    exam_id=exam.id,
                    question_id=question.id,
                    selected_option_id=selected_option.id if selected_option else None
                )
                db_session.add(new_answer)
        db_session.commit()
        flash(f'Anda menyelesaikan ujian {exam.title} dengan skor: {score}/{len(exam.questions)}', 'success')
        return redirect(url_for('dashboard'))

    return render_template('take_exam.html', exam=exam)


if __name__ == '__main__':
    with app.app_context():
        init_db() # Pastikan database diinisialisasi saat aplikasi pertama kali dijalankan
    app.run(debug=True)