"""
Formatter output AHSP sesuai contoh Lampiran V SE 47/SE/Dk/2026.
Blok:
  I. ASUMSI
  II. URUTAN KERJA
  III. PEMAKAIAN BAHAN, ALAT DAN TENAGA
  IV. HARGA DASAR SATUAN UPAH, BAHAN DAN ALAT
  V. ANALISA HARGA SATUAN PEKERJAAN
  VI. WAKTU PELAKSANAAN YANG DIPERLUKAN
  VII. VOLUME PEKERJAAN YANG DIPERLUKAN
"""

BLOK_ROMawi = ["I", "II", "III", "IV", "V", "VI", "VII"]


def format_blok_ahsp(data: dict) -> dict:
    """
    data = {
        'kode': '3.1.(1a)',
        'nama': 'Galian Biasa',
        'satuan': 'M3',
        'bidang': 'Bina Marga',
        'asumsi': [...],
        'urutan_kerja': [...],
        'pemakaian': {
            'bahan': [{'kode': 'M.05.b', 'uraian': 'Pasir', 'satuan': 'M3', 'koef': 0.5, 'harga': 220000}],
            'alat':  [...],
            'tenaga': [...]
        },
        'd': 100000, 'e': 10000, 'f': 110000
    }
    """
    return {
        "header": {
            "kode": data["kode"],
            "nama": data["nama"],
            "satuan": data["satuan"],
            "bidang": data["bidang"],
        },
        "I": data.get("asumsi", []),
        "II": data.get("urutan_kerja", []),
        "III": data.get("pemakaian", {"bahan": [], "alat": [], "tenaga": []}),
        "IV": "Lihat lampiran.",
        "V": {
            "D": data.get("d", 0),
            "E_pct": 10.0,
            "E": data.get("e", 0),
            "F": data.get("f", 0),
        },
        "VI": data.get("waktu", ""),
        "VII": data.get("volume", 1.0),
    }