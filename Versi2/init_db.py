from sqlalchemy import create_engine # Inisialisasi koneksi ke database
from models import Base # Pastikan model Base diimpor dari models.py
import os # Untuk operasi file

DB_PATH = 'exam_management.db' # Nama file database

def init_db(): # Inisialisasi database
    if os.path.exists(DB_PATH): # Hapus database lama jika ada
        os.remove(DB_PATH) # Hapus file database lama           
        print("Database lama dihapus.") # Konfirmasi penghapusan
    
    engine = create_engine(f'sqlite:///{DB_PATH}') # Gunakan SQLite
    Base.metadata.create_all(engine) # Buat semua tabel berdasarkan model
    print("Database dan tabel baru berhasil dibuat.") # Konfirmasi pembuatan database

if __name__ == '__main__': # Jalankan inisialisasi database jika file ini dieksekusi langsung
    init_db() # Panggil fungsi inisialisasi database