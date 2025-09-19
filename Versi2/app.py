#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for, flash, make_response 
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base, User, Exam, Question, Option, Answer
from fpdf import FPDF # Untuk membuat PDF
import json # Untuk mengonversi string JSON
import os # Untuk operasi file
from forms import LoginForm, RegisterForm, ExamForm, QuestionForm # Impor formulir dari forms.py

app = Flask(__name__) # Inisialisasi aplikasi Flask
app.secret_key = 'your_super_secret_key' # Ganti dengan kunci rahasia yang kuat
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///exam_management.db' # Konfigurasi database

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI']) # Membuat engine database
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine)) # Membuat sesi database
Base.query = db_session.query_property() # Menambahkan properti query ke Base

login_manager = LoginManager() # Inisialisasi LoginManager
login_manager.init_app(app) # Mengaitkan dengan aplikasi Flask
login_manager.login_view = 'login' # Halaman login

@app.teardown_appcontext # Menutup sesi database setelah setiap permintaan
def shutdown_session(exception=None): # Fungsi untuk menutup sesi
    db_session.remove() # Menghapus sesi

@login_manager.user_loader # Fungsi untuk memuat pengguna berdasarkan ID
def load_user(user_id): # Fungsi untuk memuat pengguna
    return db_session.query(User).get(int(user_id)) # Mengambil pengguna dari database

@app.route('/') # Halaman beranda
def index(): # Fungsi untuk halaman beranda
    return render_template('index.html') # Render template index.html

@app.route('/login', methods=['GET', 'POST']) # Halaman login
def login(): # Fungsi untuk halaman login
    if current_user.is_authenticated: # Jika sudah login, alihkan ke dashboard
        return redirect(url_for('dashboard')) # Redirect ke dashboard
    
    form = LoginForm() # Inisialisasi formulir login
    if form.validate_on_submit(): # Jika formulir valid
        username = form.username.data # Ambil data username
        password = form.password.data # Ambil data password
        user = db_session.query(User).filter_by(username=username).first() # Cari pengguna di database
        
        if user and check_password_hash(user.password, password): # Jika pengguna ditemukan dan password cocok
            login_user(user) # Login pengguna
            flash('Login berhasil!', 'success') # Flash pesan sukses
            return redirect(url_for('dashboard')) # Redirect ke dashboard
        else: # Jika login gagal
            flash('Nama pengguna atau kata sandi salah.', 'danger') # Flash pesan error
            
    return render_template('login.html', form=form) # Render template login.html dengan formulir

@app.route('/register', methods=['GET', 'POST']) # Halaman registrasi
def register(): # Fungsi untuk halaman registrasi
    if current_user.is_authenticated: # Jika sudah login, alihkan ke dashboard
        return redirect(url_for('dashboard')) # Redirect ke dashboard
        
    form = RegisterForm() # Inisialisasi formulir registrasi
    
    if form.validate_on_submit(): # Jika formulir valid
        username = form.username.data # Ambil data username
        password = form.password.data # Ambil data password
        role = form.role.data # Ambil data role (student/teacher)
        
        if db_session.query(User).filter_by(username=username).first(): # Cek apakah username sudah ada
            flash('Nama pengguna sudah ada.', 'danger') # Flash pesan error
            return redirect(url_for('register')) # Redirect ke halaman registrasi
            
        hashed_password = generate_password_hash(password) # Hash password
        new_user = User(username=username, password=hashed_password, role=role) # Buat instance User baru
        db_session.add(new_user) # Tambahkan ke sesi database
        db_session.commit() # Commit perubahan ke database
        
        flash('Akun berhasil dibuat!', 'success') # Flash pesan sukses
        return redirect(url_for('login')) # Redirect ke halaman login
        
    return render_template('register.html', form=form) #    Render template register.html dengan formulir

@app.route('/logout') # Halaman logout
@login_required # Hanya bisa diakses jika sudah login
def logout(): # Fungsi untuk logout
    logout_user() # Logout pengguna
    return redirect(url_for('index')) # Redirect ke halaman beranda

@app.route('/dashboard') # Halaman dashboard
@login_required # Hanya bisa diakses jika sudah login
def dashboard(): # Fungsi untuk halaman dashboard
    exams = db_session.query(Exam).all() # Ambil semua ujian dari database
    if current_user.role == 'student': # Jika pengguna adalah siswa
        student_answers = db_session.query(Answer).filter_by(student_id=current_user.id).all() # Ambil semua jawaban siswa
        exam_answers_dict = {answer.exam_id: answer for answer in student_answers} # Buat dictionary untuk jawaban siswa
        for exam in exams: # Untuk setiap ujian
            exam.student_answer = exam_answers_dict.get(exam.id) # Tambahkan jawaban siswa ke ujian
    
    return render_template('dashboard.html', exams=exams, user=current_user) # Render template dashboard.html dengan ujian dan pengguna

@app.route('/take_exam/<int:exam_id>', methods=['GET', 'POST']) #   Halaman untuk mengambil ujian
@login_required # Hanya bisa diakses jika sudah login
def take_exam(exam_id): # Fungsi untuk mengambil ujian
    exam = db_session.query(Exam).get(exam_id) # Ambil ujian berdasarkan ID
    if not exam: # Jika ujian tidak ditemukan
        flash('Ujian tidak ditemukan!', 'danger') # Flash pesan error
        return redirect(url_for('dashboard')) # Redirect ke dashboard
    
    if request.method == 'POST': # Jika metode permintaan adalah POST (mengirim jawaban)
        user_answers = {} # Inisialisasi dictionary untuk jawaban pengguna
        score = 0 # Inisialisasi skor
        
        for question in exam.questions: # Untuk setiap pertanyaan dalam ujian
            submitted_option_id = request.form.get(f'question_{question.id}') # Ambil jawaban yang dikirimkan pengguna
            if submitted_option_id: # Jika ada jawaban yang dikirimkan
                user_answers[question.id] = int(submitted_option_id) # Simpan jawaban pengguna
                correct_option = db_session.query(Option).filter_by(question_id=question.id, is_correct=True).first() # Ambil opsi yang benar
                if correct_option and correct_option.id == int(submitted_option_id): # Jika jawaban benar
                    score += 1 # Tambah skor
        
        new_answer = Answer( #  Buat instance Answer baru
            student_id=current_user.id, #   ID siswa
            exam_id=exam.id, # ID ujian
            score=score, # Skor
            submitted_answers=json.dumps(user_answers) # Jawaban yang dikirimkan dalam format JSON
        )
        db_session.add(new_answer) # Tambahkan ke sesi database
        db_session.commit() # Commit perubahan ke database
        
        flash(f'Anda menyelesaikan ujian {exam.title} dengan skor: {score}/{len(exam.questions)}', 'success') # Flash pesan sukses
        return redirect(url_for('dashboard')) # Redirect ke dashboard
        
    return render_template('take_exam.html', exam=exam) # Render template take_exam.html dengan ujian


@app.route('/download_results/<int:exam_id>') # Halaman untuk mengunduh hasil ujian
@login_required # Hanya bisa diakses jika sudah login   
def download_results(exam_id): # Fungsi untuk mengunduh hasil ujian
    exam = db_session.query(Exam).get(exam_id) # Ambil ujian berdasarkan ID
    answers = db_session.query(Answer).filter_by(exam_id=exam_id, student_id=current_user.id).first() # Ambil jawaban siswa untuk ujian tersebut
    
    if not exam or not answers: # Jika ujian atau jawaban tidak ditemukan
        flash('Hasil ujian tidak ditemukan.', 'danger') # Flash pesan error
        return redirect(url_for('dashboard')) # Redirect ke dashboard
        
    user_answers = json.loads(answers.submitted_answers) # Muat jawaban pengguna dari format JSON
    total_questions = len(exam.questions) # Hitung total pertanyaan
    grade = get_grade(answers.score, total_questions) # Dapatkan nilai berdasarkan skor

    class PDF(FPDF): # Kelas untuk membuat PDF
        def header(self): # Header PDF
            self.set_font('Arial', 'B', 12) # Set font
            self.cell(0, 10, 'Formulir Hasil Ujian', 0, 1, 'C') # Judul
            self.ln(5) # Spasi
            
        def footer(self): # Footer PDF
            self.set_y(-15) # Posisi dari bawah
            self.set_font('Arial', 'I', 8) # Set font
            self.cell(0, 10, f'Halaman {self.page_no()}', 0, 0, 'C') # Nomor halaman

    pdf = PDF() # Inisialisasi PDF
    pdf.add_page() # Tambah halaman
    pdf.set_font('Arial', 'B', 16) # Set font besar
    pdf.cell(0, 10, f'Hasil Ujian: {exam.title}', 0, 1) # Judul ujian
    pdf.set_font('Arial', '', 12) # Set font normal
    pdf.cell(0, 10, f'Nama Siswa: {current_user.username}', 0, 1) # Nama siswa
    pdf.cell(0, 10, f'Skor: {answers.score}/{total_questions}', 0, 1) # Skor
    pdf.ln(10) # Spasi

    pdf.cell(0, 10, f'Grade: {grade}', 0, 1) # Tampilkan grade
    pdf.ln(5) # Spasi
    
    for question in exam.questions: # Untuk setiap pertanyaan dalam ujian
        pdf.set_font('Arial', 'B', 12) # Set font tebal
        pdf.multi_cell(0, 10, f'Soal {question.id}: {question.text}') # Teks pertanyaan
        
        pdf.set_font('Arial', '', 10) # Set font normal
        user_choice_id = user_answers.get(str(question.id)) # Jawaban pengguna untuk pertanyaan ini
        
        for option in question.options: # Untuk setiap opsi dalam pertanyaan
            status = ' ' # Status default
            if option.is_correct: # Jika opsi ini adalah jawaban yang benar
                status = 'V' # Tandai dengan V
            if user_choice_id and option.id == user_choice_id: # Jika ini adalah jawaban yang dipilih pengguna
                status = 'X' # Tandai dengan X
                
            pdf.multi_cell(0, 5, f'[{status}] {option.text}') # Tampilkan opsi dengan status
        pdf.ln(5) # Spasi antara pertanyaan
        
    response = make_response(pdf.output(dest='S').encode('latin1')) # Buat respons PDF
    response.headers.set('Content-Disposition', 'attachment', filename=f'hasil_ujian_{exam.id}.pdf') # Set header untuk unduhan
    response.headers.set('Content-Type', 'application/pdf') # Set tipe konten
    return response # Kembalikan respons

@app.route('/manage_exams', methods=['GET', 'POST']) # Halaman untuk mengelola ujian (hanya untuk guru)
@login_required # Hanya bisa diakses jika sudah login
def manage_exams(): #   Fungsi untuk mengelola ujian
    if current_user.role != 'teacher': # Jika bukan guru
        flash('Akses ditolak.', 'danger') # Flash pesan error
        return redirect(url_for('dashboard')) # Redirect ke dashboard

    exam_form = ExamForm() # Inisialisasi formulir ujian
    question_form = QuestionForm() # Inisialisasi formulir pertanyaan

    if request.method == 'POST': # Jika metode permintaan adalah POST
        action = request.form.get('action') # Ambil aksi dari formulir

        if action == 'add_exam' and exam_form.validate_on_submit(): # Jika aksi adalah menambah ujian dan formulir valid
            title = exam_form.title.data # Ambil data judul
            description = exam_form.description.data # Ambil data deskripsi
            new_exam = Exam(title=title, description=description, author=current_user) # Buat instance Exam baru
            db_session.add(new_exam) # Tambahkan ke sesi database
            db_session.commit() # Commit perubahan ke database
            flash('Ujian baru berhasil dibuat!', 'success') # Flash pesan sukses
            return redirect(url_for('manage_exams')) # Redirect ke halaman mengelola ujian
        
        elif action == 'add_question': # Jika aksi adalah menambah pertanyaan
            print("----- Data Formulir Diterima -----") # Debugging: Tanda terima data
            print("Exam ID:", request.form.get('exam_id')) # Debugging: Tampilkan Exam ID
            print("Question Text:", request.form.get('text')) # Debugging: Tampilkan teks pertanyaan
            print("----------------------------------") # Debugging: Akhir tanda
            if question_form.validate_on_submit(): # Jika formulir valid
                exam_id = request.form.get('exam_id') # Ambil ID ujian dari formulir
                exam = db_session.query(Exam).get(exam_id) # Ambil ujian berdasarkan ID
                
                if exam and exam.author == current_user: # Jika ujian ditemukan dan milik guru yang sedang login
                    new_question = Question(text=question_form.text.data, exam=exam) # Buat instance Question baru
                    db_session.add(new_question) # Tambahkan ke sesi database
                    db_session.commit() # Commit perubahan ke database
                    
                    for option_data in question_form.options.data: # Untuk setiap opsi dalam formulir
                        new_option = Option( # Buat instance Option baru
                            question=new_question, # Hubungkan dengan pertanyaan baru
                            text=option_data['text'], # Teks opsi
                            is_correct=option_data['is_correct'] # Apakah ini jawaban yang benar
                        ) # Tutup pembuatan Option
                        db_session.add(new_option) # Tambahkan ke sesi database
                    db_session.commit() # Commit perubahan ke database
                    flash('Pertanyaan berhasil ditambahkan!', 'success') # Flash pesan sukses
                else: # Jika ujian tidak ditemukan atau bukan milik guru
                    flash('Ujian tidak ditemukan atau Anda tidak memiliki izin.', 'danger') # Flash pesan error
                return redirect(url_for('manage_exams')) # Redirect ke halaman mengelola ujian
            else: # Jika formulir tidak valid
                print("----- Validasi Gagal -----") # Debugging: Tanda validasi gagal
                for field_name, field_errors in question_form.errors.items(): # Tampilkan kesalahan validasi
                    if isinstance(field_errors, list): # Jika kesalahan adalah daftar
                        if isinstance(field_errors[0], dict): # Jika kesalahan adalah sub-formulir
                            for i, option_errors in enumerate(field_errors): # Untuk setiap kesalahan opsi
                                for sub_field, sub_errors in option_errors.items(): # Untuk setiap bidang dalam opsi
                                    print(f"Bidang Opsi {i+1} - {sub_field}: {', '.join(sub_errors)}") # Tampilkan kesalahan
                        else: # Jika kesalahan adalah bidang biasa
                            print(f"Bidang: {field_name}, Kesalahan: {', '.join(field_errors)}") # Tampilkan kesalahan
                    else: # Jika kesalahan bukan daftar (kasus tak terduga)
                        print(f"Bidang: {field_name}, Kesalahan: {field_errors}") # Tampilkan kesalahan
                print("--------------------------") # Debugging: Akhir tanda
                flash('Validasi formulir gagal. Pastikan semua bidang diisi dengan benar.', 'danger') # Flash pesan error
        
    exams = db_session.query(Exam).filter_by(author=current_user).all() # Ambil semua ujian yang dibuat oleh guru yang sedang login
    return render_template('manage_exams.html', exams=exams, exam_form=exam_form, question_form=question_form) # Render template manage_exams.html dengan ujian dan formulir

@app.route('/reset_database') # Halaman untuk mereset database (hanya untuk pengembangan)
def reset_database(): # Fungsi untuk mereset database
    try: # Coba blok ini
        if os.path.exists('exam_management.db'): # Jika file database ada
            os.remove('exam_management.db') # Hapus file database lama
        engine = create_engine('sqlite:///exam_management.db') # Buat engine baru
        Base.metadata.create_all(engine) # Buat semua tabel baru
        flash('Database berhasil direset dan dibuat ulang!', 'success') # Flash pesan sukses
    except Exception as e: # Jika ada kesalahan
        flash(f'Gagal mereset database: {e}', 'danger') # Flash pesan error
    return redirect(url_for('index')) # Redirect ke halaman beranda

def get_grade(score, total_questions): # Fungsi untuk mendapatkan nilai berdasarkan skor
    if total_questions == 0: # Jika tidak ada pertanyaan
        return 'N/A'         # Kembalikan N/A
    percentage = (score / total_questions) * 100  # Hitung persentase   
    if percentage >= 90: # Jika persentase >= 90
        return 'A' # Kembalikan nilai A
    elif percentage >= 80: # Jika persentase >= 80
        return 'B' # Kembalikan nilai B
    elif percentage >= 70: # Jika persentase >= 70
        return 'C' # Kembalikan nilai C
    elif percentage >= 60: # Jika persentase >= 60
        return 'D' # Kembalikan nilai D
    else: # Jika persentase < 60
        return 'E' # Kembalikan nilai E
    
if __name__ == '__main__': # Jalankan aplikasi
    if not os.path.exists('exam_management.db'): # Jika file database tidak ada
        from init_db import init_db # Impor fungsi init_db dari init_db.py
        init_db() # Inisialisasi database
    app.run(debug=True) # Jalankan aplikasi dalam mode debug