"""
Module: database.connection
Deskripsi:
Menangani koneksi ke database menggunakan SQLAlchemy dan menyediakan SessionLocal
untuk operasi CRUD di seluruh aplikasi. File ini juga mendefinisikan Base sebagai 
dasar dari semua model ORM yang digunakan.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import DATABASE_URL

# Membuat engine database
# Jika menggunakan SQLite, tambahkan connect_args untuk menghindari error thread
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

# Membuat session untuk interaksi dengan database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base untuk semua model SQLAlchemy
Base = declarative_base()

def get_db():
    """
    Dependency yang digunakan di setiap endpoint untuk mendapatkan session database.
    Setelah selesai digunakan, session akan ditutup otomatis.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
