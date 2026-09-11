# models/produktivitas_alat.py
"""
Rumus Produktivitas Alat & Faktor Koreksi — Lampiran II SE 47/SE/Dk/2026.

Referensi:
  • Komatsu, Specification & Application Handbook, Edition 28, Des 2007
  • SNI / Spesifikasi Umum Bina Marga
  • SE 47/SE/Dk/2026 Lampiran II bagian B

Semua fungsi static agar bisa dipanggil tanpa instansiasi.
"""


class ProduktivitasAlat:
    """Kumpulan rumus produktivitas alat sesuai Lampiran II."""

    # ==========================================================
    # A. WAKTU SIKLUS & FAKTOR DASAR
    # ==========================================================
    @staticmethod
    def waktu_siklus(*komponen):
        """
        Ts = T1 + T2 + T3 + ... (Lampiran II, rumus 15).
        Satuan: menit.
        """
        return sum(float(x) for x in komponen)

    @staticmethod
    def kecepatan_km_per_jam_ke_m_per_menit(v_km_per_jam):
        """Konversi km/jam → m/menit."""
        return float(v_km_per_jam) * 1000.0 / 60.0

    # ==========================================================
    # B. FAKTOR PEMAMPATAN (Bulking Factor) — Lampiran II B.2
    # ==========================================================
    # Contoh nilai (Tabel A.1):
    #   Pasir         : Asli 1.000, Lepas 1.110, Padat 0.950
    #   Tanah Liat    : Asli 1.000, Lepas 1.430, Padat 0.900
    # Nilai lengkap ada di tabel acuan_konversi.
    @staticmethod
    def fk_lepas_ke_padat(nilai_lepas: float, nilai_padat: float) -> float:
        """Fk = nilai_padat / nilai_lepas."""
        if nilai_lepas == 0:
            return 0.0
        return nilai_padat / nilai_lepas

    # ==========================================================
    # C. KOEFISIEN ALAT (Ka = 1/Q) — Lampiran II B.3.2.1
    # ==========================================================
    @staticmethod
    def koefisien_alat(q_per_jam: float) -> float:
        """Ka = 1 / Q  [jam per satuan]."""
        if q_per_jam is None or q_per_jam <= 0:
            return 0.0
        return 1.0 / q_per_jam

    # ==========================================================
    # D. FAKTOR EFISIENSI ALAT (Tabel A.5)
    # ==========================================================
    FAKTOR_EFISIENSI = {
        # (kondisi_operasi, kondisi_pemeliharaan): nilai
        ("Baik Sekali", "Baik Sekali"): 0.83,
        ("Baik Sekali", "Baik"): 0.78,
        ("Baik Sekali", "Sedang"): 0.72,
        ("Baik Sekali", "Buruk"): 0.63,
        ("Baik Sekali", "Buruk Sekali"): 0.53,
        ("Baik", "Baik Sekali"): 0.81,
        ("Baik", "Baik"): 0.75,
        ("Baik", "Sedang"): 0.69,
        ("Baik", "Buruk"): 0.61,
        ("Baik", "Buruk Sekali"): 0.50,
        ("Sedang", "Baik Sekali"): 0.76,
        ("Sedang", "Baik"): 0.71,
        ("Sedang", "Sedang"): 0.65,
        ("Sedang", "Buruk"): 0.57,
        ("Sedang", "Buruk Sekali"): 0.47,
        ("Buruk", "Baik Sekali"): 0.70,
        ("Buruk", "Baik"): 0.65,
        ("Buruk", "Sedang"): 0.60,
        ("Buruk", "Buruk"): 0.52,
        ("Buruk", "Buruk Sekali"): 0.42,
        ("Buruk Sekali", "Baik Sekali"): 0.63,
        ("Buruk Sekali", "Baik"): 0.60,
        ("Buruk Sekali", "Sedang"): 0.54,
        ("Buruk Sekali", "Buruk"): 0.45,
        ("Buruk Sekali", "Buruk Sekali"): 0.32,
    }

    @classmethod
    def faktor_efisiensi(cls, kondisi_operasi="Baik Sekali", kondisi_pemeliharaan="Baik Sekali") -> float:
        """Ambil Fa dari Tabel A.5."""
        return cls.FAKTOR_EFISIENSI.get((kondisi_operasi, kondisi_pemeliharaan), 0.83)

    # ==========================================================
    # E. ASPHALT MIXING PLANT (AMP) — Lampiran II B.3.2.2 no. 1
    # ==========================================================
    @staticmethod
    def amp(v_ton_per_jam: float, fa: float = 0.83) -> float:
        """Q = v × Fa  [ton/jam]."""
        return float(v_ton_per_jam) * fa

    # ==========================================================
    # F. ASPHALT FINISHER — no. 2
    # ==========================================================
    @staticmethod
    def asphalt_finisher(v_m_per_menit, b_lebar, t_tebal, d_berat_isi, fa=0.83, satuan="ton"):
        """
        Q_ton = v × b × 60 × Fa × t × D1
        Q_m3  = v × b × 60 × Fa × t
        Q_m2  = v × b × 60 × Fa
        """
        v = float(v_m_per_menit)
        b = float(b_lebar)
        t = float(t_tebal)
        d = float(d_berat_isi)
        if satuan == "ton":
            return v * b * 60.0 * fa * t * d
        if satuan == "m3":
            return v * b * 60.0 * fa * t
        if satuan == "m2":
            return v * b * 60.0 * fa
        return 0.0

    # ==========================================================
    # G. ASPHALT SPRAYER — no. 3
    # ==========================================================
    @staticmethod
    def asphalt_sprayer(pa_liter_per_menit, fa=0.83, lt_liter_per_m2=None):
        """
        Q1 (liter/jam) = pa × 60 × Fa
        Q2 (m2/jam)   = (pa × 60 × Fa) / lt
        """
        q1 = float(pa_liter_per_menit) * 60.0 * fa
        if lt_liter_per_m2 and lt_liter_per_m2 > 0:
            q2 = q1 / float(lt_liter_per_m2)
            return q1, q2
        return q1, 0.0

    # ==========================================================
    # H. BULLDOZER — no. 4
    # ==========================================================
    @staticmethod
    def bulldozer_menggusur(q_m3, fb=0.90, fm=1.00, fa_bulk=0.83, ts_menit=1.15):
        """
        Q = q × Fb × Fm × Fa_bulk × 60 / Ts  [m3/jam]
        q = L × H² (kapasitas pisau).
        """
        if ts_menit <= 0:
            return 0.0
        return float(q_m3) * fb * fm * fa_bulk * 60.0 / float(ts_menit)

    @staticmethod
    def bulldozer_meratakan(lh_m, n_lajur, b_lebar, bo_overlap, fb, fm, fa_bulk, n_lintasan, ts_menit):
        """
        Q = Lh × {N(b-bo) + bo} × Fb × Fm × Fa × 60 / (N × n × Ts)  [m2/jam]
        """
        be = float(b_lebar) - float(bo_overlap)
        num = float(lh_m) * (n_lajur * be + float(bo_overlap)) * fb * fm * fa_bulk * 60.0
        den = n_lajur * n_lintasan * ts_menit if ts_menit > 0 else 1
        return num / den

    # ==========================================================
    # I. AIR COMPRESSOR + JACK HAMMER — no. 5
    # ==========================================================
    @staticmethod
    def jack_hammer(fa=0.83, menit_per_m2=5.0, bantu_alat_lain=False):
        """
        Q = (60 / 5) × 1.00 × Fa = 12 × Fa   [m2/jam]
        """
        if bantu_alat_lain:
            menit_per_m2 = 3.0
        return 60.0 / float(menit_per_m2) * 1.00 * fa

    @staticmethod
    def air_compressor_bersih_area(v_m2_per_menit, fa=0.83):
        """Q = v × Fa × 60  [m2/jam]."""
        return float(v_m2_per_menit) * fa * 60.0

    # ==========================================================
    # J. CONCRETE MIXER — no. 6
    # ==========================================================
    @staticmethod
    def concrete_mixer(v_liter, fa=0.83, ts_menit=2.0):
        """Q = v × Fa × 60 / (1000 × Ts)  [m3/jam]."""
        if ts_menit <= 0:
            return 0.0
        return float(v_liter) * fa * 60.0 / (1000.0 * float(ts_menit))

    # ==========================================================
    # K. CRANE — no. 7
    # ==========================================================
    @staticmethod
    def crane(v_buah, fa=0.83, ts_menit=3.0):
        """Q = v × Fa × 60 / Ts  [buah/jam]."""
        if ts_menit <= 0:
            return 0.0
        return float(v_buah) * fa * 60.0 / float(ts_menit)

    # ==========================================================
    # L. DUMP TRUCK — no. 8 / 9
    # ==========================================================
    @staticmethod
    def dump_truck(v_ton, fa, d_berat_isi_ton_per_m3, ts_menit):
        """
        Q = V × Fa × 60 / (D × Ts)  [m3/jam]
        Satuan V: ton.
        """
        if ts_menit <= 0 or d_berat_isi_ton_per_m3 <= 0:
            return 0.0
        return float(v_ton) * fa * 60.0 / (float(d_berat_isi_ton_per_m3) * float(ts_menit))

    @staticmethod
    def waktu_siklus_dump_truck(l_km, v_f_km_per_jam, v_r_km_per_jam, t1_menit, t4_menit=1.5):
        """
        Ts = T1 + T2 + T3 + T4
        T2 = (L / vF) × 60
        T3 = (L / vR) × 60
        """
        t2 = (float(l_km) / v_f_km_per_jam) * 60.0 if v_f_km_per_jam > 0 else 0.0
        t3 = (float(l_km) / v_r_km_per_jam) * 60.0 if v_r_km_per_jam > 0 else 0.0
        return float(t1_menit) + t2 + t3 + float(t4_menit), t2, t3

    # ==========================================================
    # M. EXCAVATOR BACKHOE — no. 10
    # ==========================================================
    @staticmethod
    def excavator_backhoe(v_m3, fa, fb, fv, ts_menit):
        """
        Q = V × Fa × Fb × 60 / (Ts × Fv)  [m3/jam]
        """
        if ts_menit <= 0 or fv <= 0:
            return 0.0
        return float(v_m3) * fa * fb * 60.0 / (float(ts_menit) * fv)

    # ==========================================================
    # N. FLAT BED TRUCK — no. 11
    # ==========================================================
    @staticmethod
    def flat_bed_truck(v_ton, fa, ts_menit):
        """Q = v × Fa × 60 / Ts  [ton/jam]."""
        if ts_menit <= 0:
            return 0.0
        return float(v_ton) * fa * 60.0 / float(ts_menit)

    # ==========================================================
    # O. GENERATING SET — no. 12
    # ==========================================================
    @staticmethod
    def genset(v_kw, fa=0.83):
        """Q = V × Fa  [kW/jam]."""
        return float(v_kw) * fa

    # ==========================================================
    # P. MOTOR GRADER — no. 13
    # ==========================================================
    @staticmethod
    def motor_grader(lh_m, n_lajur, b_lebar, bo_overlap, n_lintasan, fa, ts_menit, t_tebal=None):
        """
        Q (m2/jam) = Lh × {N(b-bo)+bo} × Fa × 60 / (N × n × Ts)
        Q (m3/jam) = Q_m2 × t
        """
        be = float(b_lebar) - float(bo_overlap)
        num = float(lh_m) * (n_lajur * be + float(bo_overlap)) * fa * 60.0
        den = n_lajur * n_lintasan * float(ts_menit) if ts_menit > 0 else 1
        q_m2 = num / den
        if t_tebal:
            return q_m2 * float(t_tebal)
        return q_m2

    @staticmethod
    def waktu_siklus_motor_grader(lh_m, v_km_per_jam, t2_menit=1.0):
        """T1 = Lh × 60 / (v × 1000) menit."""
        t1 = float(lh_m) * 60.0 / (float(v_km_per_jam) * 1000.0) if v_km_per_jam > 0 else 0.0
        return t1 + float(t2_menit), t1

    # ==========================================================
    # Q. TRACK LOADER & WHEEL LOADER — no. 14, 15
    # ==========================================================
    @staticmethod
    def wheel_loader(v_m3, fb, fa, ts_menit):
        """Q = V × Fb × Fa × 60 / Ts  [m3/jam]."""
        if ts_menit <= 0:
            return 0.0
        return float(v_m3) * fb * fa * 60.0 / float(ts_menit)

    # ==========================================================
    # R. THREE WHEEL ROLLER (TWR) — no. 16
    # ==========================================================
    @staticmethod
    def three_wheel_roller(b_lebar, bo_overlap, v_km_per_jam, t_tebal, n_lintasan, fa=0.83, n_lajur=1):
        """
        Q = {N(b-bo) + bo} × v × 1000 × Fa × t / (n × N)  [m3/jam]
        """
        be = float(b_lebar) - float(bo_overlap)
        return (n_lajur * be + float(bo_overlap)) * float(v_km_per_jam) * 1000.0 * fa * float(t_tebal) \
               / (n_lintasan * n_lajur)

    # ==========================================================
    # S. TANDEM / PNEUMATIC / VIBRATORY ROLLER — no. 17, 18, 19
    # ==========================================================
    @staticmethod
    def tandem_roller(b_lebar, bo_overlap, v_km_per_jam, t_tebal, n_lintasan, n_lajur, fa=0.83):
        """
        Q = {N(b-bo)+bo} × v × 1000 × Fa × t / (n × N)
        """
        be = float(b_lebar) - float(bo_overlap)
        num = (n_lajur * be + float(bo_overlap)) * float(v_km_per_jam) * 1000.0 * fa * float(t_tebal)
        den = n_lintasan * n_lajur
        return num / den if den > 0 else 0.0

    pneumatic_tire_roller = tandem_roller
    vibratory_roller = tandem_roller

    # ==========================================================
    # T. CONCRETE VIBRATOR — no. 20
    # ==========================================================
    @staticmethod
    def concrete_vibrator(v_m3_per_jam, fa=0.83):
        """Q = v × Fa."""
        return float(v_m3_per_jam) * fa

    # ==========================================================
    # U. STONE CRUSHER — no. 21
    # ==========================================================
    @staticmethod
    def stone_crusher_jaw(kapasitas_ton_per_jam, undersize_pct, setting_mm, jenis_batu="River Gravel"):
        """
        Estimasi produksi agregat dari Jaw Crusher.
        Return: dict agregat berdasarkan rentang ukuran.
        """
        return {
            "kapasitas_ton_per_jam": float(kapasitas_ton_per_jam),
            "setting_mm": float(setting_mm),
            "jenis_batu": jenis_batu,
            "undersize_pct": float(undersize_pct),
        }

    @staticmethod
    def stone_crusher_wheel_loader(fa1, cp1, d_berat_isi):
        """Qb = (Fa1 × Cp1) / D  [m3/jam]."""
        if d_berat_isi <= 0:
            return 0.0
        return float(fa1) * float(cp1) / float(d_berat_isi)

    # ==========================================================
    # V. WATER PUMP — no. 22
    # ==========================================================
    @staticmethod
    def water_pump(v_m3=None):
        """Q = v (kapasitas produksi maksimum pompa) [m3/jam]."""
        return float(v_m3) if v_m3 else 4.5

    # ==========================================================
    # W. WATER TANK TRUCK — no. 23
    # ==========================================================
    @staticmethod
    def water_tank_truck(pa_liter_per_menit, wc_m3_per_m3, fa=0.83):
        """
        Q = pa × Fa × 60 / (1000 × Wc)  [m3/jam]
        """
        if wc_m3_per_m3 <= 0:
            return 0.0
        return float(pa_liter_per_menit) * fa * 60.0 / (1000.0 * float(wc_m3_per_m3))

    # ==========================================================
    # X. PEDESTRIAN ROLLER — no. 24
    # ==========================================================
    @staticmethod
    def pedestrian_roller(b_lebar, bo_overlap, v_km_per_jam, t_tebal, n_lintasan, fa=0.83):
        """Q = (b-bo) × v × 1000 × Fa × t / (60 × n)."""
        be = float(b_lebar) - float(bo_overlap)
        den = 60.0 * n_lintasan if n_lintasan > 0 else 1
        return be * float(v_km_per_jam) * 1000.0 * fa * float(t_tebal) / den

    # ==========================================================
    # Y. TAMPER — no. 25
    # ==========================================================
    @staticmethod
    def tamper(v_km_per_jam, lebar_telapak_m, t_tebal, n_lapis, n_tumbukan, fa=0.83):
        """Q = v × 1000 × Fa × lbr × t / (N × n)  [m3/jam]."""
        den = n_lapis * n_tumbukan if (n_lapis * n_tumbukan) > 0 else 1
        return float(v_km_per_jam) * 1000.0 * fa * float(lebar_telapak_m) * float(t_tebal) / den

    # ==========================================================
    # Z. JACK HAMMER (yang tidak perlu compressor) — no. 26
    # ==========================================================
    @staticmethod
    def jack_breaker(v_m3_per_jam, fa=0.83):
        """Q = V × Fa  [m3/jam]."""
        return float(v_m3_per_jam) * fa

    # ==========================================================
    # AA. PULVI MIXER (Soil Stabilizer) — no. 27
    # ==========================================================
    @staticmethod
    def pulvi_mixer(v_m_per_menit, b_lebar, t_tebal, fa=0.83):
        """Q = v × 1000 × b × t × Fa  [m3/jam]."""
        return float(v_m_per_menit) * 1000.0 * float(b_lebar) * float(t_tebal) * fa

    # ==========================================================
    # AB. CONCRETE PUMP — no. 28
    # ==========================================================
    @staticmethod
    def concrete_pump(cap_m3_per_jam, fa=0.83):
        """Q = kapasitas × Fa."""
        return float(cap_m3_per_jam) * fa

    # ==========================================================
    # AC. PILE DRIVER / HAMMER — no. 30
    # ==========================================================
    @staticmethod
    def pile_driver(v_titik, p_panjang_m, fa, ts_menit):
        """Q = V × p × Fa × 60 / Ts  [m/jam atau titik/jam]."""
        if ts_menit <= 0:
            return 0.0
        return float(v_titik) * float(p_panjang_m) * fa * 60.0 / float(ts_menit)

    # ==========================================================
    # AD. BORE PILE — no. 33 / 50
    # ==========================================================
    @staticmethod
    def bore_pile(v_titik, p_kedalaman_m, fa, ts_menit):
        """Q = V × p × Fa × 60 / Ts  [m/jam]."""
        if ts_menit <= 0:
            return 0.0
        return float(v_titik) * float(p_kedalaman_m) * fa * 60.0 / float(ts_menit)

    # ==========================================================
    # AE. ASPHALT DISTRIBUTOR — no. 41
    # ==========================================================
    @staticmethod
    def asphalt_distributor(pa_liter_per_menit, fa=0.83, efektivitas=0.75):
        """
        Q = pa × efektivitas × Fa × 60  [liter/jam]
        """
        return float(pa_liter_per_menit) * efektivitas * fa * 60.0

    # ==========================================================
    # AF. CONCRETE PAVING MACHINE (Slipform Paver) — no. 42
    # ==========================================================
    @staticmethod
    def concrete_paver(b_lebar, t_tebal, v_m_per_menit, fa=0.83):
        """Q = b × t × Fa × v × 60  [m3/jam]."""
        return float(b_lebar) * float(t_tebal) * fa * float(v_m_per_menit) * 60.0

    # ==========================================================
    # AG. BATCHING PLANT / PAN MIXER — no. 43
    # ==========================================================
    @staticmethod
    def batching_plant(v_liter, fa=0.83, ts_menit=3.0):
        """Q = V × Fa × 60 / (1000 × Ts)  [m3/jam]."""
        if ts_menit <= 0:
            return 0.0
        return float(v_liter) * fa * 60.0 / (1000.0 * float(ts_menit))

    # ==========================================================
    # AH. CONCRETE BREAKER / DROP HAMMER — no. 56
    # ==========================================================
    @staticmethod
    def concrete_breaker(v_m_per_menit, b_lebar, t_tebal, fa=0.83):
        """Q = v × b × t × Fa × 60  [m3/jam]."""
        return float(v_m_per_menit) * float(b_lebar) * float(t_tebal) * fa * 60.0

    # ==========================================================
    # AI. COLD MILLING MACHINE — no. 36
    # ==========================================================
    @staticmethod
    def cold_milling(v_m_per_menit, b_lebar, t_tebal, fa=0.70):
        """Q = v × b × Fa × 60 × t  [m3/jam]."""
        return float(v_m_per_menit) * float(b_lebar) * fa * 60.0 * float(t_tebal)

    # ==========================================================
    # AJ. COLD RECYCLER — no. 38
    # ==========================================================
    cold_recycler = cold_milling

    # ==========================================================
    # AK. HOT RECYCLER — no. 39
    # ==========================================================
    hot_recycler = cold_milling

    # ==========================================================
    # AL. AGGREGATE SPREADER — no. 40
    # ==========================================================
    @staticmethod
    def aggregate_spreader(v_km_per_jam, b_lebar, t_tebal, fa=0.83):
        """Q = v × b × Fa × 1000 × t  [m3/jam]."""
        return float(v_km_per_jam) * float(b_lebar) * fa * 1000.0 * float(t_tebal)