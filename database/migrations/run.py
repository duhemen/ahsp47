# database/migrations/run.py
"""
Migrasi idempotent database ahsp_47_2026.db
agar sesuai SE Dirjen Bina Konstruksi No. 47/SE/Dk/2026.

Menambah:
  • kolom `jenis` (Normatif/Informatif) pada analisis_ahsp_template
  • tabel `usulan_dokumen`     (dokumen pendukung Lampiran VII)
  • tabel `smkk_proyek`        (perhitungan SMKK per proyek)
  • tabel `ba_penetapan_harga` (BA Penetapan Harga - Huruf F)
  • tabel `migration_log`      (jejak migrasi)
  • seed 9 komponen SMKK (A-I) bila kosong

Jalankan dari root project:
    python -m database.migrations.run
"""

import os
import sys
from datetime import datetime

# Pastikan root project ada di sys.path
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from database.db_manager import DBManager


MIGRATIONS = []


def migration(name):
    def wrap(fn):
        MIGRATIONS.append((name, fn))
        return fn
    return wrap


# ==========================================================
# UTIL
# ==========================================================
def _column_exists(cur, table, column):
    cur.execute(f"PRAGMA table_info({table})")
    return any(r[1] == column for r in cur.fetchall())


def _table_exists(cur, table):
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    return cur.fetchone() is not None


def _ensure_migration_log(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS migration_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_migrasi TEXT UNIQUE NOT NULL,
            dijalankan_pada TEXT NOT NULL
        )
    """)


def _already_migrated(cur, name):
    cur.execute("SELECT 1 FROM migration_log WHERE nama_migrasi = ?", (name,))
    return cur.fetchone() is not None


def _log_migration(cur, name):
    cur.execute(
        "INSERT INTO migration_log (nama_migrasi, dijalankan_pada) VALUES (?, ?)",
        (name, datetime.now().isoformat(timespec="seconds"))
    )


# ==========================================================
# 001 — kolom jenis pada analisis_ahsp_template
# ==========================================================
@migration("001_add_jenis_to_template")
def mig_001(cur):
    if not _table_exists(cur, "analisis_ahsp_template"):
        print("  [SKIP] tabel analisis_ahsp_template belum ada")
        return
    if _column_exists(cur, "analisis_ahsp_template", "jenis"):
        print("  [SKIP] kolom jenis sudah ada")
        return
    cur.execute("ALTER TABLE analisis_ahsp_template ADD COLUMN jenis TEXT DEFAULT 'Informatif'")
    cur.execute("UPDATE analisis_ahsp_template SET jenis='Informatif' WHERE jenis IS NULL")
    print("  [OK] kolom jenis ditambahkan (default: Informatif)")


# ==========================================================
# 002 — usulan_dokumen (Lampiran VII)
# ==========================================================
@migration("002_create_usulan_dokumen")
def mig_002(cur):
    if _table_exists(cur, "usulan_dokumen"):
        print("  [SKIP] tabel usulan_dokumen sudah ada")
        return
    cur.execute("""
        CREATE TABLE usulan_dokumen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usulan_id INTEGER NOT NULL,
            jenis_dokumen TEXT NOT NULL,
            file_path TEXT,
            uploaded_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (usulan_id) REFERENCES usulan_ahsp(id) ON DELETE CASCADE
        )
    """)
    cur.execute("CREATE INDEX idx_usulan_dokumen_usulan ON usulan_dokumen(usulan_id)")
    print("  [OK] tabel usulan_dokumen dibuat")


# ==========================================================
# 003 — smkk_proyek (Lampiran III)
# ==========================================================
@migration("003_create_smkk_proyek")
def mig_003(cur):
    if _table_exists(cur, "smkk_proyek"):
        print("  [SKIP] tabel smkk_proyek sudah ada")
        return
    cur.execute("""
        CREATE TABLE smkk_proyek (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_proyek TEXT,
            nilai_proyek REAL,
            risiko TEXT CHECK(risiko IN ('Kecil','Sedang','Besar')),
            jumlah_pekerja INTEGER,
            subtotal_smkk REAL,
            ppn REAL,
            total_smkk REAL,
            detail_json TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    print("  [OK] tabel smkk_proyek dibuat")


# ==========================================================
# 004 — ba_penetapan_harga (Huruf F)
# ==========================================================
@migration("004_create_ba_penetapan_harga")
def mig_004(cur):
    if _table_exists(cur, "ba_penetapan_harga"):
        print("  [SKIP] tabel ba_penetapan_harga sudah ada")
        return
    cur.execute("""
        CREATE TABLE ba_penetapan_harga (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nomor_ba TEXT NOT NULL,
            balai TEXT NOT NULL,
            tahun INTEGER NOT NULL,
            tanggal_penetapan TEXT NOT NULL,
            file_path TEXT,
            status TEXT DEFAULT 'Draft',
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    print("  [OK] tabel ba_penetapan_harga dibuat")


# ==========================================================
# 005 — seed 9 komponen SMKK (A-I) bila kosong
# ==========================================================
@migration("005_seed_komponen_smkk_9")
def mig_005(cur):
    if not _table_exists(cur, "smkk_komponen"):
        print("  [SKIP] tabel smkk_komponen belum ada")
        return
    cur.execute("SELECT COUNT(*) FROM smkk_komponen WHERE proyek_id IS NULL")
    if cur.fetchone()[0] > 0:
        print("  [SKIP] smkk_komponen default sudah terisi")
        return

    default_9 = [
        ("A", "Penyiapan Dokumen Penerapan SMKK (RKK, RMPK, RKPPL, RMLLP)", "Set", "persentase", 0.0015),
        ("B", "Sosialisasi, Promosi dan Pelatihan", "Ls", "persentase", 0.0030),
        ("C", "Alat Pelindung Kerja (APK) dan Alat Pelindung Diri (APD)", "Ls", "persentase", 0.0030),
        ("D", "Asuransi (Construction All Risk / CAR)", "Ls", "persentase", 0.0010),
        ("E", "Personel Keselamatan Konstruksi", "Orang-Bulan", "persentase", 0.0015),
        ("F", "Fasilitas Sarana, Prasarana dan Alat Kesehatan", "Set", "persentase", 0.0020),
        ("G", "Rambu dan Perlengkapan Lalu Lintas", "Ls", "persentase", 0.0015),
        ("H", "Konsultasi dengan Ahli Terkait Keselamatan Konstruksi", "Orang-Jam", "persentase", 0.0010),
        ("I", "Kegiatan dan Peralatan Terkait Pengendalian Risiko", "Ls", "persentase", 0.0015),
    ]
    for row in default_9:
        cur.execute("""
            INSERT INTO smkk_komponen (kode, nama, satuan, tipe, nilai_default, nilai_kustom, proyek_id)
            VALUES (?, ?, ?, ?, ?, NULL, NULL)
        """, row)
    print("  [OK] 9 komponen SMKK default (A-I) dimasukkan")


# ==========================================================
# RUNNER
# ==========================================================
def run():
    print("=" * 60)
    print("MIGRASI DATABASE ahsp_47_2026")
    print("SE Dirjen Bina Konstruksi No. 47/SE/Dk/2026")
    print("=" * 60)

    db = DBManager()  # otomatis init_db()
    conn = db.get_connection()
    cur = conn.cursor()

    _ensure_migration_log(cur)
    conn.commit()

    for name, fn in MIGRATIONS:
        print(f"\n>>> {name}")
        if _already_migrated(cur, name):
            print("  [SKIP] sudah pernah dijalankan")
            continue
        try:
            fn(cur)
            _log_migration(cur, name)
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"  [ERROR] {e}")
            raise

    conn.close()
    print("\n" + "=" * 60)
    print("MIGRASI SELESAI")
    print("=" * 60)


if __name__ == "__main__":
    run()