# utils/helpers.py
"""
Fungsi bantu umum untuk aplikasi AHSP SE 47/SE/Dk/2026.
"""

from config.settings import (
    DEFAULT_OVERHEAD_PROFIT,
    OVERHEAD_PROFIT_MIN,
    OVERHEAD_PROFIT_MAX,
    DEFAULT_PPN,
)


# ==========================================================
# FORMAT & PARSE RUPIAH
# ==========================================================
def format_rp(val):
    """Format angka menjadi 'Rp 1.234.567,89'."""
    try:
        return f"Rp {float(val):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return "Rp 0,00"


def parse_rp(text):
    """Kebalikan dari format_rp — 'Rp 1.234,56' → 1234.56."""
    if not text:
        return 0.0
    try:
        t = str(text).strip().replace("Rp", "").replace(" ", "").replace(".", "")
        if "," in t:
            t = t.replace(",", ".")
        return float(t)
    except ValueError:
        return 0.0


def format_angka(val, desimal=4):
    """Format angka Indonesia tanpa prefix Rp."""
    try:
        return f"{float(val):,.{desimal}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return "0"


# ==========================================================
# KALKULASI AHSP (SE 47/SE/Dk/2026)
# ==========================================================
def hitung_ahsp(jumlah_d, overhead_pct=DEFAULT_OVERHEAD_PROFIT):
    """
    Hitung E dan F sesuai SE 47/SE/Dk/2026 (Lampiran V contoh AHSP).

        D = A + B + C  (Tenaga + Bahan + Peralatan)
        E = overhead_pct% × D
        F = D + E      (Harga Satuan Pekerjaan — BELUM PPN)

    Args:
        jumlah_d (float)   : D = A + B + C
        overhead_pct (float): Persentase Overhead & Profit (default 10.0)

    Returns:
        tuple (E, F) — (nilai_overhead, harga_satuan_pekerjaan)
    """
    try:
        d = float(jumlah_d)
    except (TypeError, ValueError):
        d = 0.0

    try:
        pct = float(overhead_pct)
    except (TypeError, ValueError):
        pct = DEFAULT_OVERHEAD_PROFIT

    overhead_val = d * (pct / 100.0)
    hsp_f = d + overhead_val
    return round(overhead_val, 2), round(hsp_f, 2)


def hitung_rekap_rab(items, overhead_default=DEFAULT_OVERHEAD_PROFIT, ppn_pct=DEFAULT_PPN):
    """
    Rekap RAB/HPS di tingkat proyek. PPN ditambahkan di sini — bukan di AHSP.

    Args:
        items (list[dict]): tiap item berisi minimal
            {'volume': float, 'harga_dasar': float, 'overhead_pct': float}
        overhead_default : fallback overhead jika item tidak memuat
        ppn_pct          : persentase PPN (default 11%)

    Returns:
        dict {
            'subtotal_d'      : Σ (volume × harga_dasar)
            'total_overhead'  : Σ (volume × harga_dasar × overhead_pct/100)
            'subtotal_e'      : subtotal_d + total_overhead   (= F)
            'ppn_pct'         : ppn_pct
            'ppn_val'         : subtotal_e × ppn_pct/100
            'grand_total'     : subtotal_e + ppn_val
        }
    """
    subtotal_d = 0.0
    total_overhead = 0.0

    for it in items or []:
        try:
            vol = float(it.get("volume", 0) or 0)
            hd = float(it.get("harga_dasar", 0) or 0)
            oh = float(it.get("overhead_pct", overhead_default) or overhead_default)
        except (TypeError, ValueError):
            continue
        subtotal_d += vol * hd
        total_overhead += vol * hd * (oh / 100.0)

    subtotal_e = subtotal_d + total_overhead
    ppn = subtotal_e * (float(ppn_pct) / 100.0)

    return {
        "subtotal_d": round(subtotal_d, 2),
        "total_overhead": round(total_overhead, 2),
        "subtotal_e": round(subtotal_e, 2),
        "ppn_pct": float(ppn_pct),
        "ppn_val": round(ppn, 2),
        "grand_total": round(subtotal_e + ppn, 2),
    }


# ==========================================================
# VALIDASI
# ==========================================================
def validate_overhead_profit(val):
    """Pastikan overhead antara OVERHEAD_PROFIT_MIN - OVERHEAD_PROFIT_MAX."""
    try:
        v = float(val)
    except (ValueError, TypeError):
        raise ValueError("Overhead & Profit harus berupa angka.")
    if v < OVERHEAD_PROFIT_MIN or v > OVERHEAD_PROFIT_MAX:
        raise ValueError(
            f"Overhead & Profit harus antara {OVERHEAD_PROFIT_MIN}% - {OVERHEAD_PROFIT_MAX}%. "
            f"Contoh SE 47/SE/Dk/2026 menggunakan 10% × D."
        )
    return v


def validate_kode_hsp(kode: str) -> bool:
    """Cek format kode HSP: minimal 3 karakter dengan titik (mis. L.01)."""
    if not kode or len(kode) < 3:
        return False
    return "." in kode


def pembulatan_aman(nilai, desimal=2):
    """Pembulatan dengan penanganan None."""
    try:
        return round(float(nilai), desimal)
    except (ValueError, TypeError):
        return 0.0