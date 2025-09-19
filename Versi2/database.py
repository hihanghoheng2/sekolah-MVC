from sqlalchemy import create_engine # Inisialisasi koneksi ke database
from sqlalchemy.orm import scoped_session, sessionmaker # Menggunakan scoped_session untuk thread-safety
from sqlalchemy.ext.declarative import declarative_base # Deklarasi base class untuk model

engine = create_engine('sqlite:///exam_management.db') # Menggunakan SQLite
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
# Inisialisasi Base class untuk model
Base = declarative_base() # Base class untuk semua model
Base.query = db_session.query # Menambahkan query ke Base class

def init_db(): # Inisialisasi database
    import models # Import semua model di sini agar terdeteksi oleh Base.metadata
    Base.metadata.create_all(bind=engine)