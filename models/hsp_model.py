from database.db_manager import DBManager
from datetime import datetime


class HSPModel:
    def __init__(self):
        self.db = DBManager()

    def get_all_hsp(self):
        """Mengambil semua data dari tabel hsp_data, diurutkan berdasarkan kolom kode secara ascending."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM hsp_data ORDER BY kode ASC")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_hsp_by_kode(self, kode):
        """Mengambil 1 data HSP berdasarkan kode (misal: 'L.01')."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM hsp_data WHERE kode = ?", (kode,))
        row = cursor.fetchone()
        conn.close()
        return row

    def get_hsp_by_kategori(self, kategori):
        """Memfilter data berdasarkan kategori ('Tenaga Kerja', 'Bahan', 'Peralatan')."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM hsp_data WHERE kategori = ? ORDER BY kode ASC", (kategori,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def add_hsp(self, data):
        """
        Melakukan INSERT data HSP baru.
        
        Args:
            data (dict): Dictionary berisi keys: kode, uraian, kategori, satuan, 
                         harga_satuan, sumber_vendor, tanggal_survei
        
        Returns:
            int: ID (primary key) dari row yang baru di-insert, atau None jika gagal.
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO hsp_data (kode, uraian, kategori, satuan, harga_satuan, sumber_vendor, tanggal_survei)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                data['kode'],
                data['uraian'],
                data['kategori'],
                data['satuan'],
                data['harga_satuan'],
                data.get('sumber_vendor'),
                data.get('tanggal_survei')
            ))
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
            return new_id
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e

    def update_hsp(self, kode, data):
        """
        Melakukan UPDATE data HSP berdasarkan kode dan memperbarui kolom updated_at.
        
        Args:
            kode (str): Kode HSP yang akan di-update (misal: 'L.01')
            data (dict): Dictionary berisi fields yang akan di-update: uraian, kategori, satuan, 
                         harga_satuan, sumber_vendor, tanggal_survei
        
        Returns:
            bool: True jika berhasil, False jika kode tidak ditemukan.
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            # Bangun query dynamic berdasarkan fields yang disediakan
            allowed_fields = ['uraian', 'kategori', 'satuan', 'harga_satuan', 'sumber_vendor', 'tanggal_survei']
            set_clauses = []
            values = []
            
            for field in allowed_fields:
                if field in data:
                    set_clauses.append(f"{field} = ?")
                    values.append(data[field])
            
            if not set_clauses:
                conn.close()
                return False
            
            # Tambahkan updated_at
            set_clauses.append("updated_at = ?")
            values.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
            # Tambahkan kode untuk WHERE clause
            values.append(kode)
            
            query = f"UPDATE hsp_data SET {', '.join(set_clauses)} WHERE kode = ?"
            cursor.execute(query, values)
            conn.commit()
            updated = cursor.rowcount > 0
            conn.close()
            return updated
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e

    def delete_hsp(self, kode):
        """
        Menghapus data HSP berdasarkan kode.
        
        Args:
            kode (str): Kode HSP yang akan dihapus (misal: 'L.01')
        
        Returns:
            bool: True jika berhasil dihapus, False jika kode tidak ditemukan.
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM hsp_data WHERE kode = ?", (kode,))
            conn.commit()
            deleted = cursor.rowcount > 0
            conn.close()
            return deleted
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e

    def get_hsp_price(self, kode):
        """
        Mengambil hanya nilai harga_satuan (float) untuk kebutuhan kalkulasi RAB.
        
        Args:
            kode (str): Kode HSP (misal: 'L.01')
        
        Returns:
            float: Nilai harga_satuan, atau None jika kode tidak ditemukan.
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT harga_satuan FROM hsp_data WHERE kode = ?", (kode,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return float(row['harga_satuan'])
        return None