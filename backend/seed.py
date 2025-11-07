# seed.py
"""
Script sederhana untuk mengisi data awal ke database.
Gunakan hanya untuk pengujian dan presentasi.
"""

from database.connection import SessionLocal, engine, Base
from database.models import Destination
from sqlalchemy.exc import IntegrityError

Base.metadata.create_all(bind=engine)

db = SessionLocal()

destinations = [
    Destination(
        name="Pantai Kuta",
        category="Pantai",
        location="Badung, Bali",
        price=0,
        description="Pantai populer dengan pemandangan matahari terbenam yang indah.",
        image_url="https://example.com/kuta.jpg",
    ),
    Destination(
        name="Ubud Monkey Forest",
        category="Alam & Budaya",
        location="Gianyar, Bali",
        price=80000,
        description="Hutan lindung dengan ratusan monyet dan pura kuno.",
        image_url="https://example.com/ubud.jpg",
    ),
    Destination(
        name="Danau Batur",
        category="Alam",
        location="Bangli, Bali",
        price=50000,
        description="Danau vulkanik dengan pemandangan Gunung Batur yang menawan.",
        image_url="https://example.com/batur.jpg",
    ),
]

try:
    db.add_all(destinations)
    db.commit()
    print("✅ Data destinasi awal berhasil ditambahkan.")
except IntegrityError:
    db.rollback()
    print("⚠️ Data sudah pernah diisi sebelumnya, lewati pengisian.")
finally:
    db.close()
