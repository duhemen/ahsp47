# models/smkk_model.py
"""
Model Biaya Penerapan SMKK — Lampiran III SE 47/SE/Dk/2026.

Menyediakan:
  • get_all_komponen()   → daftar 9 komponen (A-I) dari DB
  • get_komponen_9()     → daftar 9 komponen dari konstanta
  • hitung_personel()    → kebutuhan personel per tingkat risiko
  • hitung_total()       → kalkulasi lengkap SMKK
  • add/update/delete    → CRUD komponen
"""

from database.db_manager import DBManager
from config.constants import (
    SMKK_KOMPONEN,
    RASIO_PETUGAS_K3,
    RISIKO_KECIL,
    RISIKO_SEDANG,
    RISIKO_BESAR,
)


class SMKKModel:
    """Model untuk Biaya Penerapan SMKK (Lampiran III SE 47/2026)."""

    # ==========================================================
    # KOEFISIEN DEFAULT 9 KOMPONEN (A-I)
    # ==========================================================
    KOEF_DEFAULT = {
        "A": 0.0015,   # Penyiapan Dokumen
        "B": 0.0030,   # Sosialisasi, Promosi, Pelatihan
        "C": 0.0030,   # APK & APD
        "D": 0.0010,   # Asuransi CAR (min 0,1%)
        "E": 0.0015,   # Personel Keselamatan Konstruksi
        "F": 0.0020,   # Fasilitas Kesehatan
        "G": 0.0015,   # Rambu & Perlengkapan Lalu Lintas
        "H": 0.0010,   # Konsultasi Ahli
        "I": 0.0015,   # Kegiatan & Peralatan Pengendalian Risiko
    }

    def __init__(self):
        self.db = DBManager()

    # ==========================================================
    # READ — 9 KOMPONEN DARI DATABASE
    # ==========================================================
    def get_all_komponen(self):
        """
        Ambil 9 komponen SMKK default (proyek_id IS NULL) dari DB.
        Return: list of dict {'kode', 'nama', 'satuan', 'tipe',
                              'nilai_default', 'nilai_kustom'}
        """
        conn = None
        try:
            conn = self.db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT kode, nama, satuan, tipe, nilai_default, nilai_kustom
                FROM smkk_komponen
                WHERE proyek_id IS NULL
                ORDER BY kode ASC
            """)
            rows = cur.fetchall()
            hasil = []
            for r in rows:
                hasil.append({
                    "kode": r["kode"],
                    "nama": r["nama"],
                    "satuan": r["satuan"] or "Ls",
                    "tipe": r["tipe"] or "persentase",
                    "nilai_default": float(r["nilai_default"] or 0),
                    "nilai_kustom": float(r["nilai_kustom"]) if r["nilai_kustom"] is not None else None,
                })
            return hasil
        except Exception as e:
            print(f"[ERROR] get_all_komponen: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_komponen_9(self):
        """Ambil 9 komponen dari konstanta (tanpa DB)."""
        return list(SMKK_KOMPONEN)

    def get_komponen_by_kode(self, kode: str):
        """Ambil 1 komponen berdasarkan kode."""
        conn = None
        try:
            conn = self.db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT kode, nama, satuan, tipe, nilai_default, nilai_kustom
                FROM smkk_komponen
                WHERE kode = ? AND proyek_id IS NULL
            """, (kode,))
            r = cur.fetchone()
            if not r:
                return None
            return {
                "kode": r["kode"],
                "nama": r["nama"],
                "satuan": r["satuan"] or "Ls",
                "tipe": r["tipe"] or "persentase",
                "nilai_default": float(r["nilai_default"] or 0),
                "nilai_kustom": float(r["nilai_kustom"]) if r["nilai_kustom"] is not None else None,
            }
        except Exception as e:
            print(f"[ERROR] get_komponen_by_kode: {e}")
            return None
        finally:
            if conn:
                conn.close()

    # ==========================================================
    # PERSONEL BERDASARKAN RISIKO (Lampiran III hlm. 100)
    # ==========================================================
    def hitung_personel(self, jumlah_pekerja: int, risiko: str):
        """
        Return list of dict {'peran', 'jumlah', 'keterangan'}.
        """
        hasil = []

        if risiko == RISIKO_KECIL:
            jml = max(1, -(-jumlah_pekerja // RASIO_PETUGAS_K3["Kecil"]))
            hasil.append({
                "peran": "Petugas K3 Konstruksi / Petugas Keselamatan Konstruksi",
                "jumlah": jml,
                "keterangan": f"1 petugas per {RASIO_PETUGAS_K3['Kecil']} pekerja",
            })

        elif risiko == RISIKO_SEDANG:
            hasil.append({
                "peran": "Ahli K3 Konstruksi / Ahli Keselamatan Konstruksi Muda",
                "jumlah": 1,
                "keterangan": "Pimpinan UKK",
            })
            jml = max(1, -(-jumlah_pekerja // RASIO_PETUGAS_K3["Sedang"]))
            hasil.append({
                "peran": "Petugas K3 Konstruksi / Petugas Keselamatan Konstruksi",
                "jumlah": jml,
                "keterangan": f"1 petugas per {RASIO_PETUGAS_K3['Sedang']} pekerja",
            })

        else:  # BESAR
            hasil.append({
                "peran": "Ahli K3 Konstruksi / Ahli Keselamatan Konstruksi Utama atau Madya",
                "jumlah": 1,
                "keterangan": "Pimpinan UKK (pengalaman ≥ 3 tahun)",
            })
            jml = max(1, -(-jumlah_pekerja // RASIO_PETUGAS_K3["Besar"]))
            hasil.append({
                "peran": "Petugas K3 Konstruksi / Petugas Keselamatan Konstruksi",
                "jumlah": jml,
                "keterangan": f"1 petugas per {RASIO_PETUGAS_K3['Besar']} pekerja",
            })
            if jumlah_pekerja > 100:
                hasil.append({
                    "peran": "Ahli K3 Konstruksi Madya / Ahli Keselamatan Konstruksi Madya",
                    "jumlah": 1,
                    "keterangan": "Tambahan untuk > 100 pekerja (pengalaman ≥ 3 tahun)",
                })

        return hasil

    # ==========================================================
    # KALKULASI TOTAL SMKK
    # ==========================================================
    def hitung_total(self, nilai_proyek: float, risiko: str = RISIKO_SEDANG,
                     jumlah_pekerja: int = 0):
        """
        Hitung 9 komponen SMKK berdasarkan nilai proyek.
        Return: dict {'risiko', 'komponen', 'personel', 'subtotal',
                      'persen', 'ppn', 'total'}
        """
        if nilai_proyek <= 0:
            return {
                "risiko": risiko,
                "komponen": [],
                "personel": [],
                "subtotal": 0.0,
                "persen": 0.0,
                "ppn": 0.0,
                "total": 0.0,
                "error": "Nilai proyek harus > 0",
            }

        # Ambil komponen dari DB
        komponen_db = self.get_all_komponen()

        # Kalau DB kosong, fallback ke konstanta
        if not komponen_db:
            komponen_db = [
                {"kode": k["kode"], "nama": k["nama"], "satuan": "Ls",
                 "tipe": "persentase",
                 "nilai_default": self.KOEF_DEFAULT.get(k["kode"], 0),
                 "nilai_kustom": None}
                for k in SMKK_KOMPONEN
            ]

        detail = []
        subtotal = 0.0
        for k in komponen_db:
            koef = (k["nilai_kustom"] if k["nilai_kustom"] is not None
                    else k["nilai_default"])
            biaya = nilai_proyek * float(koef)
            detail.append({
                "kode": k["kode"],
                "nama": k["nama"],
                "satuan": k["satuan"],
                "koefisien": float(koef),
                "biaya": round(biaya, 2),
            })
            subtotal += biaya

        personel = self.hitung_personel(jumlah_pekerja, risiko) if jumlah_pekerja else []

        return {
            "risiko": risiko,
            "komponen": detail,
            "personel": personel,
            "subtotal": round(subtotal, 2),
            "persen": round((subtotal / nilai_proyek) * 100, 4) if nilai_proyek else 0.0,
            "ppn": 0.0,   # dihitung di rekap akhir
            "total": round(subtotal, 2),
        }

    # ==========================================================
    # CRUD — ADD / UPDATE / DELETE
    # ==========================================================
    def add_komponen(self, data):
        """Tambah komponen SMKK baru."""
        conn = None
        try:
            conn = self.db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO smkk_komponen
                (kode, nama, satuan, tipe, nilai_default, nilai_kustom, proyek_id)
                VALUES (?, ?, ?, ?, ?, ?, NULL)
            """, (
                data["kode"],
                data["nama"],
                data.get("satuan", "Ls"),
                data.get("tipe", "persentase"),
                float(data.get("nilai_default", 0) or 0),
                data.get("nilai_kustom"),
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"[ERROR] add_komponen: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    def update_nilai_komponen(self, kode, nama, nilai_default, nilai_kustom):
        """Update komponen SMKK berdasarkan kode."""
        conn = None
        try:
            conn = self.db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                UPDATE smkk_komponen
                SET nama = ?, nilai_default = ?, nilai_kustom = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE kode = ? AND proyek_id IS NULL
            """, (nama, float(nilai_default or 0), nilai_kustom, kode))
            conn.commit()
            return cur.rowcount > 0
        except Exception as e:
            print(f"[ERROR] update_nilai_komponen: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    def delete_komponen(self, kode):
        """Hapus komponen SMKK default berdasarkan kode."""
        conn = None
        try:
            conn = self.db.get_connection()
            cur = conn.cursor()
            cur.execute(
                "DELETE FROM smkk_komponen WHERE kode = ? AND proyek_id IS NULL",
                (kode,),
            )
            conn.commit()
            return cur.rowcount > 0
        except Exception as e:
            print(f"[ERROR] delete_komponen: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    # ==========================================================
    # RESET / SEED
    # ==========================================================
    def reset_to_default(self):
        """Hapus semua komponen dan seed ulang 9 komponen default."""
        conn = None
        try:
            conn = self.db.get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM smkk_komponen WHERE proyek_id IS NULL")
            for k in SMKK_KOMPONEN:
                cur.execute("""
                    INSERT INTO smkk_komponen
                    (kode, nama, satuan, tipe, nilai_default, nilai_kustom, proyek_id)
                    VALUES (?, ?, ?, ?, ?, NULL, NULL)
                """, (
                    k["kode"], k["nama"], "Ls", "persentase",
                    self.KOEF_DEFAULT.get(k["kode"], 0.001),
                ))
            conn.commit()
            return True
        except Exception as e:
            print(f"[ERROR] reset_to_default: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    # ==========================================================
    # INTEGRASI PROYEK — SIMPAN & AMBIL
    # ==========================================================
    def save_to_proyek(self, proyek_id, nama_proyek, nilai_proyek,
                       risiko, jumlah_pekerja, komponen,
                       subtotal, ppn, total):
        """
        Simpan hasil perhitungan SMKK ke tabel smkk_proyek.
        Return: id baris smkk_proyek.
        """
        import json
        conn = self.db.get_connection()
        try:
            cur = conn.cursor()
            # Hapus hasil lama untuk proyek ini (kalau ada)
            cur.execute(
                "DELETE FROM smkk_proyek WHERE nama_proyek = ? "
                "AND nilai_proyek = ?",
                (nama_proyek, float(nilai_proyek))
            )
            cur.execute("""
                INSERT INTO smkk_proyek
                (nama_proyek, nilai_proyek, risiko, jumlah_pekerja,
                 subtotal_smkk, ppn, total_smkk, detail_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                nama_proyek, float(nilai_proyek), risiko, int(jumlah_pekerja),
                float(subtotal), float(ppn), float(total),
                json.dumps(komponen, ensure_ascii=False),
            ))
            conn.commit()
            new_id = cur.lastrowid

            # Update cache di proyek_rab (kalau ada kolom smkk_total)
            try:
                cur.execute(
                    "UPDATE proyek_rab SET smkk_total = ? WHERE id = ?",
                    (float(total), proyek_id)
                )
                conn.commit()
            except Exception:
                pass  # kolom belum ada, skip

            return new_id
        finally:
            conn.close()

    def get_by_proyek(self, proyek_id):
        """
        Ambil hasil SMKK terakhir untuk proyek tertentu.
        Return: dict atau None kalau belum pernah disimpan.
        """
        import json
        conn = self.db.get_connection()
        try:
            # Ambil dulu info proyek untuk match
            cur = conn.cursor()
            cur.execute(
                "SELECT nama_proyek, nilai_kontrak FROM proyek_rab WHERE id = ?",
                (proyek_id,)
            )
            row = cur.fetchone()
            if not row:
                return None

            nama = row["nama_proyek"]
            nilai = float(row["nilai_kontrak"] or 0)

            # Cari hasil SMKK yang match dengan proyek ini
            cur.execute("""
                SELECT * FROM smkk_proyek
                WHERE nama_proyek = ?
                ORDER BY id DESC LIMIT 1
            """, (nama,))
            r = cur.fetchone()
            if not r:
                return None

            return {
                "id": r["id"],
                "nama_proyek": r["nama_proyek"],
                "nilai_proyek": float(r["nilai_proyek"]),
                "risiko": r["risiko"],
                "jumlah_pekerja": r["jumlah_pekerja"],
                "subtotal": float(r["subtotal_smkk"] or 0),
                "ppn": float(r["ppn"] or 0),
                "total": float(r["total_smkk"] or 0),
                "komponen": json.loads(r["detail_json"] or "[]"),
                "created_at": r["created_at"],
            }
        finally:
            conn.close()