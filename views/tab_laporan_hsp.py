# views/tab_laporan_hsp.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QLineEdit, QFormLayout, QMessageBox,
    QGroupBox, QAbstractItemView
)
from PyQt5.QtCore import Qt

from models.laporan_hsp_model import LaporanHSPModel
from config.theme import get_global_stylesheet, make_heading, apply_property


class TabLaporanHSP(QWidget):
    def __init__(self):
        super().__init__()
        self.model = LaporanHSPModel()
        self.setStyleSheet(get_global_stylesheet())
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        layout.addWidget(make_heading(
            "Laporan Pengumpulan Data Harga Satuan Pokok (HSP) Sektor Konstruksi — Balai Teknis"
        ))
        sub = QLabel(
            "Sesuai SE Dirjen Bina Konstruksi No. 47/SE/Dk/2026 Huruf F "
            "(Proses Bisnis Perencanaan, Pengumpulan, Pemeriksaan & Penetapan BA)"
        )
        apply_property(sub, "subheading", True)
        layout.addWidget(sub)

        group_box = QGroupBox("Input Berita Acara Penetapan Harga Satuan Pokok Balai")
        form_layout = QFormLayout()

        self.txt_ba = QLineEdit()
        self.txt_ba.setPlaceholderText("Contoh: BA.01/BALAI-SDA/X/2026")
        self.txt_balai = QLineEdit("Balai Teknik BWS / BP2JK")
        self.txt_tahun = QLineEdit("2026")
        self.txt_petugas = QLineEdit("Petugas Lapangan A")
        self.txt_pengawas = QLineEdit("Pengawas B")
        self.txt_pengolah = QLineEdit("Pengolah Data C")
        self.txt_tgl_penetapan = QLineEdit("2026-10-31")

        form_layout.addRow("Nomor Berita Acara (BA):", self.txt_ba)
        form_layout.addRow("Nama Balai Teknis / UPT:", self.txt_balai)
        form_layout.addRow("Tahun Anggaran:", self.txt_tahun)
        form_layout.addRow("Petugas Lapangan (Survei):", self.txt_petugas)
        form_layout.addRow("Pengawas (Verifikasi & Validasi):", self.txt_pengawas)
        form_layout.addRow("Pengolah Data (Entry SIPASTI):", self.txt_pengolah)
        form_layout.addRow("Tanggal Penetapan BA (Maks 31 Okt):", self.txt_tgl_penetapan)

        btn_simpan = QPushButton("Simpan Berita Acara & Penetapan Data")
        apply_property(btn_simpan, "accent", "success")
        btn_simpan.clicked.connect(self.simpan_laporan)
        form_layout.addRow(btn_simpan)

        group_box.setLayout(form_layout)
        layout.addWidget(group_box)

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            "ID", "No. BA Penetapan", "Balai Teknis", "Tahun",
            "Petugas Lapangan", "Pengawas", "Pengolah Data", "Tgl Penetapan"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        self.load_data()

    def simpan_laporan(self):
        ba = self.txt_ba.text().strip()
        balai = self.txt_balai.text().strip()
        tahun_str = self.txt_tahun.text().strip()
        petugas = self.txt_petugas.text().strip()
        pengawas = self.txt_pengawas.text().strip()
        pengolah = self.txt_pengolah.text().strip()
        tgl = self.txt_tgl_penetapan.text().strip()

        if not ba or not balai:
            QMessageBox.warning(self, "Peringatan", "Nomor BA dan Nama Balai wajib diisi!")
            return
        try:
            tahun = int(tahun_str)
        except ValueError:
            QMessageBox.warning(self, "Peringatan", "Tahun harus berupa angka!")
            return

        try:
            self.model.create_laporan(
                ba, balai, tahun, petugas, pengawas, pengolah, tgl, "Tervalidasi"
            )
            QMessageBox.information(
                self, "Sukses",
                f"Berita Acara Penetapan Harga HSP {ba} berhasil disimpan!"
            )
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan: {e}")

    def load_data(self):
        try:
            rows = self.model.get_all_laporan()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal memuat data: {e}")
            return

        self.table.setRowCount(0)
        for r_idx, row in enumerate(rows):
            self.table.insertRow(r_idx)
            # FIX: sqlite3.Row tidak support slicing — konversi ke list dulu
            values = list(row)
            # Buang kolom terakhir (status_rekonsiliasi) sesuai kolom tabel 8
            for c_idx, val in enumerate(values[:-1]):
                if c_idx >= self.table.columnCount():
                    break
                self.table.setItem(r_idx, c_idx, QTableWidgetItem(str(val)))