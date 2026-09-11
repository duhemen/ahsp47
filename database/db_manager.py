# database/db_manager.py
"""
Manajer database SQLite untuk Aplikasi AHSP SE 47/SE/Dk/2026.

PENTING: Versi ini konsolidasi dari db_manager.py lama +
penambahan tabel sesuai SE 47/SE/Dk/2026:
  • kolom `jenis` pada analisis_ahsp_template (Normatif/Informatif)
  • tabel usulan_dokumen      (Lampiran VII — 7 dokumen pendukung)
  • tabel smkk_proyek         (Lampiran III — hasil perhitungan SMKK)
  • tabel ba_penetapan_harga  (Huruf F — BA max 31 Oktober)
  • kolom nilai_kontrak & smkk_total pada proyek_rab
"""

import sqlite3
from config.settings import DB_PATH


class DBManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.init_db()

    # ==========================================================
    # KONEKSI
    # ==========================================================
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    # ==========================================================
    # HELPER MIGRASI (self-contained — buka koneksi sendiri)
    # ==========================================================
    def _column_exists(self, table: str, column: str) -> bool:
        """
        Cek apakah kolom ada di tabel.
        Aman dipanggil kapan saja — membuka koneksi sendiri & menutupnya.
        """
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute(f"PRAGMA table_info({table})")
            return any(row[1] == column for row in cur.fetchall())
        finally:
            conn.close()

    def _table_exists(self, table: str) -> bool:
        """
        Cek apakah tabel ada di database.
        Aman dipanggil kapan saja — membuka koneksi sendiri & menutupnya.
        """
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table,),
            )
            return cur.fetchone() is not None
        finally:
            conn.close()

    # ==========================================================
    # INISIALISASI
    # ==========================================================
    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # ---------- 1. Data HSP (Lampiran I) ----------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hsp_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kode TEXT UNIQUE NOT NULL,
                uraian TEXT NOT NULL,
                kategori TEXT CHECK(kategori IN ('Tenaga Kerja', 'Bahan', 'Peralatan')),
                satuan TEXT NOT NULL,
                harga_satuan REAL NOT NULL,
                sumber_vendor TEXT,
                tanggal_survei TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT
            )
        """)

        # ---------- 2. Laporan Pengumpulan Data HSP Balai ----------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS laporan_pengumpulan_hsp (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nomor_ba TEXT NOT NULL,
                nama_balai TEXT NOT NULL,
                tahun INTEGER NOT NULL,
                petugas_lapangan TEXT,
                pengawas TEXT,
                pengolah_data TEXT,
                tanggal_penetapan TEXT,
                status_rekonsiliasi TEXT DEFAULT 'Draft'
            )
        """)

        # ---------- 3. Acuan & Konversi (Lampiran II) ----------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS acuan_konversi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                jenis_tanah_bahan TEXT NOT NULL,
                kondisi_semula TEXT NOT NULL,
                fk_asli REAL NOT NULL,
                fk_lepas REAL NOT NULL,
                fk_padat REAL NOT NULL
            )
        """)

        # ---------- 4. Master Proyek RAB / HPS ----------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS proyek_rab (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama_proyek TEXT NOT NULL,
                lokasi TEXT NOT NULL,
                instansi TEXT NOT NULL,
                tahun_anggaran INTEGER NOT NULL,
                overhead_pct REAL DEFAULT 10.0,
                ppn_pct REAL DEFAULT 11.0,
                tanggal_buat TEXT
            )
        """)

        # ---------- 5. Item Pekerjaan RAB ----------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS item_rab (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proyek_id INTEGER NOT NULL,
                divisi TEXT NOT NULL,
                kode_item TEXT NOT NULL,
                uraian_pekerjaan TEXT NOT NULL,
                satuan TEXT NOT NULL,
                volume REAL NOT NULL,
                harga_dasar REAL NOT NULL,
                overhead_pct REAL NOT NULL,
                harga_satuan REAL NOT NULL,
                FOREIGN KEY (proyek_id) REFERENCES proyek_rab (id)
            )
        """)

        # ---------- 6. Usulan AHSP (Lampiran VII) ----------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usulan_ahsp (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nomor_surat TEXT NOT NULL,
                pengusul TEXT NOT NULL,
                jenis_usulan TEXT CHECK(jenis_usulan IN ('Baru', 'Perubahan Mayor', 'Perubahan Minor')),
                nama_pekerjaan TEXT NOT NULL,
                alasan_justifikasi TEXT NOT NULL,
                sptjm_status INTEGER DEFAULT 0 CHECK(sptjm_status IN (0,1)),
                tanggal_usulan TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT
            )
        """)

        # ---------- 7. Komponen SMKK (Lampiran III) ----------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS smkk_komponen (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kode TEXT UNIQUE NOT NULL,
                nama TEXT NOT NULL,
                satuan TEXT NOT NULL,
                tipe TEXT NOT NULL CHECK(tipe IN ('persentase', 'nilai_manual')),
                nilai_default REAL NOT NULL,
                nilai_kustom REAL,
                proyek_id INTEGER,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT,
                FOREIGN KEY (proyek_id) REFERENCES proyek_rab(id)
            )
        """)

        # ---------- 8. Master Template Item Pekerjaan AHSP ----------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analisis_ahsp_template (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kode_pekerjaan TEXT UNIQUE NOT NULL,
                nama_pekerjaan TEXT NOT NULL,
                satuan TEXT NOT NULL,
                bidang TEXT NOT NULL CHECK(bidang IN ('Bina Marga', 'Sumber Daya Air (SDA)', 'Cipta Karya'))
            )
        """)

        # ---------- 9. Rincian Komponen Koefisien Analisis AHSP ----------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analisis_ahsp_detail (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER,
                komponen_kode TEXT NOT NULL,
                koefisien_standar REAL NOT NULL,
                FOREIGN KEY (template_id) REFERENCES analisis_ahsp_template(id),
                FOREIGN KEY (komponen_kode) REFERENCES hsp_data(kode)
            )
        """)

        # ======================================================
        # MIGRASI TAMBAHAN (SE 47/SE/Dk/2026)
        # ======================================================

        # ---------- 10. Tabel usulan_dokumen ----------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usulan_dokumen (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usulan_id INTEGER NOT NULL,
                jenis_dokumen TEXT NOT NULL,
                file_path TEXT,
                uploaded_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (usulan_id) REFERENCES usulan_ahsp(id) ON DELETE CASCADE
            )
        """)

        # ---------- 11. Tabel smkk_proyek ----------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS smkk_proyek (
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

        # ---------- 12. Tabel ba_penetapan_harga ----------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ba_penetapan_harga (
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

        # ---------- 13. Tabel migration_log ----------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS migration_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama_migrasi TEXT UNIQUE NOT NULL,
                dijalankan_pada TEXT NOT NULL
            )
        """)

        # ---------- 14. Kolom jenis pada analisis_ahsp_template ----------
        if not self._column_exists("analisis_ahsp_template", "jenis"):
            cursor.execute(
                "ALTER TABLE analisis_ahsp_template ADD COLUMN jenis TEXT DEFAULT 'Informatif'"
            )
            cursor.execute(
                "UPDATE analisis_ahsp_template SET jenis='Informatif' WHERE jenis IS NULL"
            )

        # ---------- 15. Kolom nilai_kontrak pada proyek_rab ----------
        if not self._column_exists("proyek_rab", "nilai_kontrak"):
            cursor.execute(
                "ALTER TABLE proyek_rab ADD COLUMN nilai_kontrak REAL DEFAULT 0"
            )

        # ---------- 16. Kolom smkk_total pada proyek_rab (cache) ----------
        if not self._column_exists("proyek_rab", "smkk_total"):
            cursor.execute(
                "ALTER TABLE proyek_rab ADD COLUMN smkk_total REAL DEFAULT 0"
            )

        # ---------- Indexes ----------
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_hsp_data_kode ON hsp_data(kode)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_item_rab_proyek_id ON item_rab(proyek_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_smkk_komponen_kode ON smkk_komponen(kode)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_smkk_komponen_proyek_id ON smkk_komponen(proyek_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analisis_template_kode ON analisis_ahsp_template(kode_pekerjaan)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analisis_detail_template ON analisis_ahsp_detail(template_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_usulan_dokumen_usulan ON usulan_dokumen(usulan_id)")

        # ---------- COMMIT & CLOSE (SETELAH semua ALTER) ----------
        conn.commit()
        conn.close()

        # ---------- Seed data (buka koneksi sendiri) ----------
        self.seed_initial_data()

    # ==========================================================
    # SEED DATA AWAL
    # ==========================================================
    def seed_initial_data(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # ---------- 1. Sample HSP ----------
        cursor.execute("SELECT COUNT(*) FROM hsp_data")
        if cursor.fetchone()[0] == 0:
            sample_hsp = [
                ("L.01", "Pekerja", "Tenaga Kerja", "OH", 150000.0, "Survei UMK", "2026-08-01"),
                ("L.02", "Tukang Batu", "Tenaga Kerja", "OH", 180000.0, "Survei UMK", "2026-08-01"),
                ("L.04", "Mandor", "Tenaga Kerja", "OH", 210000.0, "Survei UMK", "2026-08-01"),
                ("M.12", "Semen Portland (PC)", "Bahan", "kg", 1600.0, "Distributor", "2026-08-01"),
                ("M.05.b", "Pasir Pasang", "Bahan", "m3", 220000.0, "Quarry Lokal", "2026-08-01"),
                ("E.06", "Concrete Mixer 500 Liter", "Peralatan", "jam", 85000.0, "Sewa Alat", "2026-08-01"),
                ("E.10", "Excavator Backhoe 0.93 m3", "Peralatan", "jam", 350000.0, "Sewa Alat", "2026-08-01"),
                ("E.35", "Dump Truck 10 Ton", "Peralatan", "jam", 280000.0, "Sewa Alat", "2026-08-01"),
                ("E.15.e", "Excavator 155 HP", "Peralatan", "jam", 562993.0, "Sewa Alat", "2026-08-01"),
            ]
            cursor.executemany(
                """INSERT INTO hsp_data
                   (kode, uraian, kategori, satuan, harga_satuan, sumber_vendor, tanggal_survei)
                   VALUES (?,?,?,?,?,?,?)""",
                sample_hsp,
            )

        # ---------- 2. Sample Acuan Konversi ----------
        cursor.execute("SELECT COUNT(*) FROM acuan_konversi")
        if cursor.fetchone()[0] == 0:
            sample_fk = [
                ("Pasir", "Asli (A)", 1.000, 1.110, 0.950),
                ("Pasir", "Lepas (B)", 0.900, 1.000, 0.860),
                ("Tanah Liat Berpasir", "Asli (A)", 1.000, 1.250, 0.900),
                ("Tanah Liat", "Asli (A)", 1.000, 1.430, 0.900),
            ]
            cursor.executemany(
                """INSERT INTO acuan_konversi
                   (jenis_tanah_bahan, kondisi_semula, fk_asli, fk_lepas, fk_padat)
                   VALUES (?,?,?,?,?)""",
                sample_fk,
            )

        # ---------- 3. Sample Proyek & Item RAB ----------
        cursor.execute("SELECT COUNT(*) FROM proyek_rab")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO proyek_rab
                (nama_proyek, lokasi, instansi, tahun_anggaran,
                 overhead_pct, ppn_pct, tanggal_buat)
                VALUES ('Pembangunan Jembatan & Jalan Akses Pesisir',
                        'Kabupaten Semarang', 'Dinas Pekerjaan Umum', 2026,
                        10.0, 11.0, '2026-09-09')
            """)
            proyek_id = cursor.lastrowid

            sample_items = [
                (proyek_id, "DIVISI 1 - UMUM & SMKK", "1.22.(1a)",
                 "Penyiapan Dokumen Penerapan SMKK", "Set", 1.0, 5000000.0, 10.0, 5500000.0),
                (proyek_id, "DIVISI 1 - UMUM & SMKK", "1.22.(3a)",
                 "Alat Pelindung Kerja (APK) & APD", "Ls", 1.0, 15000000.0, 10.0, 16500000.0),
                (proyek_id, "DIVISI 2 - DRAINASE", "2.1.(1)",
                 "Galian untuk Selokan Drainase dan Saluran Air", "m3", 450.0, 45000.0, 10.0, 49500.0),
                (proyek_id, "DIVISI 2 - DRAINASE", "2.2.(1)",
                 "Pasangan Batu dengan Mortar", "m3", 120.0, 850000.0, 10.0, 935000.0),
                (proyek_id, "DIVISI 3 - PEKERJAAN TANAH", "3.1.(1a)",
                 "Galian Tanah Biasa", "m3", 1250.0, 35000.0, 10.0, 38500.0),
                (proyek_id, "DIVISI 5 - PERKERASAN BERBUTIR", "5.1.(1a)",
                 "Lapis Fondasi Agregat Kelas A", "m3", 320.0, 480000.0, 10.0, 528000.0),
            ]
            cursor.executemany("""
                INSERT INTO item_rab
                (proyek_id, divisi, kode_item, uraian_pekerjaan, satuan,
                 volume, harga_dasar, overhead_pct, harga_satuan)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, sample_items)

        # ---------- 3b. Seed 2 proyek tambahan (SDA + CK) ----------
        cursor.execute("SELECT COUNT(*) FROM proyek_rab")
        if cursor.fetchone()[0] == 1:
            # Proyek SDA
            cursor.execute("""
                INSERT INTO proyek_rab
                (nama_proyek, lokasi, instansi, tahun_anggaran,
                 overhead_pct, ppn_pct, tanggal_buat)
                VALUES ('Rehabilitasi Daerah Irigasi Cisadane',
                        'Kabupaten Tangerang', 'Balai Besar Wilayah Sungai', 2026,
                        10.0, 11.0, '2026-09-09')
            """)
            sda_pid = cursor.lastrowid
            cursor.executemany("""
                INSERT INTO item_rab
                (proyek_id, divisi, kode_item, uraian_pekerjaan, satuan,
                 volume, harga_dasar, overhead_pct, harga_satuan)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, [
                (sda_pid, "DIVISI 1 - PEKERJAAN PERSIAPAN", "SDA.1.1",
                 "Pembersihan Lahan", "m2", 2500.0, 15000.0, 10.0, 16500.0),
                (sda_pid, "DIVISI 2 - GALIAN", "SDA.01.g",
                 "Galian Tanah Biasa Mekanis", "m3", 1800.0, 42000.0, 10.0, 46200.0),
                (sda_pid, "DIVISI 3 - PASANGAN", "SDA.3.1",
                 "Pasangan Batu Kali 1:4", "m3", 350.0, 720000.0, 10.0, 792000.0),
            ])

            # Proyek Cipta Karya
            cursor.execute("""
                INSERT INTO proyek_rab
                (nama_proyek, lokasi, instansi, tahun_anggaran,
                 overhead_pct, ppn_pct, tanggal_buat)
                VALUES ('Pembangunan Gedung Kantor 3 Lantai',
                        'Kota Bandung', 'Dinas Cipta Karya', 2026,
                        10.0, 11.0, '2026-09-09')
            """)
            ck_pid = cursor.lastrowid
            cursor.executemany("""
                INSERT INTO item_rab
                (proyek_id, divisi, kode_item, uraian_pekerjaan, satuan,
                 volume, harga_dasar, overhead_pct, harga_satuan)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, [
                (ck_pid, "DIVISI 1 - PEKERJAAN PERSIAPAN", "CK.1.1",
                 "Bongkaran & Pembersihan", "m2", 800.0, 25000.0, 10.0, 27500.0),
                (ck_pid, "DIVISI 3 - BETON", "CK.B.01",
                 "Beton Mutu Sedang fc 20 MPa", "m3", 250.0, 1150000.0, 10.0, 1265000.0),
                (ck_pid, "DIVISI 4 - DINDING", "CK.4.1",
                 "Pasangan Dinding Bata Ringan", "m2", 1200.0, 145000.0, 10.0, 159500.0),
            ])

        # ---------- 4. 9 Komponen SMKK default (A-I) ----------
        cursor.execute("SELECT COUNT(*) FROM smkk_komponen WHERE proyek_id IS NULL")
        if cursor.fetchone()[0] == 0:
            default_komponen = [
                ("A", "Penyiapan Dokumen Penerapan SMKK", "Set", "persentase", 0.0015),
                ("B", "Sosialisasi, Promosi dan Pelatihan", "Ls", "persentase", 0.0030),
                ("C", "Alat Pelindung Kerja (APK) dan Alat Pelindung Diri (APD)", "Ls", "persentase", 0.0030),
                ("D", "Asuransi (Construction All Risk / CAR)", "Ls", "persentase", 0.0010),
                ("E", "Personel Keselamatan Konstruksi", "Orang-Bulan", "persentase", 0.0015),
                ("F", "Fasilitas Sarana, Prasarana dan Alat Kesehatan", "Set", "persentase", 0.0020),
                ("G", "Rambu dan Perlengkapan Lalu Lintas", "Ls", "persentase", 0.0015),
                ("H", "Konsultasi dengan Ahli Terkait Keselamatan Konstruksi", "Orang-Jam", "persentase", 0.0010),
                ("I", "Kegiatan dan Peralatan Terkait Pengendalian Risiko", "Ls", "persentase", 0.0015),
            ]
            cursor.executemany("""
                INSERT INTO smkk_komponen
                (kode, nama, satuan, tipe, nilai_default, nilai_kustom, proyek_id)
                VALUES (?, ?, ?, ?, ?, NULL, NULL)
            """, default_komponen)

        # ---------- 5. Sample Template AHSP & Detail ----------
        cursor.execute("SELECT COUNT(*) FROM analisis_ahsp_template")
        if cursor.fetchone()[0] == 0:
            # Bina Marga
            cursor.execute("""
                INSERT INTO analisis_ahsp_template
                (kode_pekerjaan, nama_pekerjaan, satuan, bidang, jenis)
                VALUES ('BM.3.1.1a',
                        'Galian Tanah Biasa Menggunakan Alat Berat',
                        'm3', 'Bina Marga', 'Informatif')
            """)
            bm_id = cursor.lastrowid

            # SDA
            cursor.execute("""
                INSERT INTO analisis_ahsp_template
                (kode_pekerjaan, nama_pekerjaan, satuan, bidang, jenis)
                VALUES ('SDA.01.g',
                        'Galian Tanah Biasa Mekanis',
                        'm3', 'Sumber Daya Air (SDA)', 'Informatif')
            """)
            sda_id = cursor.lastrowid

            # Cipta Karya
            cursor.execute("""
                INSERT INTO analisis_ahsp_template
                (kode_pekerjaan, nama_pekerjaan, satuan, bidang, jenis)
                VALUES ('CK.B.01',
                        'Membuat 1 m3 Beton Mutu Sedang fc 20 MPa (Slump 5 cm, Agregat Maks 19 mm)',
                        'm3', 'Cipta Karya', 'Informatif')
            """)
            ck_id = cursor.lastrowid

            sample_details = [
                # Bina Marga
                (bm_id, "L.01", 0.0750),
                (bm_id, "L.04", 0.0050),
                (bm_id, "E.10", 0.0071),
                (bm_id, "E.35", 0.1547),
                # SDA
                (sda_id, "L.01", 0.0520),
                (sda_id, "L.04", 0.0020),
                (sda_id, "E.10", 0.0098),
                # Cipta Karya (komposisi beton Lampiran II)
                (ck_id, "L.01", 1.6500),
                (ck_id, "L.02", 0.2750),
                (ck_id, "L.04", 0.0830),
                (ck_id, "M.12", 330.0000),
                (ck_id, "M.05.b", 0.5450),
                (ck_id, "E.06", 0.2500),
            ]
            cursor.executemany("""
                INSERT INTO analisis_ahsp_detail
                (template_id, komponen_kode, koefisien_standar)
                VALUES (?, ?, ?)
            """, sample_details)

        conn.commit()
        conn.close()