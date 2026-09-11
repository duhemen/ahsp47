from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QHeaderView, 
                             QDialog, QLabel, QLineEdit, QFormLayout, QMessageBox)
from PyQt5.QtCore import Qt
from models.acuan_model import AcuanModel
from config.theme import get_global_stylesheet, make_heading, apply_property

class AcuanDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.data = data
        self.setStyleSheet(get_global_stylesheet())
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Tambah / Ubah Data Acuan Konversi")
        self.resize(400, 250)
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        self.input_material = QLineEdit()
        self.input_kondisi = QLineEdit()
        self.input_asli = QLineEdit("1.000")
        self.input_lepas = QLineEdit("1.000")
        self.input_padat = QLineEdit("1.000")
        
        form_layout.addRow(QLabel("Jenis Tanah / Bahan:"), self.input_material)
        form_layout.addRow(QLabel("Kondisi Semula:"), self.input_kondisi)
        form_layout.addRow(QLabel("Kondisi Asli (A):"), self.input_asli)
        form_layout.addRow(QLabel("Kondisi Lepas (B):"), self.input_lepas)
        form_layout.addRow(QLabel("Kondisi Padat (C):"), self.input_padat)
        
        layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        self.btn_simpan = QPushButton("Simpan")
        self.btn_batal = QPushButton("Batal")
        self.btn_simpan.clicked.connect(self.accept)
        self.btn_batal.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_simpan)
        btn_layout.addWidget(self.btn_batal)
        layout.addLayout(btn_layout)
        
        if self.data:
            self.input_material.setText(str(self.data.get('jenis_tanah_bahan', '')))
            self.input_kondisi.setText(str(self.data.get('kondisi_semula', '')))
            self.input_asli.setText(str(self.data.get('fk_asli', '1.000')))
            self.input_lepas.setText(str(self.data.get('fk_lepas', '1.000')))
            self.input_padat.setText(str(self.data.get('fk_padat', '1.000')))

    def get_data(self):
        return {
            'jenis_tanah_bahan': self.input_material.text().strip(),
            'kondisi_semula': self.input_kondisi.text().strip(),
            'fk_asli': float(self.input_asli.text().replace(',', '.') or 1.0),
            'fk_lepas': float(self.input_lepas.text().replace(',', '.') or 1.0),
            'fk_padat': float(self.input_padat.text().replace(',', '.') or 1.0)
        }

class TabAcuan(QWidget):
    def __init__(self):
        super().__init__()
        self.model = AcuanModel()
        self.setStyleSheet(get_global_stylesheet())
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        toolbar = QHBoxLayout()
        self.btn_tambah = QPushButton("➕ Tambah Acuan")
        self.btn_ubah = QPushButton("✏️ Ubah Data")
        self.btn_hapus = QPushButton("🗑️ Hapus Data")
        self.btn_refresh = QPushButton("🔄 Refresh")
        
        toolbar.addWidget(self.btn_tambah)
        toolbar.addWidget(self.btn_ubah)
        toolbar.addWidget(self.btn_hapus)
        toolbar.addStretch()
        toolbar.addWidget(self.btn_refresh)
        layout.addLayout(toolbar)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Jenis Tanah / Bahan", "Kondisi Semula", 
            "Kondisi Asli (A)", "Kondisi Lepas (B)", "Kondisi Padat (C)"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        layout.addWidget(self.table)
        
        self.btn_tambah.clicked.connect(self.tambah_data)
        self.btn_ubah.clicked.connect(self.ubah_data)
        self.btn_hapus.clicked.connect(self.hapus_data)
        self.btn_refresh.clicked.connect(self.load_data)
        
        self.load_data()
        
    def load_data(self):
        self.table.setRowCount(0)
        rows = self.model.get_all_konversi()
        for row in rows:
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row.get('id', ''))))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(row.get('jenis_tanah_bahan', ''))))
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(row.get('kondisi_semula', ''))))
            self.table.setItem(row_idx, 3, QTableWidgetItem(f"{row.get('fk_asli', 1.0):.3f}"))
            self.table.setItem(row_idx, 4, QTableWidgetItem(f"{row.get('fk_lepas', 1.0):.3f}"))
            self.table.setItem(row_idx, 5, QTableWidgetItem(f"{row.get('fk_padat', 1.0):.3f}"))

    def tambah_data(self):
        dialog = AcuanDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            new_data = dialog.get_data()
            if hasattr(self.model, 'add_acuan'):
                self.model.add_acuan(new_data)
            QMessageBox.information(self, "Sukses", "Data acuan baru berhasil disimpan!")
            self.load_data()

    def ubah_data(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Peringatan", "Pilih baris yang ingin diubah!")
            return
        row_idx = selected[0].row()
        data = {
            'id': int(self.table.item(row_idx, 0).text()),
            'jenis_tanah_bahan': self.table.item(row_idx, 1).text(),
            'kondisi_semula': self.table.item(row_idx, 2).text(),
            'fk_asli': self.table.item(row_idx, 3).text(),
            'fk_lepas': self.table.item(row_idx, 4).text(),
            'fk_padat': self.table.item(row_idx, 5).text(),
        }
        dialog = AcuanDialog(self, data)
        if dialog.exec_() == QDialog.Accepted:
            updated_data = dialog.get_data()
            if hasattr(self.model, 'update_acuan'):
                self.model.update_acuan(data['id'], updated_data)
            QMessageBox.information(self, "Sukses", "Data acuan berhasil diperbarui!")
            self.load_data()

    def hapus_data(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Peringatan", "Pilih data yang ingin dihapus!")
            return
        row_idx = selected[0].row()
        acuan_id = int(self.table.item(row_idx, 0).text())
        reply = QMessageBox.question(self, "Konfirmasi", "Hapus data acuan ini?", 
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if hasattr(self.model, 'delete_acuan'):
                self.model.delete_acuan(acuan_id)
            QMessageBox.information(self, "Sukses", "Data berhasil dihapus!")
            self.load_data()
