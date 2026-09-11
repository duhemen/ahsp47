class SDAModel:
    @staticmethod
    def calculate_hsp(jumlah_d, overhead_pct):
        overhead_val = jumlah_d * (overhead_pct / 100.0)
        hsp_f = jumlah_d + overhead_val
        return overhead_val, hsp_f