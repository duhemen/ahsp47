from database.db_manager import DBManager

class UsulanModel:
    def __init__(self):
        self.db = DBManager()

    def create_usulan(self, nomor_surat, pengusul, jenis_usulan, nama_pekerjaan, justifikasi, sptjm_status, tanggal):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO usulan_ahsp (nomor_surat, pengusul, jenis_usulan, nama_pekerjaan, alasan_justifikasi, sptjm_status, tanggal_usulan)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (nomor_surat, pengusul, jenis_usulan, nama_pekerjaan, justifikasi, sptjm_status, tanggal))
        conn.commit()
        conn.close()

    def get_all_usulan(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usulan_ahsp ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        return rows