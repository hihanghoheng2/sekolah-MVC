from app import app
from database import db_session
from models import Exam, Question, Option

with app.app_context():
    try:
        # --- GANTI NILAI DI SINI ---
        exam_title = "Thesis" 
        old_question_text = "Apa tujuan nya?"
        new_question_text = "Apa tujuan nya?"
        new_correct_option_text = "--"
        # --- SAMPAI DI SINI ---

        # Cari pertanyaan yang ingin diubah
        exam = db_session.query(Exam).filter_by(title=exam_title).first()
        if exam:
            question_to_edit = db_session.query(Question).filter_by(exam_id=exam.id, text=old_question_text).first()
            if question_to_edit:
                # Perbarui teks pertanyaan
                question_to_edit.text = new_question_text

                # Hapus semua opsi lama
                db_session.query(Option).filter_by(question_id=question_to_edit.id).delete()

                # Tambahkan opsi baru (contoh)
                options_to_add = [
                    ("Opsi 1", False),
                    ("Opsi 2", True),
                    ("Opsi 3", False),
                    ("opsi 4", False)
                ]
                for text, is_correct in options_to_add:
                    new_option = Option(question_id=question_to_edit.id, text=text, is_correct=is_correct)
                    db_session.add(new_option)

                db_session.commit()
                print(f"Pertanyaan '{old_question_text}' berhasil diperbarui menjadi '{new_question_text}'.")
            else:
                print("Pertanyaan tidak ditemukan.")
        else:
            print("Ujian tidak ditemukan.")

    except Exception as e:
        db_session.rollback()
        print(f"Terjadi kesalahan: {e}")
