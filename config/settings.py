# config/settings.py
import os
import sys

# ==========================================================
# BASE DIR — handle script & frozen (.exe)
# ==========================================================
if getattr(sys, "frozen", False):
    # Dijalankan sebagai .exe (PyInstaller) → DB di samping .exe
    BASE_DIR = os.path.dirname(sys.executable)
    _DB_DIR = BASE_DIR
    _ASSETS_DIR = getattr(sys, "_MEIPASS", BASE_DIR)  # resource di temp extract
else:
    # Dijalankan sebagai script
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _DB_DIR = os.path.join(BASE_DIR, "database")
    _ASSETS_DIR = BASE_DIR

DB_PATH = os.path.join(_DB_DIR, "ahsp_47_2026.db")
ASSETS_DIR = _ASSETS_DIR

# ==========================================================
# APP METADATA
# ==========================================================
APP_NAME = "Aplikasi AHSP & Rekapitulasi HPS/RAB - SE 47/SE/Dk/2026"
APP_VERSION = "2.0.0"
SE_NOMOR = "47/SE/Dk/2026"
SE_TANGGAL = "13 Februari 2026"
SE_MENCABUT = "182/SE/Dk/2025"

# ==========================================================
# KALKULASI
# ==========================================================
# Overhead & Profit: contoh SE pakai 10%. Bisa diubah 0-15% oleh pengguna.
DEFAULT_OVERHEAD_PROFIT = 10.0
OVERHEAD_PROFIT_MIN = 0.0
OVERHEAD_PROFIT_MAX = 15.0

# PPN ditambahkan di REKAP, bukan di AHSP
DEFAULT_PPN = 11.0

# ==========================================================
# BIDANG — HARUS SAMA PERSIS dengan CHECK constraint di db_manager.py
# ==========================================================
BIDANG_BM = "Bina Marga"
BIDANG_SDA = "Sumber Daya Air (SDA)"   # ← FIX: sebelumnya "Sumber Daya Air"
BIDANG_CK = "Cipta Karya"

# ==========================================================
# TINGKAT RISIKO SMKK (Lampiran III)
# ==========================================================
RISIKO_KECIL = "Kecil"
RISIKO_SEDANG = "Sedang"
RISIKO_BESAR = "Besar"

# ==========================================================
# BATAS WAKTU REGULASI
# ==========================================================
BATAS_BA_HARGA_BULAN = 10
BATAS_BA_HARGA_TANGGAL = 31
BATAS_PERALIHAN_SIRUP_HARI = 20

# ==========================================================
# TEKNIS
# ==========================================================
STRAND_PANJANG_M = 50.0
STRAND_BERAT_KG_PER_M = 21.90