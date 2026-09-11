# config/constants.py
"""
Konstanta & enum untuk Aplikasi AHSP SE 47/SE/Dk/2026.

Modul ini menjadi satu-satunya sumber kebenaran (single source of truth)
untuk:
  • kategori HSP
  • jenis AHSP (Normatif/Informatif)
  • jenis usulan AHSP
  • 9 komponen SMKK (Lampiran III)
  • rasio personel SMKK berdasarkan tingkat risiko
"""

# ==========================================================
# KATEGORI HSP (Lampiran I)
# ==========================================================
KATEGORI_TENAGA = "Tenaga Kerja"
KATEGORI_BAHAN = "Bahan"
KATEGORI_PERALATAN = "Peralatan"

KATEGORI_VALID = (KATEGORI_TENAGA, KATEGORI_BAHAN, KATEGORI_PERALATAN)

# Awalan kode HSP (untuk validasi)
AWALAN_KODE = {
    "L": KATEGORI_TENAGA,       # L.01 = Pekerja
    "M": KATEGORI_BAHAN,        # M.12 = Semen
    "E": KATEGORI_PERALATAN,    # E.10 = Excavator
    "A": KATEGORI_BAHAN,        # alias alternatif
    "B": KATEGORI_BAHAN,
    "P": KATEGORI_PERALATAN,
}

# ==========================================================
# JENIS AHSP (Lampiran V/VI — kolom NORMATIF / INFORMATIF)
# ==========================================================
NORMATIF = "Normatif"
INFORMATIF = "Informatif"
JENIS_AHSP_VALID = (NORMATIF, INFORMATIF)

# ==========================================================
# JENIS USULAN AHSP (Huruf L)
# ==========================================================
USULAN_BARU = "Baru"
USULAN_MAYOR = "Perubahan Mayor"
USULAN_MINOR = "Perubahan Minor"
USULAN_VALID = (USULAN_BARU, USULAN_MAYOR, USULAN_MINOR)

# ==========================================================
# DOKUMEN PENDUKUNG USULAN (Huruf L.11)
# ==========================================================
DOKUMEN_USULAN = [
    ("tabel_usulan", "Tabel Usulan AHSP (asumsi bahan, peralatan, tenaga kerja, metode)"),
    ("justifikasi_teknis", "Justifikasi Teknis (analisis produktivitas alat & tenaga kerja)"),
    ("spesifikasi", "Spesifikasi yang diacu"),
    ("tabel_referensi", "Tabel Referensi yang digunakan"),
    ("berita_acara", "Berita Acara Pembahasan oleh Tim Pembahas"),
    ("screenshot_sipasti", "Bukti Usulan AHSP di dalam SIPASTI (tangkapan layar)"),
    ("surat_pernyataan", "Surat Pernyataan Kelengkapan Berkas & Kebenaran Substansi Teknis"),
]

# ==========================================================
# BIDANG
# ==========================================================
BIDANG_SDA = "Sumber Daya Air (SDA)"
BIDANG_BM = "Bina Marga"
BIDANG_CK = "Cipta Karya"

BIDANG_VALID = (BIDANG_SDA, BIDANG_BM, BIDANG_CK)

# ==========================================================
# 9 KOMPONEN SMKK (Lampiran III Tabel III.1 — Kode A s.d I)
# ==========================================================
# Catatan: 'sub' tidak dipakai untuk perhitungan, hanya keterangan.
SMKK_KOMPONEN = [
    {
        "kode": "A",
        "nama": "Penyiapan Dokumen Penerapan SMKK",
        "sub": "RKK, RMPK, RKPPL, RMLLP, prosedur, formulir, laporan bulanan",
    },
    {
        "kode": "B",
        "nama": "Sosialisasi, Promosi dan Pelatihan",
        "sub": "Induksi, briefing, TBM, awareness, simulasi tanggap darurat, banner, poster",
    },
    {
        "kode": "C",
        "nama": "Alat Pelindung Kerja (APK) dan Alat Pelindung Diri (APD)",
        "sub": "Safety net, life line, guard railing, safety deck, helm, rompi, sepatu, dll",
    },
    {
        "kode": "D",
        "nama": "Asuransi (Construction All Risk / CAR)",
        "sub": "Minimal 0,1% dari nilai proyek (SSUK) + asuransi pihak ketiga",
    },
    {
        "kode": "E",
        "nama": "Personel Keselamatan Konstruksi",
        "sub": "Ahli K3 Konstruksi, Petugas K3, Petugas Tanggap Darurat, P3K, Flagman, dll",
    },
    {
        "kode": "F",
        "nama": "Fasilitas, Sarana, Prasarana dan Alat Kesehatan",
        "sub": "P3K, klinik, ambulans, wastafel, handy transceiver, fogging",
    },
    {
        "kode": "G",
        "nama": "Rambu dan Perlengkapan Lalu Lintas",
        "sub": "Rambu petunjuk/larangan/peringatan/kewajiban/informasi, cone, barrier",
    },
    {
        "kode": "H",
        "nama": "Konsultasi dengan Ahli Terkait Keselamatan Konstruksi",
        "sub": "Ahli Lingkungan, Geoteknik, Gempa, Bendungan, Jembatan, Gedung, dll",
    },
    {
        "kode": "I",
        "nama": "Kegiatan dan Peralatan Terkait Pengendalian Risiko",
        "sub": "Manajemen mutu, testing & commissioning, APAR, penangkal petir, CCTV, washing bay",
    },
]

SMKK_KODE_VALID = [k["kode"] for k in SMKK_KOMPONEN]  # ['A', ..., 'I']

# ==========================================================
# RASIO PERSONEL SMKK (Lampiran III — halaman 100)
# ==========================================================
# Rasio = jumlah pekerja per 1 petugas K3 Konstruksi.
RASIO_PETUGAS_K3 = {
    "Kecil": 60,   # 1 petugas per 60 pekerja
    "Sedang": 50,  # 1 petugas per 50 pekerja
    "Besar": 40,   # 1 petugas per 40 pekerja
}

# ==========================================================
# TINGKAT RISIKO SMKK
# ==========================================================
RISIKO_KECIL = "Kecil"
RISIKO_SEDANG = "Sedang"
RISIKO_BESAR = "Besar"
RISIKO_VALID = (RISIKO_KECIL, RISIKO_SEDANG, RISIKO_BESAR)

# Jumlah minimum APAR per tingkat risiko (contoh, Lampiran III)
APAR_MINIMUM = {
    "Kecil": {"A": 1},
    "Sedang": {"A": 3, "B": 1, "C": 1, "D": 0},
    "Besar": {"A": 5, "B": 2, "C": 1, "D": 1},
}