# models/rab_model.py
"""
Model RAB / HPS — SE 47/SE/Dk/2026.

Menyediakan CRUD:
  • Proyek       : create / read / update / delete
  • Item RAB     : create / read / update / delete
  • Integrasi AHSP: hitung D & F dari analisis_ahsp_template
"""

from database.db_manager import DBManager


class RABModel:
    def __init__(self):
        self.db = DBManager()

    # ==========================================================
    # NILAI KONTRAK & SMKK SYNC
    # ==========================================================
    def update_nilai_kontrak(self, proyek_id, nilai_kontrak):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE proyek_rab SET nilai_kontrak = ? WHERE id = ?",
                (float(nilai_kontrak), proyek_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def get_nilai_kontrak(self, proyek_id):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COALESCE(nilai_kontrak, 0) AS nk FROM proyek_rab WHERE id = ?",
                (proyek_id,)
            )
            row = cursor.fetchone()
            return float(row["nk"]) if row else 0.0
        finally:
            conn.close()

    # ==========================================================
    # PROYEK — READ
    # ==========================================================
    def get_proyek_list(self):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM proyek_rab ORDER BY id DESC")
            return cursor.fetchall()
        finally:
            conn.close()

    def get_proyek_by_id(self, proyek_id):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM proyek_rab WHERE id = ?", (proyek_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    # ==========================================================
    # PROYEK — CREATE / UPDATE / DELETE
    # ==========================================================
    def create_proyek(self, nama_proyek, lokasi, instansi, tahun_anggaran,
                      overhead_pct=10.0, ppn_pct=11.0, tanggal_buat=None):
        import datetime
        if tanggal_buat is None:
            tanggal_buat = datetime.date.today().isoformat()

        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO proyek_rab
                (nama_proyek, lokasi, instansi, tahun_anggaran,
                 overhead_pct, ppn_pct, tanggal_buat)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (nama_proyek, lokasi, instansi, int(tahun_anggaran),
                  float(overhead_pct), float(ppn_pct), tanggal_buat))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def update_proyek(self, proyek_id, data):
        allowed = ["nama_proyek", "lokasi", "instansi", "tahun_anggaran",
                   "overhead_pct", "ppn_pct"]
        sets, vals = [], []
        for k in allowed:
            if k in data:
                sets.append(f"{k} = ?")
                vals.append(data[k])
        if not sets:
            return False
        vals.append(proyek_id)

        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE proyek_rab SET {', '.join(sets)} WHERE id = ?", vals
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def delete_proyek(self, proyek_id):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM item_rab WHERE proyek_id = ?", (proyek_id,))
            cursor.execute("DELETE FROM proyek_rab WHERE id = ?", (proyek_id,))
            conn.commit()
            return True
        finally:
            conn.close()

    # ==========================================================
    # ITEM RAB — READ
    # ==========================================================
    def get_item_rab(self, proyek_id):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM item_rab WHERE proyek_id = ? "
                "ORDER BY divisi ASC, id ASC",
                (proyek_id,)
            )
            return [dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    def get_item_rab_by_id(self, item_id):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM item_rab WHERE id = ?", (item_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    # ==========================================================
    # ITEM RAB — CREATE
    # ==========================================================
    def add_item_rab(self, proyek_id, divisi, kode_item, uraian,
                     satuan, volume, harga_dasar, overhead_pct):
        """
        harga_dasar = D (harga sebelum overhead)
        harga_satuan = F = D × (1 + overhead/100)
        """
        harga_satuan = float(harga_dasar) * (1 + float(overhead_pct) / 100.0)
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO item_rab
                (proyek_id, divisi, kode_item, uraian_pekerjaan, satuan,
                 volume, harga_dasar, overhead_pct, harga_satuan)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (proyek_id, divisi, kode_item, uraian, satuan,
                  float(volume), float(harga_dasar), float(overhead_pct),
                  harga_satuan))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def add_item_from_ahsp(self, proyek_id, template_id, divisi,
                           volume, overhead_pct=10.0):
        """
        Shortcut: hitung D dari template AHSP, lalu insert.
        Return: (item_id, D, F)
        """
        tpl = self._get_template_by_id(template_id)
        if not tpl:
            raise ValueError(f"Template ID {template_id} tidak ditemukan")

        d_val = self._hitung_d_dari_template(template_id)
        f_val = d_val * (1 + float(overhead_pct) / 100.0)

        item_id = self.add_item_rab(
            proyek_id=proyek_id,
            divisi=divisi or tpl["bidang"],
            kode_item=tpl["kode_pekerjaan"],
            uraian=tpl["nama_pekerjaan"],
            satuan=tpl["satuan"],
            volume=volume,
            harga_dasar=d_val,
            overhead_pct=overhead_pct,
        )
        return item_id, d_val, f_val

    # ==========================================================
    # ITEM RAB — UPDATE / DELETE
    # ==========================================================
    def update_item_rab(self, item_id, data):
        allowed = ["divisi", "kode_item", "uraian_pekerjaan", "satuan",
                   "volume", "harga_dasar", "overhead_pct"]
        sets, vals = [], []
        for k in allowed:
            if k in data:
                sets.append(f"{k} = ?")
                vals.append(data[k])
        if not sets:
            return False

        # Recalc harga_satuan if harga_dasar atau overhead berubah
        if "harga_dasar" in data or "overhead_pct" in data:
            existing = self.get_item_rab_by_id(item_id)
            hd = float(data.get("harga_dasar", existing["harga_dasar"]))
            oh = float(data.get("overhead_pct", existing["overhead_pct"]))
            sets.append("harga_satuan = ?")
            vals.append(hd * (1 + oh / 100.0))

        vals.append(item_id)

        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE item_rab SET {', '.join(sets)} WHERE id = ?", vals
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def delete_item_rab(self, item_id):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM item_rab WHERE id = ?", (item_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    # ==========================================================
    # INTEGRASI AHSP
    # ==========================================================
    def get_ahsp_templates(self, bidang=None, jenis=None):
        """Ambil semua template AHSP dari analisis_ahsp_template."""
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            sql = """
                SELECT id, kode_pekerjaan, nama_pekerjaan, satuan, bidang,
                       COALESCE(jenis, 'Informatif') AS jenis
                FROM analisis_ahsp_template WHERE 1=1
            """
            params = []
            if bidang:
                sql += " AND bidang = ?"
                params.append(bidang)
            if jenis:
                sql += " AND COALESCE(jenis,'Informatif') = ?"
                params.append(jenis)
            sql += " ORDER BY bidang, kode_pekerjaan"
            cursor.execute(sql, params)
            return [dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    def _get_template_by_id(self, template_id):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, kode_pekerjaan, nama_pekerjaan, satuan, bidang,
                       COALESCE(jenis, 'Informatif') AS jenis
                FROM analisis_ahsp_template WHERE id = ?
            """, (template_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def _hitung_d_dari_template(self, template_id):
        """D = Σ (koef × harga_satuan) dari analisis_ahsp_detail."""
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.koefisien_standar AS koef, h.harga_satuan
                FROM analisis_ahsp_detail d
                JOIN hsp_data h ON d.komponen_kode = h.kode
                WHERE d.template_id = ?
            """, (template_id,))
            rows = cursor.fetchall()
            return round(sum(float(r["koef"]) * float(r["harga_satuan"])
                             for r in rows), 2)
        finally:
            conn.close()

    def hitung_dan_f_dari_template(self, template_id, overhead_pct=10.0):
        """Return (D, F) untuk preview di dialog."""
        d = self._hitung_d_dari_template(template_id)
        f = round(d * (1 + float(overhead_pct) / 100.0), 2)
        return d, f