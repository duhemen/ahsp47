from database.db_manager import DBManager


class AcuanModel:
    def __init__(self):
        self.db = DBManager()

    def get_all_acuan(self):
        """
        Mengambil semua data acuan/konversi dari tabel acuan_konversi.
        
        Returns:
            list: List of dictionaries berisi semua data acuan, atau list kosong jika error/tidak ada data.
        """
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM acuan_konversi ORDER BY jenis_tanah_bahan, kondisi_semula")
            rows = cursor.fetchall()
            # Convert sqlite3.Row objects to dictionaries
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"[ERROR] get_all_acuan: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_acuan_by_id(self, acuan_id):
        """
        Mengambil data acuan spesifik berdasarkan ID.
        
        Args:
            acuan_id (int): ID acuan yang dicari.
            
        Returns:
            dict: Dictionary berisi data acuan, atau None jika tidak ditemukan/error.
        """
        if not isinstance(acuan_id, int) or acuan_id <= 0:
            print(f"[WARNING] get_acuan_by_id: ID tidak valid: {acuan_id}")
            return None
            
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM acuan_konversi WHERE id = ?", (acuan_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            print(f"[ERROR] get_acuan_by_id: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def get_acuan_by_material(self, nama_material):
        """
        Mengambil data acuan untuk material/jenis tanah tertentu.
        
        Args:
            nama_material (str): Nama material (jenis_tanah_bahan) yang dicari.
            
        Returns:
            list: List of dictionaries berisi data acuan untuk material tersebut,
                  atau list kosong jika tidak ditemukan/error.
        """
        if not nama_material or not isinstance(nama_material, str):
            print(f"[WARNING] get_acuan_by_material: Nama material tidak valid: {nama_material}")
            return []
            
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM acuan_konversi WHERE jenis_tanah_bahan = ? ORDER BY kondisi_semula",
                (nama_material.strip(),)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"[ERROR] get_acuan_by_material: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_fk_by_material_and_kondisi(self, nama_material, kondisi_semula, fk_type):
        """
        Mengambil nilai faktor konversi (Fk) spesifik untuk perhitungan AHSP teknis.
        
        Args:
            nama_material (str): Nama material (jenis_tanah_bahan).
            kondisi_semula (str): Kondisi semula material (misal: 'Asli (A)', 'Lepas (B)').
            fk_type (str): Tipe Fk yang diambil - 'fk_asli', 'fk_lepas', atau 'fk_padat'.
            
        Returns:
            float: Nilai Fk sebagai float, atau None jika tidak ditemukan/error.
        """
        valid_fk_types = ['fk_asli', 'fk_lepas', 'fk_padat']
        if fk_type not in valid_fk_types:
            print(f"[WARNING] get_fk_by_material_and_kondisi: tipe Fk tidak valid: {fk_type}. Harus salah satu dari {valid_fk_types}")
            return None
            
        if not nama_material or not isinstance(nama_material, str):
            print(f"[WARNING] get_fk_by_material_and_kondisi: Nama material tidak valid")
            return None
            
        if not kondisi_semula or not isinstance(kondisi_semula, str):
            print(f"[WARNING] get_fk_by_material_and_kondisi: Kondisi semula tidak valid")
            return None
            
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            # Gunakan parameterized query untuk keamanan - kolom fk_type tidak bisa diparameterisasi,
            # jadi kita validasi manual di atas
            query = f"SELECT {fk_type} FROM acuan_konversi WHERE jenis_tanah_bahan = ? AND kondisi_semula = ?"
            cursor.execute(query, (nama_material.strip(), kondisi_semula.strip()))
            row = cursor.fetchone()
            return float(row[fk_type]) if row else None
        except Exception as e:
            print(f"[ERROR] get_fk_by_material_and_kondisi: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def get_fk_asli(self, nama_material, kondisi_semula):
        """
        Shortcut method untuk mendapatkan Fk Asli (keadaan asli/undisturbed).
        
        Returns:
            float: Nilai Fk Asli, atau None jika tidak ditemukan.
        """
        return self.get_fk_by_material_and_kondisi(nama_material, kondisi_semula, 'fk_asli')

    def get_fk_lepas(self, nama_material, kondisi_semula):
        """
        Shortcut method untuk mendapatkan Fk Lepas (setelah digali/longsor).
        
        Returns:
            float: Nilai Fk Lepas, atau None jika tidak ditemukan.
        """
        return self.get_fk_by_material_and_kondisi(nama_material, kondisi_semula, 'fk_lepas')

    def get_fk_padat(self, nama_material, kondisi_semula):
        """
        Shortcut method untuk mendapatkan Fk Padat (setelah dikompaksi).
        
        Returns:
            float: Nilai Fk Padat, atau None jika tidak ditemukan.
        """
        return self.get_fk_by_material_and_kondisi(nama_material, kondisi_semula, 'fk_padat')

    def get_all_materials(self):
        """
        Mengambil daftar unik semua jenis material/tanah yang tersedia.
        
        Returns:
            list: List of strings berisi nama material unik, atau list kosong jika error.
        """
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT jenis_tanah_bahan FROM acuan_konversi ORDER BY jenis_tanah_bahan")
            rows = cursor.fetchall()
            return [row['jenis_tanah_bahan'] for row in rows]
        except Exception as e:
            print(f"[ERROR] get_all_materials: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_kondisi_by_material(self, nama_material):
        """
        Mengambil daftar kondisi semula yang tersedia untuk material tertentu.
        
        Args:
            nama_material (str): Nama material.
            
        Returns:
            list: List of strings berisi kondisi semula yang tersedia, atau list kosong jika error.
        """
        if not nama_material or not isinstance(nama_material, str):
            return []
            
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT DISTINCT kondisi_semula FROM acuan_konversi WHERE jenis_tanah_bahan = ? ORDER BY kondisi_semula",
                (nama_material.strip(),)
            )
            rows = cursor.fetchall()
            return [row['kondisi_semula'] for row in rows]
        except Exception as e:
            print(f"[ERROR] get_kondisi_by_material: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def add_acuan(self, data):
        """Menambah data acuan baru ke database"""
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            query = """INSERT INTO acuan_konversi (jenis_tanah_bahan, kondisi_semula, fk_asli, fk_lepas, fk_padat) 
                       VALUES (?, ?, ?, ?, ?)"""
            cursor.execute(query, (data['jenis_tanah_bahan'], data['kondisi_semula'], data['fk_asli'], data['fk_lepas'], data['fk_padat']))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"[ERROR] add_acuan: {e}")
            if conn: conn.rollback()
            return None
        finally:
            if conn: conn.close()

    def update_acuan(self, acuan_id, data):
        """Memperbarui data acuan berdasarkan ID"""
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            query = """UPDATE acuan_konversi SET jenis_tanah_bahan=?, kondisi_semula=?, fk_asli=?, fk_lepas=?, fk_padat=? 
                       WHERE id=?"""
            cursor.execute(query, (data['jenis_tanah_bahan'], data['kondisi_semula'], data['fk_asli'], data['fk_lepas'], data['fk_padat'], acuan_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"[ERROR] update_acuan: {e}")
            if conn: conn.rollback()
            return False
        finally:
            if conn: conn.close()

    def delete_acuan(self, acuan_id):
        """Menghapus data acuan berdasarkan ID"""
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM acuan_konversi WHERE id = ?", (acuan_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"[ERROR] delete_acuan: {e}")
            if conn: conn.rollback()
            return False
        finally:
            if conn: conn.close()


    def get_all_konversi(self):
        """Alias untuk get_all_acuan agar sinkron dengan views/tab_acuan.py"""
        return self.get_all_acuan()
