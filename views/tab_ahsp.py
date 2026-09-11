# views/tab_ahsp.py
"""
Kalkulator AHSP terpadu untuk Bidang SDA, Bina Marga, dan Cipta Karya
sesuai SE Dirjen Bina Konstruksi No. 47/SE/Dk/2026.

Struktur output mengikuti contoh Lampiran IV (SDA), V (BM), dan VI (CK):
    I.   ASUMSI
    II.  URUTAN KERJA
    III. PEMAKAIAN BAHAN, ALAT DAN TENAGA
    IV.  HARGA DASAR SATUAN UPAH, BAHAN DAN ALAT
    V.   ANALISA HARGA SATUAN PEKERJAAN  (D + E = F, tanpa PPN)
    VI.  WAKTU PELAKSANAAN YANG DIPERLUKAN
    VII. VOLUME PEKERJAAN YANG DIPERLUKAN
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QComboBox, QDoubleSpinBox, QLabel,
    QMessageBox, QGroupBox, QFormLayout, QTextEdit, QSplitter,
    QAbstractItemView, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from database.db_manager import DBManager
from models.ahsp_engine import AHSPEngine
from config.settings import (
    BIDANG_BM, BIDANG_SDA, BIDANG_CK,
    DEFAULT_OVERHEAD_PROFIT, OVERHEAD_PROFIT_MIN, OVERHEAD_PROFIT_MAX,
    SE_NOMOR
)
from config.constants import NORMATIF, INFORMATIF
from utils.helpers import format_rp
from config.theme import get_global_stylesheet, make_heading, apply_property

class TabAHSP(QWidget):
    """Kalkulator AHSP terpadu (BM, CK, SDA) — Lampiran IV, V, VI SE 47/2026."""

    def __init__(self):
        super().__init__()
        self.db = DBManager()
        self.engine = AHSPEngine()
        self.template_id = None
        self.template_data = None
        self.setStyleSheet(get_global_stylesheet())
        self.init_ui()

    # ==========================================================
    # UI
    # ==========================================================
    def init_ui(self):
        layout = QVBoxLayout(self)

        lbl_judul = QLabel("Kalkulator AHSP Terpadu — Bidang SDA, Bina Marga, Cipta Karya")
        lbl_judul.setStyleSheet("font-weight: bold; font-size: 14px; color: #0d47a1;")
        layout.addWidget(lbl_judul)

        lbl_sub = QLabel(f"Acuan: SE Dirjen Bina Konstruksi No. {SE_NOMOR} — Lampiran IV, V, VI")
        lbl_sub.setStyleSheet("font-style: italic; color: #555;")
        layout.addWidget(lbl_sub)

        # Filter bar
        bar = QHBoxLayout()
        bar.addWidget(QLabel("Bidang:"))
        self.cb_bidang = QComboBox()
        self.cb_bidang.addItem("-- Semua Bidang --", None)
        self.cb_bidang.addItem(BIDANG_SDA, BIDANG_SDA)
        self.cb_bidang.addItem(BIDANG_BM, BIDANG_BM)
        self.cb_bidang.addItem(BIDANG_CK, BIDANG_CK)
        bar.addWidget(self.cb_bidang)

        bar.addWidget(QLabel("Jenis:"))
        self.cb_jenis = QComboBox()
        self.cb_jenis.addItem("-- Semua --", None)
        self.cb_jenis.addItem(NORMATIF, NORMATIF)
        self.cb_jenis.addItem(INFORMATIF, INFORMATIF)
        bar.addWidget(self.cb_jenis)

        bar.addWidget(QLabel("Template Pekerjaan:"))
        self.cb_template = QComboBox()
        self.cb_template.setMinimumWidth(420)
        bar.addWidget(self.cb_template, 1)
        bar.addStretch()
        layout.addLayout(bar)

        # Splitter: tabel komponen | preview blok I-VII
        splitter = QSplitter(Qt.Horizontal)

        # === KIRI ===
        left = QWidget()
        lv = QVBoxLayout(left)
        lv.setContentsMargins(0, 0, 4, 0)

        tb = QHBoxLayout()
        self.btn_tambah = QPushButton("+ Tambah Baris")
        self.btn_hapus = QPushButton("- Hapus Baris")
        self.btn_export = QPushButton("Ekspor AHSP")
        tb.addWidget(self.btn_tambah)
        tb.addWidget(self.btn_hapus)
        tb.addStretch()
        tb.addWidget(self.btn_export)
        lv.addLayout(tb)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Kelompok", "Kode HSP", "Uraian Komponen",
            "Satuan", "Koefisien", "Harga Satuan (Rp)", "Jumlah (Rp)"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        lv.addWidget(self.table)
        splitter.addWidget(left)

        # === KANAN ===
        right = QWidget()
        rv = QVBoxLayout(right)
        rv.setContentsMargins(4, 0, 0, 0)
        self.txt_blok = QTextEdit()
        self.txt_blok.setReadOnly(True)
        self.txt_blok.setFont(QFont("Consolas", 9))
        self.txt_blok.setPlaceholderText("Blok I-VII AHSP akan tampil di sini...")
        rv.addWidget(self.txt_blok)
        splitter.addWidget(right)
        splitter.setSizes([750, 550])
        layout.addWidget(splitter, 1)

        # Panel rekap
        panel = QGroupBox("V. Analisa Harga Satuan Pekerjaan")
        form = QFormLayout()

        self.lbl_a = QLabel("Rp 0,00")
        self.lbl_b = QLabel("Rp 0,00")
        self.lbl_c = QLabel("Rp 0,00")
        self.lbl_d = QLabel("Rp 0,00")

        self.spin_overhead = QDoubleSpinBox()
        self.spin_overhead.setRange(OVERHEAD_PROFIT_MIN, OVERHEAD_PROFIT_MAX)
        self.spin_overhead.setValue(DEFAULT_OVERHEAD_PROFIT)
        self.spin_overhead.setSuffix(" %")
        self.spin_overhead.setDecimals(2)

        self.lbl_e = QLabel("Rp 0,00")
        self.lbl_f = QLabel("Rp 0,00")

        form.addRow("A. Jumlah Harga Tenaga Kerja:", self.lbl_a)
        form.addRow("B. Jumlah Harga Bahan:", self.lbl_b)
        form.addRow("C. Jumlah Harga Peralatan:", self.lbl_c)
        form.addRow("D. Jumlah Harga (A + B + C):", self.lbl_d)
        form.addRow("E. Overhead & Profit (10% × D):", self.spin_overhead)
        form.addRow("E. Nilai Overhead:", self.lbl_e)
        form.addRow("F. Harga Satuan Pekerjaan (D + E):", self.lbl_f)
        panel.setLayout(form)
        layout.addWidget(panel)

        # Koneksi
        self.cb_bidang.currentIndexChanged.connect(self.load_templates_to_combo)
        self.cb_jenis.currentIndexChanged.connect(self.load_templates_to_combo)
        self.cb_template.currentIndexChanged.connect(self.load_template_details)
        self.btn_tambah.clicked.connect(self.tambah_baris_kosong)
        self.btn_hapus.clicked.connect(self.hapus_baris)
        self.spin_overhead.valueChanged.connect(self.hitung_total)
        self.btn_export.clicked.connect(self.export_ahsp)

        self.load_templates_to_combo()

    # ==========================================================
    # TEMPLATE LOADER
    # ==========================================================
    def load_templates_to_combo(self):
        self.cb_template.blockSignals(True)
        self.cb_template.clear()
        self.cb_template.addItem("-- Pilih Analisis Pekerjaan --", None)

        bidang = self.cb_bidang.currentData()
        jenis = self.cb_jenis.currentData()

        conn = self.db.get_connection()
        try:
            cur = conn.cursor()
            sql = ("SELECT id, kode_pekerjaan, nama_pekerjaan, bidang, "
                   "COALESCE(jenis,'Informatif') AS jenis FROM analisis_ahsp_template WHERE 1=1")
            params = []
            if bidang:
                sql += " AND bidang = ?"
                params.append(bidang)
            if jenis:
                sql += " AND COALESCE(jenis,'Informatif') = ?"
                params.append(jenis)
            sql += " ORDER BY bidang, kode_pekerjaan"
            cur.execute(sql, params)
            for row in cur.fetchall():
                self.cb_template.addItem(
                    f"[{row['bidang']}] [{row['kode_pekerjaan']}] {row['nama_pekerjaan']}",
                    row["id"]
                )
        finally:
            conn.close()
        self.cb_template.blockSignals(False)

    def load_template_details(self):
        self.template_id = self.cb_template.currentData()
        if not self.template_id:
            self.table.setRowCount(0)
            self.txt_blok.clear()
            self._reset_rekap()
            return

        conn = self.db.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM analisis_ahsp_template WHERE id = ?", (self.template_id,))
            self.template_data = dict(cur.fetchone())

            cur.execute("""
                SELECT d.koefisien_standar AS koef,
                       h.kode, h.uraian, h.kategori, h.satuan, h.harga_satuan
                FROM analisis_ahsp_detail d
                JOIN hsp_data h ON d.komponen_kode = h.kode
                WHERE d.template_id = ?
                ORDER BY h.kategori, h.kode
            """, (self.template_id,))
            rows = cur.fetchall()
        finally:
            conn.close()

        self.table.setRowCount(0)
        for row in rows:
            r = self.table.rowCount()
            self.table.insertRow(r)
            kat = row["kategori"] or "-"
            kat_singkat = {
                "Tenaga Kerja": "A. TENAGA",
                "Bahan": "B. BAHAN",
                "Peralatan": "C. PERALATAN",
            }.get(kat, kat)
            self._set_row(
                r, kat_singkat, row["kode"], row["uraian"], row["satuan"],
                f"{row['koef']:.4f}", f"{float(row['harga_satuan']):.2f}"
            )

        self.hitung_total()

    # ==========================================================
    # BARIS HELPERS
    # ==========================================================
    def _set_row(self, r, kelompok, kode, uraian, satuan, koef, harga):
        for c, val in enumerate([kelompok, kode, uraian, satuan, koef, harga, "0.00"]):
            item = QTableWidgetItem(str(val))
            if c == 0:
                item.setBackground(QColor("#E3F2FD"))
            if c >= 4:
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(r, c, item)

    def _reset_rekap(self):
        for lbl in (self.lbl_a, self.lbl_b, self.lbl_c, self.lbl_d, self.lbl_e, self.lbl_f):
            lbl.setText("Rp 0,00")

    def tambah_baris_kosong(self):
        r = self.table.rowCount()
        self.table.insertRow(r)
        self._set_row(r, "C. PERALATAN", "Manual", "Komponen tambahan kustom",
                      "Ls", "1.0000", "0.00")

    def hapus_baris(self):
        sel = self.table.selectedItems()
        if not sel:
            return
        self.table.removeRow(sel[0].row())
        self.hitung_total()

    # ==========================================================
    # HITUNG A s.d F
    # ==========================================================
    def hitung_total(self):
        total_a = total_b = total_c = 0.0
        for r in range(self.table.rowCount()):
            try:
                kel = (self.table.item(r, 0).text() or "").upper()
                koef = float((self.table.item(r, 4).text() or "0").replace(",", "."))
                harga = float((self.table.item(r, 5).text() or "0").replace(",", "."))
                jumlah = koef * harga
                self.table.setItem(r, 6, QTableWidgetItem(f"{jumlah:.2f}"))
                if "A. TENAGA" in kel:
                    total_a += jumlah
                elif "B. BAHAN" in kel:
                    total_b += jumlah
                elif "C. PERALATAN" in kel:
                    total_c += jumlah
            except (ValueError, AttributeError):
                continue

        d = total_a + total_b + total_c
        oh_pct = self.spin_overhead.value() / 100.0
        e = d * oh_pct
        f = d + e

        self.lbl_a.setText(format_rp(total_a))
        self.lbl_b.setText(format_rp(total_b))
        self.lbl_c.setText(format_rp(total_c))
        self.lbl_d.setText(format_rp(d))
        self.lbl_e.setText(format_rp(e))
        self.lbl_f.setText(format_rp(f))
        self._render_blok(total_a, total_b, total_c, d, e, f, oh_pct * 100)

    # ==========================================================
    # RENDER BLOK I - VII
    # ==========================================================
    def _render_blok(self, a, b, c, d, e, f, oh_pct):
        t = self.template_data or {}
        L = []
        L.append("=" * 78)
        L.append("I.   ASUMSI")
        L.append("=" * 78)
        L.append(f"Kode Pekerjaan : {t.get('kode_pekerjaan', '-')}")
        L.append(f"Nama Pekerjaan : {t.get('nama_pekerjaan', '-')}")
        L.append(f"Satuan         : {t.get('satuan', '-')}")
        L.append(f"Bidang         : {t.get('bidang', '-')}")
        L.append(f"Jenis          : {t.get('jenis', 'Informatif')}")
        L.append("")
        L.append("=" * 78)
        L.append("II.  URUTAN KERJA")
        L.append("=" * 78)
        L.append("(Mengikuti urutan kerja Lampiran SE 47/SE/Dk/2026)")
        L.append("")
        L.append("=" * 78)
        L.append("III. PEMAKAIAN BAHAN, ALAT DAN TENAGA")
        L.append("=" * 78)
        for r in range(self.table.rowCount()):
            kel = self.table.item(r, 0).text()
            kode = self.table.item(r, 1).text()
            uraian = self.table.item(r, 2).text()
            satuan = self.table.item(r, 3).text()
            koef = self.table.item(r, 4).text()
            harga = self.table.item(r, 5).text()
            L.append(f"  [{kel:<13}] {kode:<12} {uraian:<38} {satuan:<6} {koef:<10} Rp {harga}")
        L.append("")
        L.append("=" * 78)
        L.append("IV.  HARGA DASAR SATUAN UPAH, BAHAN DAN ALAT")
        L.append("=" * 78)
        L.append("Lihat lampiran harga satuan pokok (HSP) pada SIPASTI.")
        L.append("")
        L.append("=" * 78)
        L.append("V.   ANALISA HARGA SATUAN PEKERJAAN")
        L.append("=" * 78)
        L.append(f"A. Jumlah Harga Tenaga Kerja : {format_rp(a)}")
        L.append(f"B. Jumlah Harga Bahan         : {format_rp(b)}")
        L.append(f"C. Jumlah Harga Peralatan     : {format_rp(c)}")
        L.append(f"D. Jumlah Harga (A+B+C)       : {format_rp(d)}")
        L.append(f"E. Overhead & Profit ({oh_pct:.2f}% × D) : {format_rp(e)}")
        L.append(f"F. HARGA SATUAN PEKERJAAN (D+E) : {format_rp(f)}")
        L.append("")
        L.append("=" * 78)
        L.append("VI.  WAKTU PELAKSANAAN YANG DIPERLUKAN")
        L.append("=" * 78)
        L.append("Masa Pelaksanaan : ....... bulan")
        L.append("")
        L.append("=" * 78)
        L.append("VII. VOLUME PEKERJAAN YANG DIPERLUKAN")
        L.append("=" * 78)
        L.append(f"Volume Pekerjaan : 1,00 {t.get('satuan', '')}")
        L.append("")
        L.append("Catatan: Harga Satuan Pekerjaan (F) BELUM termasuk PPN.")
        L.append("         PPN ditambahkan pada Rekapitulasi RAB/HPS.")
        self.txt_blok.setPlainText("\n".join(L))

    # ==========================================================
    # EKSPOR
    # ==========================================================
    def export_ahsp(self):
        if not self.template_id:
            QMessageBox.warning(self, "Peringatan", "Pilih template pekerjaan terlebih dahulu.")
            return
        kode = self.template_data.get('kode_pekerjaan', 'manual')
        kode = kode.replace('.', '_').replace('(', '').replace(')', '')
        default = f"AHSP_{kode}.txt"
        path, _ = QFileDialog.getSaveFileName(self, "Simpan AHSP", default, "Text (*.txt);;All Files (*)")
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(self.txt_blok.toPlainText())
            QMessageBox.information(self, "Sukses", f"AHSP disimpan ke:\n{path}")
        except Exception as ex:
            QMessageBox.critical(self, "Error", str(ex))