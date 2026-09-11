from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, 
                             QTextEdit, QCheckBox, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QFormLayout, QMessageBox, QGroupBox)
from config.theme import get_global_stylesheet
from models.usulan_model import UsulanModel
from config.theme import get_global_stylesheet, make_heading, apply_property

class TabUsulan(QWidget):
    def __init__(self):
        super().__init__()
        self.model = UsulanModel()
        self.setStyleSheet(get_global_stylesheet())
        self.init_ui()
    def init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Lampiran VII: Pengajuan Usulan AHSP Baru / Perubahan (Mayor & Minor)")
        layout.addWidget(make_heading("Lampiran VII: Pengajuan Usulan AHSP Baru / Perubahan (Mayor & Minor)"))
        layout.addWidget(title)

        group_box = QGroupBox("Formulir Usulan AHSP & Templat Semula-Menjadi")
        form = QFormLayout()

        self.txt_surat = QLineEdit()
        self.txt_surat.setPlaceholderText("Contoh: UM.01.02/Balai-SDA/123/2026")
        self.txt_pengusul = QLineEdit("Balai / Dinas Teknis / K/L/I")
        
        self.combo_jenis = QComboBox()
        self.combo_jenis.addItems(["Baru", "Perubahan Mayor", "Perubahan Minor"])

        self.txt_pekerjaan = QLineEdit()
        self.txt_justifikasi = QTextEdit()
        self.txt_justifikasi.setMaximumHeight(80)

        self.chk_sptjm = QCheckBox("Melampirkan Surat Pertanggungjawaban Mutlak (SPTJM)")

        form.addRow("Nomor Surat Usulan:", self.txt_surat)
        form.addRow("Unit Pengusul:", self.txt_pengusul)
        form.addRow("Jenis Usulan:", self.combo_jenis)
        form.addRow("Nama Item Pekerjaan:", self.txt_pekerjaan)
        form.addRow("Justifikasi Teknis:", self.txt_justifikasi)
        form.addRow("Kelengkapan SPTJM:", self.chk_sptjm)

        btn_submit = QPushButton("Kirim Usulan AHSP")
        btn_submit.setStyleSheet("background-color: #0277bd; color: white; font-weight: bold;")
        btn_submit.clicked.connect(self.submit_usulan)

        form.addRow(btn_submit)
        group_box.setLayout(form)
        layout.addWidget(group_box)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "ID", "No. Surat", "Pengusul", "Jenis", "Nama Pekerjaan", "SPTJM", "Tgl Usulan"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.load_data()

    def submit_usulan(self):
        surat = self.txt_surat.text()
        pengusul = self.txt_pengusul.text()
        jenis = self.combo_jenis.currentText()
        pekerjaan = self.txt_pekerjaan.text()
        justifikasi = self.txt_justifikasi.toPlainText()
        sptjm = 1 if self.chk_sptjm.isChecked() else 0

        if not surat or not pekerjaan:
            QMessageBox.warning(self, "Peringatan", "Nomor Surat dan Nama Pekerjaan wajib diisi!")
            return

        self.model.create_usulan(surat, pengusul, jenis, pekerjaan, justifikasi, sptjm, "2026-09-09")
        QMessageBox.information(self, "Sukses", "Usulan AHSP berhasil didaftarkan!")
        self.load_data()

    def load_data(self):
        rows = self.model.get_all_usulan()
        self.table.setRowCount(0)
        for r_idx, row in enumerate(rows):
            self.table.insertRow(r_idx)
            self.table.setItem(r_idx, 0, QTableWidgetItem(str(row['id'])))
            self.table.setItem(r_idx, 1, QTableWidgetItem(str(row['nomor_surat'])))
            self.table.setItem(r_idx, 2, QTableWidgetItem(str(row['pengusul'])))
            self.table.setItem(r_idx, 3, QTableWidgetItem(str(row['jenis_usulan'])))
            self.table.setItem(r_idx, 4, QTableWidgetItem(str(row['nama_pekerjaan'])))
            self.table.setItem(r_idx, 5, QTableWidgetItem("Ada" if row['sptjm_status'] == 1 else "Tidak"))
            self.table.setItem(r_idx, 6, QTableWidgetItem(str(row['tanggal_usulan'])))