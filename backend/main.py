"""
Main entry point aplikasi Travel Planner API.

Deskripsi:
File ini menginisialisasi instance FastAPI, membuat tabel database
berdasarkan model SQLAlchemy, dan meregistrasikan seluruh router layanan.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.connection import Base, engine
from services.auth.router import router as auth_router
from services.review.router import router as review_router
from services.explorer.router import router as explorer_router
from services.user.router import router as user_router
from services.itinerary.router import router as itinerary_router


# Inisialisasi aplikasi FastAPI
app = FastAPI(
    title="Travel Planner API",
    version="1.0",
    description=(
        "Backend API untuk aplikasi Travel Planner. "
        "Menyediakan fitur autentikasi pengguna, eksplorasi destinasi, "
        "serta ulasan perjalanan wisata."
    ),
)

# Membuat seluruh tabel database berdasarkan model (jika belum ada)
Base.metadata.create_all(bind=engine)

# Konfigurasi CORS agar frontend (React/Flutter) bisa mengakses API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # sementara open, nanti bisa dibatasi ke domain frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrasi router dari setiap service
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(review_router, prefix="/reviews", tags=["Reviews"])
app.include_router(explorer_router, prefix="/explorer", tags=["Explorer"])
app.include_router(user_router, prefix="/user", tags=["User"])
app.include_router(itinerary_router, prefix="/itineraries", tags=["Itineraries"])

# Endpoint root
@app.get("/", tags=["Root"])
def home():
    """
    Endpoint root sederhana untuk mengecek status API.
    """
    return {
        "message": "Welcome to Travel Planner API 🚀",
        "status": "Running",
        "version": "1.0",
    }
