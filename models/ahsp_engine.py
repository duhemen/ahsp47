# models/ahsp_engine.py
"""
Engine tunggal untuk analisis AHSP SE 47/SE/Dk/2026.

Menggabungkan:
  • HSP dari database (Lampiran I)
  • Produktivitas alat (Lampiran II)
  • Kategori Tenaga/Bahan/Peralatan
  • Kalkulasi A s.d F
  • Rekap RAB (PPN di level rekap, bukan AHSP)
"""

from utils.helpers import hitung_ahsp, hitung_rekap_rab
from models.produktivitas_alat import ProduktivitasAlat
from models.hsp_model import HSPModel
from config.constants import (
    KATEGORI_TENAGA, KATEGORI_BAHAN, KATEGORI_PERALATAN,
)


class AHSPEngine:
    """Fasad (facade) untuk seluruh operasi AHSP."""

    def __init__(self):
        self.hsp = HSPModel()
        self.prod = ProduktivitasAlat()

    # ==========================================================
    # HARGA SATUAN DASAR (dari HSP)
    # ==========================================================
    def harga(self, kode_hsp: str) -> float:
        """Ambil harga satuan HSP (0.0 jika tidak ditemukan)."""
        h = self.hsp.get_hsp_price(kode_hsp)
        return float(h) if h is not None else 0.0

    # ==========================================================
    # BAGIAN A — TENAGA KERJA
    # ==========================================================
    def hitung_tenaga(self, komponen_tenaga: list) -> float:
        """
        Args:
            komponen_tenaga: [{'kode': 'L.01', 'koef': 0.0750}, ...]
        Returns:
            float  — total harga A
        """
        return sum(
            float(k.get("koef", 0)) * self.harga(k.get("kode", ""))
            for k in komponen_tenaga or []
        )

    # ==========================================================
    # BAGIAN B — BAHAN
    # ==========================================================
    def hitung_bahan(self, komponen_bahan: list) -> float:
        return sum(
            float(k.get("koef", 0)) * self.harga(k.get("kode", ""))
            for k in komponen_bahan or []
        )

    # ==========================================================
    # BAGIAN C — PERALATAN
    # ==========================================================
    def hitung_peralatan(self, komponen_alat: list) -> float:
        return sum(
            float(k.get("koef", 0)) * self.harga(k.get("kode", ""))
            for k in komponen_alat or []
        )

    # ==========================================================
    # BAGIAN D, E, F
    # ==========================================================
    def hitung_hsp(self, tenaga: float, bahan: float, alat: float,
                   overhead_pct: float = 10.0) -> dict:
        """
        D = A + B + C
        E = overhead_pct% × D
        F = D + E   (harga satuan pekerjaan, tanpa PPN)
        """
        a = float(tenaga or 0)
        b = float(bahan or 0)
        c = float(alat or 0)
        d = a + b + c
        e, f = hitung_ahsp(d, overhead_pct)
        return {
            "A_tenaga": round(a, 2),
            "B_bahan": round(b, 2),
            "C_alat": round(c, 2),
            "D_jumlah": round(d, 2),
            "E_overhead_pct": float(overhead_pct),
            "E_overhead": round(e, 2),
            "F_hsp": round(f, 2),
        }

    # ==========================================================
    # EKSEKUSI PENUH DARI SATU TEMPLATE
    # ==========================================================
    def hitung_dari_template(self, template_id: int, overhead_pct: float = 10.0) -> dict:
        """
        Ambil rincian komponen dari `analisis_ahsp_detail`,
        hitung A, B, C, D, E, F.

        Return dict lengkap dengan `komponen` list untuk verifikasi.
        """
        conn = self.hsp.db.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT d.koefisien_standar AS koef,
                       h.kode, h.uraian, h.kategori, h.satuan, h.harga_satuan
                FROM analisis_ahsp_detail d
                JOIN hsp_data h ON d.komponen_kode = h.kode
                WHERE d.template_id = ?
            """, (template_id,))
            rows = cur.fetchall()
        finally:
            conn.close()

        tenaga = bahan = alat = 0.0
        komponen = []
        for r in rows:
            subtotal = float(r["koef"]) * float(r["harga_satuan"])
            kat = r["kategori"]
            if kat == KATEGORI_TENAGA:
                tenaga += subtotal
            elif kat == KATEGORI_BAHAN:
                bahan += subtotal
            elif kat == KATEGORI_PERALATAN:
                alat += subtotal

            komponen.append({
                "kode": r["kode"],
                "uraian": r["uraian"],
                "kategori": kat,
                "satuan": r["satuan"],
                "koefisien": float(r["koef"]),
                "harga": float(r["harga_satuan"]),
                "subtotal": round(subtotal, 2),
            })

        hasil = self.hitung_hsp(tenaga, bahan, alat, overhead_pct)
        hasil["komponen"] = komponen
        return hasil

    # ==========================================================
    # REKAP RAB (PPN di level rekap)
    # ==========================================================
    def rekap_rab(self, items: list, ppn_pct: float = 11.0) -> dict:
        """
        Rekap RAB/HPS di level proyek. Lihat utils.helpers.hitung_rekap_rab.
        """
        return hitung_rekap_rab(items, ppn_pct=ppn_pct)