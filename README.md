# 🇮🇩 AHSP 47/2026 — Aplikasi Analisis Harga Satuan Pekerjaan

**Aplikasi internal untuk menyusun RAB / HPS Pekerjaan Konstruksi
sesuai SE Direktorat Jenderal Bina Konstruksi No. 47/SE/Dk/2026**
---

## 📋 Daftar Isi

- [Ringkasan](#-ringkasan)
- [Fitur Utama](#-fitur-utama)
- [Persyaratan Sistem](#-persyaratan-sistem)
- [Instalasi](#-instalasi)
  - [Setup Awal (Sekali Saja)](#setup-awal-sekali-saja)
  - [Menjalankan Aplikasi](#menjalankan-aplikasi)
  - [Verifikasi Instalasi](#verifikasi-instalasi)
- [Struktur Proyek](#-struktur-proyek)
- [Panduan Pengguna](#-panduan-pengguna)
  - [Alur Kerja Ideal](#alur-kerja-ideal)
  - [Tab 1 — Laporan HSP Balai](#tab-1--laporan-hsp-balai)
  - [Tab 2 — Lampiran I: Data HSP](#tab-2--lampiran-i-data-hsp)
  - [Tab 3 — Lampiran II: Tabel Acuan](#tab-3--lampiran-ii-tabel-acuan)
  - [Tab 4 — Lampiran III: Biaya SMKK](#tab-4--lampiran-iii-biaya-smkk)
  - [Tab 5 — Lampiran IV-VI: Kalkulator AHSP](#tab-5--lampiran-iv-vi-kalkulator-ahsp)
  - [Tab 6 — Lampiran VII: Pengajuan Usulan](#tab-6--lampiran-vii-pengajuan-usulan)
  - [Tab 7 — Rekapitulasi & Ekspor RAB](#tab-7--rekapitulasi--ekspor-rab)
- [Update Kode](#-update-kode)
- [Troubleshooting](#-troubleshooting)
- [FAQ](#-faq)
- [Backup & Restore Data](#-backup--restore-data)
- [Referensi Regulasi](#-referensi-regulasi)
- [Kontak Internal](#-kontak-internal)

---

## 🎯 Ringkasan

Aplikasi ini menggantikan proses manual penyusunan AHSP/RAB/HPS yang
sebelumnya menggunakan banyak file Excel terpisah. Semua perhitungan
mengikuti **Lampiran SE Dirjen Bina Konstruksi No. 47/SE/Dk/2026**
(perubahan dari SE 182/SE/Dk/2025).

| Lampiran | Isi | Tab di Aplikasi |
|---|---|---|
| I | Database Harga Satuan Pokok (HSP) | **Lampiran I: Data HSP** |
| II | Tabel Konversi & Produktivitas Alat | **Lampiran II: Tabel Acuan** |
| III | Biaya Penerapan SMKK (9 komponen A-I) | **Lampiran III: Biaya SMKK** |
| IV-VI | Kalkulator AHSP (SDA / Bina Marga / Cipta Karya) | **Lampiran IV-VI: Kalkulator AHSP** |
| VII | Pengajuan Usulan AHSP Baru/Perubahan | **Lampiran VII: Pengajuan Usulan** |
| — | Rekapitulasi + Ekspor Excel | **Rekapitulasi & Ekspor RAB** |

### Manfaat

- ✅ **Hemat waktu** — RAB yang biasanya 2-3 hari jadi 2-3 jam
- ✅ **Konsisten** — rumus SE 47/2026 ter-embed, tidak ada salah hitung manual
- ✅ **Traceable** — setiap item RAB bisa dilacak dari HSP mana
- ✅ **Integrasi** — HSP → AHSP → SMKK → RAB saling terhubung otomatis
- ✅ **Portabel** — berbasis Python, bisa dijalankan di Windows/Linux/macOS

---

## ✨ Fitur Utama

### 📊 Manajemen Data
- **CRUD HSP** (Harga Satuan Pokok) — Tenaga Kerja / Bahan / Peralatan
- **CRUD Acuan Konversi** — faktor asli/lepas/padat per jenis tanah
- **CRUD Proyek RAB** — multiple proyek dalam 1 aplikasi
- **CRUD Item RAB** — dari template AHSP atau manual

### 🧮 Kalkulator Otomatis
- **AHSP Terpadu** — Bidang SDA, Bina Marga, Cipta Karya
- **9 Komponen SMKK** — sesuai Lampiran III (A s.d. I)
- **Personel K3** — rekomendasi otomatis berdasarkan risiko & jumlah pekerja
- **Overhead & Profit** — 0-15%, default 10% sesuai contoh SE
- **PPN** — rekap di level RAB (bukan di AHSP)

### 💾 Ekspor
- **Excel (.xlsx)** — 3 blok: AHSP + SMKK + Rekap PPN
- **TXT** — ekspor AHSP blok I-VII, ekspor SMKK

### 🎨 UI/UX
- **Tema Kementerian PU** — biru `#004488` + aksen gold `#F5B301`
- **High-DPI aware** — cocok untuk layar 4K
- **Tabular navigation** — 7 tab linear sesuai lampiran

---

## 💻 Persyaratan Sistem

### Sistem Operasi
| OS | Status |
|---|---|
| Windows 10 / 11 (64-bit) | ✅ Rekomendasi |
| Linux (Ubuntu 22.04+) | ✅ Didukung |
| macOS (12+) | ✅ Didukung |

### Runtime
| Komponen | Versi |
|---|---|
| Python | **3.11.x** |
| PyQt5 | ≥ 5.15.9 |
| openpyxl | ≥ 3.1.0 |
| SQLite | built-in Python |

**💡 Catatan:** Aplikasi ini **tidak membutuhkan** pandas, numpy, atau
library scientific. Hanya **PyQt5** dan **openpyxl**.
Ringan, cepat, portabel.

### Resource
| Komponen | Minimal |
|---|---|
| RAM | 2 GB (rekomendasi 4 GB) |
| Disk | 200 MB (source + database) |
| Layar | 1280 × 720 |

---

## 📥 Instalasi

### Setup Awal (Sekali Saja)

#### Langkah 1 — Dapatkan Source Code

Minta ke **developer/tim IT** untuk meng-copy folder `ahsp_47_2026/`
ke komputer Anda. Letakkan di drive dengan akses tulis, contoh:

```
C:\ahsp_47_2026\
```

**Jangan** taruh di `C:\Program Files\` (butuh admin untuk tulis DB).

---

#### Langkah 2 — Install Python 3.11

**Cara A — Anaconda (Rekomendasi):**

1. Download **Anaconda** dari [anaconda.com](https://www.anaconda.com/products/individual)
2. Install (next → next → finish)
3. Buka **Anaconda Prompt** dari Start Menu

**Cara B — Python Official:**

1. Download **Python 3.11** dari [python.org](https://www.python.org/downloads/)
2. Saat install, **centang** ✅ "Add Python to PATH"
3. Klik "Install Now"

---

#### Langkah 3 — Buat Environment

**Jika pakai Anaconda:**

```powershell
# 1. Masuk ke folder project
cd C:\ahsp_47_2026

# 2. Buat environment dari file environment.yml
conda env create -f environment.yml

# 3. Aktifkan
conda activate ahsp47
```

**Jika pakai Python official:**

```powershell
# 1. Masuk ke folder project
cd C:\ahsp_47_2026

# 2. Buat virtual environment
python -m venv venv

# 3. Aktifkan
.\venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt
```

---

#### Langkah 4 — Inisialisasi Database

```powershell
# Pastikan environment aktif dulu
python -m database.migrations.run
```

**Ekspektasi output:**
```
============================================================
MIGRASI DATABASE ahsp_47_2026
SE Dirjen Bina Konstruksi No. 47/SE/Dk/2026
============================================================
>>> 001_add_jenis_to_template
  [OK] kolom jenis ditambahkan
...
MIGRASI SELESAI
============================================================
```

Database `database/ahsp_47_2026.db` otomatis dibuat dengan:
- 9 sample HSP
- 3 sample proyek (Bina Marga, SDA, Cipta Karya)
- 9 komponen SMKK default
- 3 template AHSP sample

---

### Menjalankan Aplikasi

Setiap kali mau pakai:

```powershell
# 1. Masuk folder project
cd C:\ahsp_47_2026

# 2. Aktifkan environment
conda activate ahsp47
# (atau: .\venv\Scripts\activate)

# 3. Jalankan aplikasi
python main.py
```

Jendela aplikasi akan terbuka dengan tema biru PU.

---

### Verifikasi Instalasi

Untuk cek apakah semua siap:

```powershell
python install_check.py
```

**Ekspektasi output:**
```
======================================================================
  RINGKASAN : 45 OK  |  2 WARN  |  0 FAIL
======================================================================
>>> Instalasi siap. Jalankan: python main.py
```

Kalau ada **[FAIL]** → perbaiki dulu sebelum pakai.

---

## 📂 Struktur Proyek

```
ahsp_47_2026/
│
├── main.py                        # Entry point — jalankan ini
├── install_check.py               # Verifikasi instalasi
├── environment.yml                # Conda env
├── requirements.txt               # Pip deps
├── README.md                      # File ini
│
├── config/                        # Konfigurasi aplikasi
│   ├── settings.py                # Path DB, versi, konstanta global
│   ├── constants.py               # Enum: kategori HSP, SMKK, bidang
│   └── theme.py                   # Tema UI (warna PU, stylesheet)
│
├── database/                      # Manajemen database SQLite
│   ├── db_manager.py              # Koneksi + migrasi + seed
│   ├── ahsp_47_2026.db            # File database (auto-generated)
│   └── migrations/
│       └── run.py                 # Migration runner
│
├── models/                        # Business logic
│   ├── hsp_model.py               # CRUD HSP
│   ├── acuan_model.py             # CRUD konversi tanah
│   ├── smkk_model.py              # Perhitungan SMKK + personel
│   ├── rab_model.py               # CRUD Proyek + Item RAB
│   ├── usulan_model.py            # CRUD usulan AHSP
│   ├── laporan_hsp_model.py       # CRUD BA penetapan HSP
│   ├── ahsp_engine.py             # Engine kalkulasi A-F
│   └── produktivitas_alat.py      # Rumus alat (Lampiran II)
│
├── views/                         # UI (PyQt5)
│   ├── main_window.py             # Window utama + tab manager
│   ├── tab_hsp.py                 # Tab Lampiran I
│   ├── tab_acuan.py               # Tab Lampiran II
│   ├── tab_smkk.py                # Tab Lampiran III
│   ├── tab_ahsp.py                # Tab Lampiran IV-VI
│   ├── tab_usulan.py              # Tab Lampiran VII
│   ├── tab_rab_export.py          # Tab Rekapitulasi & Ekspor
│   ├── tab_laporan_hsp.py         # Tab Laporan BA Balai
│   └── dialogs/
│       └── rab_dialogs.py         # Dialog Proyek / Item RAB
│
├── utils/                         # Utilitas
│   ├── helpers.py                 # format_rp, hitung_ahsp, dll
│   ├── exporter.py                # Excel exporter 3 blok
│   ├── validator.py               # Validasi input
│   └── ahsp_format.py             # Formatter blok I-VII
│
└── assets/                        # (opsional)
    └── icon.ico                   # Icon aplikasi
```

---

## 📚 Panduan Pengguna

### Alur Kerja Ideal

```
┌─────────────────────────────────────────────────────────────┐
│  [1] INPUT HSP        →  Tab Lampiran I: Data HSP            │
│      (Upah, Bahan, Peralatan dari survey)                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  [2] INPUT ACUAN      →  Tab Lampiran II: Tabel Acuan        │
│      (Faktor konversi tanah/bahan)                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  [3] BA PENETAPAN     →  Tab Laporan HSP Balai               │
│      (Nomor BA resmi penetapan HSP)                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  [4] BUAT PROYEK      →  Tab Rekapitulasi & Ekspor RAB       │
│      (Nama, lokasi, instansi, tahun anggaran)               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  [5] ISI ITEM RAB     →  Tab RAB → "+ Item dari Template"   │
│      (Pilih template AHSP, isi volume)                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  [6] HITUNG SMKK      →  Tab RAB → "⬆ Kirim ke Tab SMKK"    │
│      (Di Tab SMKK: Hitung → Simpan ke Proyek)               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  [7] REVIEW & EKSPOR  →  Tab RAB → "Ekspor ke Excel (.xlsx)"│
│      (File berisi 3 blok: AHSP + SMKK + Rekap PPN)          │
└─────────────────────────────────────────────────────────────┘
```

---

### Tab 1 — Laporan HSP Balai

**Fungsi:** Input Berita Acara Penetapan Harga Satuan Pokok dari Balai Teknis.

**Langkah:**
1. Isi **Nomor BA** (contoh: `BA.01/BALAI-SDA/X/2026`)
2. Isi **Nama Balai / UPT**
3. Isi **Tahun Anggaran** (contoh: `2026`)
4. Isi nama **Petugas Lapangan**, **Pengawas**, **Pengolah Data**
5. Isi **Tanggal Penetapan** (maks 31 Oktober sesuai SE)
6. Klik **"Simpan Berita Acara & Penetapan Data"**

Data akan muncul di tabel di bawah.

---

### Tab 2 — Lampiran I: Data HSP

**Fungsi:** Database Harga Satuan Pokok (upah, bahan, peralatan).

**Langkah Tambah Data:**
1. Klik **"+ Tambah Data"**
2. Isi:
   - **Kode** — format: `L.xx` (tenaga), `M.xx` (bahan), `E.xx` (peralatan)
   - **Uraian** — deskripsi komponen
   - **Kategori** — Tenaga Kerja / Bahan / Peralatan
   - **Satuan** — OH / m² / m³ / kg / jam / dll
   - **Harga Satuan**
   - **Sumber/Vendor**, **Tanggal Survei**
3. Klik **"Simpan"**

**Ubah Harga:**
1. Pilih baris → klik **"Ubah Harga"**
2. Ubah nilai → Simpan

**💡 Tips:** HSP ini jadi sumber harga untuk semua perhitungan AHSP
dan RAB. Kalau harga berubah, tinggal update di sini.

---

### Tab 3 — Lampiran II: Tabel Acuan

**Fungsi:** Faktor konversi tanah/bahan (asli / lepas / padat).

**Langkah:**
1. Klik **"+ Tambah Acuan"**
2. Isi **Jenis Tanah/Bahan** (contoh: `Pasir`, `Tanah Liat`)
3. Isi **Kondisi Semula** (contoh: `Asli (A)`)
4. Isi **Faktor Asli**, **Lepas**, **Padat** (contoh: `1.000`, `1.110`, `0.950`)
5. Simpan

---

### Tab 4 — Lampiran III: Biaya SMKK

**Fungsi:** Hitung Biaya Penerapan Sistem Manajemen Keselamatan Konstruksi (SMKK) — 9 komponen A s.d. I.

**Langkah:**
1. **Pilih Proyek** di combo atas (proyek dari Tab RAB)
2. Klik **"⬇ Muat dari Proyek"** — auto isi nama, nilai kontrak, risiko
3. Sesuaikan jika perlu:
   - **Nilai Proyek (HPS/Kontrak)** — sumber perhitungan SMKK
   - **Tingkat Risiko** — Kecil / Sedang / Besar
   - **Jumlah Tenaga Kerja** — untuk hitung personel K3
   - **PPN** — default 11%
4. Klik **"Hitung Biaya SMKK"**
5. Review tabel komponen A-I + personel K3 yang dibutuhkan
6. Klik **"💾 Simpan ke Proyek"** — supaya angka ini dipakai di Tab RAB

**Output:**
- **Section B** — Daftar personel K3 (Ahli K3, Petugas K3)
- **Section C** — Tabel 9 komponen SMKK dengan biaya
- **Section D** — Subtotal + PPN + Total

**⚠️ Penting:** Tanpa klik "Simpan ke Proyek", Tab RAB akan menghitung
SMKK sendiri (fallback pakai koefisien default). Selisih bisa terjadi
jika nilai kontrak ≠ subtotal AHSP.

---

### Tab 5 — Lampiran IV-VI: Kalkulator AHSP

**Fungsi:** Kalkulator AHSP terpadu untuk 3 bidang (SDA, Bina Marga, Cipta Karya).

**Langkah:**
1. Pilih **Bidang** (SDA / Bina Marga / Cipta Karya)
2. Pilih **Jenis** (Normatif / Informatif / Semua)
3. Pilih **Template Pekerjaan** dari combo
4. Lihat hasil kalkulasi di:
   - **Tabel kiri** — rincian komponen (Tenaga, Bahan, Peralatan)
   - **Preview kanan** — Blok I-VII lengkap (ASUMSI s.d. VOLUME)
   - **Panel bawah** — Rekap A, B, C, D, E, F
5. Sesuaikan **Overhead & Profit** (0-15%) jika perlu
6. Klik **"Ekspor AHSP"** untuk simpan ke `.txt`

**Rumus yang dipakai:**
```
A = Jumlah Harga Tenaga Kerja
B = Jumlah Harga Bahan
C = Jumlah Harga Peralatan
D = A + B + C
E = Overhead% × D       (default 10%)
F = D + E               (Harga Satuan Pekerjaan, BELUM PPN)
```

---

### Tab 6 — Lampiran VII: Pengajuan Usulan

**Fungsi:** Formulir usulan AHSP baru atau perubahan (mayor/minor).

**Langkah:**
1. Isi **Nomor Surat Usulan** (contoh: `UM.01/Balai-SDA/123/2026`)
2. Isi **Unit Pengusul** (Balai / Dinas / K/L/I)
3. Pilih **Jenis Usulan** — Baru / Perubahan Mayor / Perubahan Minor
4. Isi **Nama Item Pekerjaan**
5. Isi **Justifikasi Teknis** (alasan usulan)
6. Centang **SPTJM** jika melampirkan Surat Pernyataan
7. Klik **"Kirim Usulan AHSP"**

Data akan muncul di tabel di bawah.

---

### Tab 7 — Rekapitulasi & Ekspor RAB

**Fungsi:** Manajemen proyek + item RAB + ekspor Excel.

#### 7.1. Buat Proyek Baru

1. Klik **"+ Proyek Baru"**
2. Isi form:
   - **Nama Proyek** ⭐
   - **Lokasi** ⭐
   - **Instansi**
   - **Tahun Anggaran**
   - **Overhead Default** (10%)
   - **PPN Default** (11%)
3. Klik **OK**

#### 7.2. Tambah Item dari Template AHSP

1. Pilih proyek di combo
2. Klik **"+ Item dari Template AHSP"**
3. Pilih **Filter Bidang** (opsional)
4. Pilih **Template AHSP** dari combo
5. Isi **Divisi** (contoh: `DIVISI 1 - UMUM`)
6. Isi **Volume**
7. Sesuaikan **Overhead** jika perlu
8. Lihat **Preview D → F** (otomatis terupdate)
9. Klik **OK**

#### 7.3. Tambah Item Manual

1. Klik **"+ Item Manual"**
2. Isi: Divisi, Kode Item, Uraian, Satuan, Volume, Harga Dasar, Overhead
3. Lihat preview **F = D × (1 + oh%)**
4. Klik **OK**

#### 7.4. Edit / Hapus Item

- **Edit:** Double-click baris ATAU pilih + klik **"Edit Item"**
- **Hapus:** Pilih baris + klik **"- Hapus Item"**

#### 7.5. Kirim ke Tab SMKK

1. Pilih proyek
2. Klik **"⬆ Kirim ke Tab SMKK"**
3. Otomatis pindah ke Tab SMKK, proyek ter-select
4. Di Tab SMKK: **"⬇ Muat dari Proyek"** → **"Hitung"** → **"💾 Simpan"**

#### 7.6. Ekspor ke Excel

1. Pilih proyek
2. Sesuaikan **PPN** (spin box)
3. Klik **"Ekspor RAB/HPS ke Excel (.xlsx)"**
4. Pilih lokasi simpan → Save

**File Excel berisi 3 blok:**
- **Blok A** — AHSP per item pekerjaan
- **Blok B** — 9 komponen SMKK
- **Blok C** — Rekap RAB + PPN + Grand Total

---

## 🔄 Update Kode

Kalau ada update dari developer, **jangan langsung timpa** folder.
Ikuti prosedur berikut:

### 1. Backup Data Dulu

```powershell
# Backup database
Copy-Item database\ahsp_47_2026.db "D:\Backup\ahsp_47_$(Get-Date -Format 'yyyyMMdd').db"
```

### 2. Update Source Code

- Timpa semua file **kecuali** `database/ahsp_47_2026.db`
- Atau extract update ke folder baru, lalu copy `ahsp_47_2026.db` dari folder lama

### 3. Jalankan Migrasi

```powershell
conda activate ahsp47
python -m database.migrations.run
```

Migrasi akan menambahkan kolom/tabel baru tanpa menghapus data lama.

### 4. Verifikasi

```powershell
python install_check.py
python main.py
```

---

## 🔧 Troubleshooting

### ❌ `ModuleNotFoundError: PyQt5`

**Penyebab:** Environment belum aktif / PyQt5 belum install.

**Solusi:**
```powershell
conda activate ahsp47
pip install PyQt5 openpyxl
python main.py
```

---

### ❌ `sqlite3.ProgrammingError: Cannot operate on a closed database`

**Penyebab:** Bug di kode migrasi (sudah diperbaiki di v2.0).

**Solusi:** Pastikan `database/db_manager.py` versi terbaru (helper `_column_exists`
sudah self-contained).

---

### ❌ Data hilang setelah update

**Penyebab:** File `.db` ke-overwrite saat update kode.

**Solusi:** Selalu backup `ahsp_47_2026.db` sebelum update. Restore dari backup.

---

### ❌ Angka SMKK di Tab RAB berbeda dengan Tab SMKK

**Penyebab:** Tab RAB pakai fallback (belum "Simpan ke Proyek").

**Solusi:**
1. Buka Tab SMKK
2. Pilih proyek → **"⬇ Muat dari Proyek"**
3. Klik **"💾 Simpan ke Proyek"**
4. Kembali ke Tab RAB → angka sudah sync

---

### ❌ Export Excel error: "Permission denied"

**Penyebab:** File `.xlsx` sedang dibuka di Excel.

**Solusi:** Tutup file Excel, ekspor ulang dengan nama berbeda.

---

### ❌ Aplikasi tidak mau terbuka (tidak ada respon)

**Penyebab:** Python crash sebelum window muncul.

**Solusi:**
```powershell
# Jalankan di terminal untuk lihat error
python main.py
```
Traceback akan muncul di console. Kirim ke developer untuk diagnosa.

---

### ❌ Layar pecah / tampilan blur di 4K

**Penyebab:** High-DPI scaling belum diaktifkan.

**Solusi:** `main.py` sudah handle otomatis. Kalau masih blur:
```powershell
# Set environment variable sebelum run
$env:QT_AUTO_SCREEN_SCALE_FACTOR = "1"
python main.py
```

---

## ❓ FAQ

**Q: Apakah bisa jalan di Mac/Linux?**
A: Bisa. Install Python 3.11 + PyQt5 + openpyxl, jalankan `python main.py`.

**Q: Berapa banyak proyek yang bisa disimpan?**
A: Tidak ada batas. Semua tersimpan di 1 file SQLite lokal.

**Q: Apakah data bisa di-import dari Excel?**
A: Belum ada fitur import. Harus input manual. (Roadmap v2.1)

**Q: Apakah bisa export ke PDF?**
A: Belum ada. Saat ini hanya Excel (.xlsx) dan TXT. (Roadmap v2.1)

**Q: Bagaimana cara reset database (mulai dari nol)?**
A:
```powershell
Remove-Item database\ahsp_47_2026.db
python -m database.migrations.run
```

**Q: File database disimpan di mana?**
A: Di `database/ahsp_47_2026.db` (relatif terhadap root project).

**Q: Apakah bisa dipakai 2 orang sekaligus?**
A: Tidak. SQLite single-user. Untuk multi-user, perlu migrasi ke
   PostgreSQL/MySQL (Roadmap v2.2).

**Q: Apakah aplikasi ini bisa disebar ke pihak luar?**
A: **Tidak.** Aplikasi ini **internal use only**. Dilarang disebar
   tanpa izin tertulis.

---

## 💾 Backup & Restore Data

### Backup Manual

```powershell
# Copy file database ke folder backup
Copy-Item database\ahsp_47_2026.db "D:\Backup\ahsp_47_$(Get-Date -Format 'yyyyMMdd_HHmmss').db"
```

Atau copy-paste manual file `database\ahsp_47_2026.db` ke flashdisk.

### Backup Otomatis (Windows Task Scheduler)

1. Buka **Task Scheduler** (cari di Start Menu)
2. Create Basic Task → nama: `Backup AHSP 47`
3. Trigger: **Daily**, jam 17:00
4. Action: Start a program → `powershell.exe`
5. Arguments:
   ```
   -Command "Copy-Item 'C:\ahsp_47_2026\database\ahsp_47_2026.db' 'D:\Backup\ahsp_47_$(Get-Date -Format yyyyMMdd).db'"
   ```

### Restore

```powershell
# Replace database dengan file backup
Copy-Item "D:\Backup\ahsp_47_20260911.db" database\ahsp_47_2026.db -Force
```

---

## 📊 Referensi Regulasi

Aplikasi ini mengacu pada:

- **SE Dirjen Bina Konstruksi No. 47/SE/Dk/2026** tanggal 13 Februari 2026
  tentang *Petunjuk Teknis Penyusunan Perkiraan Biaya Pekerjaan Konstruksi
  Bidang Pekerjaan Umum*
- **SE 182/SE/Dk/2025** (dicabut oleh SE 47/2026)
- Lampiran I-VII SE 47/2026

**Dokumen terkait:**
- Peraturan Menteri PUPR No. 8/2023 tentang Pedoman Penyusunan Perkiraan Biaya
- Peraturan Menteri PUPR No. 10/2021 tentang SMKK
- PP No. 14/2021 tentang Perubahan atas PP No. 22/2020 tentang Peraturan
  Pelaksanaan UU Cipta Kerja

---

## 👥 Kontak Internal

**Pelaporan Bug / Saran:**
Kirim ke Komentar dengan subjek: `[BUG] AHSP 47 - <deskripsi singkat>`

---

## 📄 Lisensi

Dilarang diperjualbelikan / disebar ke pihak luar tanpa izin tertulis
dari pengembang.

---

## 🗺️ Roadmap

### v2.1 (Target: Q2 2026)
- [ ] Import HSP dari Excel
- [ ] Export RAB ke PDF berkop SE 47
- [ ] Upload 7 dokumen pendukung Lampiran VII
- [ ] Integrasi tab AHSP → RAB (tombol "Tambah ke Proyek" di tab AHSP)

### v2.2 (Target: Q3 2026)
- [ ] Multi-user (login per user)
- [ ] Versioning / audit trail
- [ ] Template proyek (favorit)
- [ ] Sinkronisasi ke server internal

### v3.0 (Target: Q4 2026)
- [ ] Migrasi ke PostgreSQL untuk multi-user
- [ ] API untuk integrasi SIPASTI
- [ ] Dashboard analitik (grafik tren harga)

---

**Dibuat dengan ❤️ untuk efisiensi pekerjaan konstruksi Indonesia**

*Versi 2.0.0 — September 2026*

---