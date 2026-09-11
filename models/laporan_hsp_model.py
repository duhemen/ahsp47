from database.db_manager import DBManager

class LaporanHSPModel:
    def __init__(self):
        self.db = DBManager()

    def create_laporan(self, nomor_ba, nama_balai, tahun, petugas_lapangan, pengawas, pengolah_data, tanggal_penetapan, status_rekonsiliasi):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO laporan_pengumpulan_hsp 
            (nomor_ba, nama_balai, tahun, petugas_lapangan, pengawas, pengolah_data, tanggal_penetapan, status_rekonsiliasi)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (nomor_ba, nama_balai, tahun, petugas_lapangan, pengawas, pengolah_data, tanggal_penetapan, status_rekonsiliasi))
        conn.commit()
        conn.close()

    def get_all_laporan(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM laporan_pengumpulan_hsp ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        return rows