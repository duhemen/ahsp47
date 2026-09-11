from config.settings import DEFAULT_OVERHEAD_PROFIT, DEFAULT_PPN
from models.hsp_model import HSPModel


class BMModel:
    def __init__(self):
        self.hsp_model = HSPModel()

    def get_hsp_prices(self, kode_upah_list, kode_bahan_list, kode_alat_list):
        """
        Mengambil harga satuan untuk daftar kode Upah, Bahan, dan Alat.
        
        Args:
            kode_upah_list (list): List kode HSP untuk kategori Tenaga Kerja
            kode_bahan_list (list): List kode HSP untuk kategori Bahan
            kode_alat_list (list): List kode HSP untuk kategori Peralatan
            
        Returns:
            dict: Dictionary berisi harga untuk setiap kategori
        """
        harga_upah = {}
        harga_bahan = {}
        harga_alat = {}
        
        for kode in kode_upah_list:
            harga = self.hsp_model.get_hsp_price(kode)
            if harga is not None:
                harga_upah[kode] = harga
                
        for kode in kode_bahan_list:
            harga = self.hsp_model.get_hsp_price(kode)
            if harga is not None:
                harga_bahan[kode] = harga
                
        for kode in kode_alat_list:
            harga = self.hsp_model.get_hsp_price(kode)
            if harga is not None:
                harga_alat[kode] = harga
                
        return {
            'upah': harga_upah,
            'bahan': harga_bahan,
            'alat': harga_alat
        }

    def calculate_component_total(self, harga_dict, koefisien_dict):
        """
        Menghitung total harga untuk satu komponen (Upah/Bahan/Alat).
        
        Args:
            harga_dict (dict): Dictionary {kode: harga_satuan}
            koefisien_dict (dict): Dictionary {kode: koefisien}
            
        Returns:
            float: Total harga komponen
        """
        total = 0.0
        for kode, harga in harga_dict.items():
            koef = koefisien_dict.get(kode, 0)
            total += harga * koef
        return total

    def calculate_jumlah_harga(self, upah_data, bahan_data, alat_data):
        """
        Menghitung Jumlah Harga (Total Upah + Total Bahan + Total Alat).
        
        Args:
            upah_data (dict): {kode: koefisien} untuk Tenaga Kerja
            bahan_data (dict): {kode: koefisien} untuk Bahan
            alat_data (dict): {kode: koefisien} untuk Peralatan
            
        Returns:
            tuple: (total_upah, total_bahan, total_alat, jumlah_harga)
        """
        # Ambil harga dari database
        kode_upah = list(upah_data.keys())
        kode_bahan = list(bahan_data.keys())
        kode_alat = list(alat_data.keys())
        
        prices = self.get_hsp_prices(kode_upah, kode_bahan, kode_alat)
        
        # Hitung total per komponen
        total_upah = self.calculate_component_total(prices['upah'], upah_data)
        total_bahan = self.calculate_component_total(prices['bahan'], bahan_data)
        total_alat = self.calculate_component_total(prices['alat'], alat_data)
        
        jumlah_harga = total_upah + total_bahan + total_alat
        
        return total_upah, total_bahan, total_alat, jumlah_harga

    def calculate_overhead(self, jumlah_harga, overhead_pct=None):
        """
        Menghitung nilai Overhead & Profit.
        
        Args:
            jumlah_harga (float): Total harga (Upah + Bahan + Alat)
            overhead_pct (float, optional): Persentase Overhead. Default dari settings.
            
        Returns:
            tuple: (overhead_val, hsp_before_ppn)
        """
        if overhead_pct is None:
            overhead_pct = DEFAULT_OVERHEAD_PROFIT
            
        overhead_val = jumlah_harga * (overhead_pct / 100.0)
        hsp_before_ppn = jumlah_harga + overhead_val
        
        return overhead_val, hsp_before_ppn

    def calculate_ppn(self, hsp_before_ppn, ppn_pct=None):
        """
        Menghitung nilai PPN.
        
        Args:
            hsp_before_ppn (float): Harga Satuan sebelum PPN
            ppn_pct (float, optional): Persentase PPN. Default dari settings.
            
        Returns:
            tuple: (ppn_val, hsp_final)
        """
        if ppn_pct is None:
            ppn_pct = DEFAULT_PPN
            
        ppn_val = hsp_before_ppn * (ppn_pct / 100.0)
        hsp_final = hsp_before_ppn + ppn_val
        
        return ppn_val, hsp_final

    def calculate_ahsp_bina_marga(self, upah_data, bahan_data, alat_data, overhead_pct=None, ppn_pct=None):
        """
        Kalkulasi lengkap AHSP Bina Marga sesuai SE 47/SE/Dk/2026.
        
        Rumus:
        1. Jumlah Harga = Total Upah + Total Bahan + Total Alat
        2. Overhead = Jumlah Harga * (Overhead% / 100)
        3. Harga Satuan (sebelum PPN) = Jumlah Harga + Overhead
        4. PPN = Harga Satuan * (PPN% / 100)
        5. Harga Satuan Final = Harga Satuan + PPN
        
        Args:
            upah_data (dict): {kode_hsp: koefisien} untuk Tenaga Kerja
            bahan_data (dict): {kode_hsp: koefisien} untuk Bahan
            alat_data (dict): {kode_hsp: koefisien} untuk Peralatan
            overhead_pct (float, optional): Persentase Overhead & Profit (default 10%)
            ppn_pct (float, optional): Persentase PPN (default 11%)
            
        Returns:
            dict: Hasil kalkulasi lengkap
        """
        # 1. Hitung Jumlah Harga
        total_upah, total_bahan, total_alat, jumlah_harga = self.calculate_jumlah_harga(
            upah_data, bahan_data, alat_data
        )
        
        # 2. Hitung Overhead
        overhead_val, hsp_before_ppn = self.calculate_overhead(jumlah_harga, overhead_pct)
        
        # 3. Hitung PPN
        ppn_val, hsp_final = self.calculate_ppn(hsp_before_ppn, ppn_pct)
        
        return {
            'total_upah': round(total_upah, 2),
            'total_bahan': round(total_bahan, 2),
            'total_alat': round(total_alat, 2),
            'jumlah_harga': round(jumlah_harga, 2),
            'overhead_pct': overhead_pct if overhead_pct is not None else DEFAULT_OVERHEAD_PROFIT,
            'overhead_val': round(overhead_val, 2),
            'hsp_before_ppn': round(hsp_before_ppn, 2),
            'ppn_pct': ppn_pct if ppn_pct is not None else DEFAULT_PPN,
            'ppn_val': round(ppn_val, 2),
            'hsp_final': round(hsp_final, 2)
        }

    @staticmethod
    def calculate_hsp(jumlah_d, overhead_pct):
        """
        Legacy method untuk kompatibilitas mundur.
        Menghitung Overhead dan HSP (Harga Satuan Pekerjaan) sederhana.
        """
        overhead_val = jumlah_d * (overhead_pct / 100.0)
        hsp_f = jumlah_d + overhead_val
        return overhead_val, hsp_f