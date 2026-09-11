from config.settings import OVERHEAD_PROFIT_MIN, OVERHEAD_PROFIT_MAX


def validate_overhead_profit(val):
    v = float(val)
    if v < OVERHEAD_PROFIT_MIN or v > OVERHEAD_PROFIT_MAX:
        raise ValueError(
            f"Overhead & Profit harus antara {OVERHEAD_PROFIT_MIN}% - {OVERHEAD_PROFIT_MAX}%. "
            f"Contoh pada SE 47/SE/Dk/2026 menggunakan 10% × D."
        )
    return v


def validate_kode_ahsp(kode: str) -> bool:
    """Format kode: L.xx, M.xx, E.xx, atau A.xx dst."""
    if not kode or len(kode) < 3:
        return False
    return kode[1] == "." or kode[2:3] == "."


def validate_risiko(risiko: str) -> bool:
    from config.settings import RISIKO_KECIL, RISIKO_SEDANG, RISIKO_BESAR
    return risiko in (RISIKO_KECIL, RISIKO_SEDANG, RISIKO_BESAR)


def validate_ba_tanggal(tanggal_iso: str) -> bool:
    """BA Penetapan Harga maks 31 Oktober."""
    from datetime import date
    d = date.fromisoformat(tanggal_iso)
    return d.month <= 10 or (d.month == 10 and d.day <= 31)