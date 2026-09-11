# views/tab_hsp.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QHBoxLayout, QDialog, QFormLayout, QLineEdit, QComboBox,
    QDoubleSpinBox, QDateEdit, QMessageBox, QAbstractItemView
)
from PyQt5.QtCore import Qt, QDate
from models.hsp_model import HSPModel
from utils.helpers import format_rp, parse_rp
from config.theme import get_global_stylesheet, make_heading, apply_property

class HSPDialog(QDialog):
    """Dialog form untuk Tambah/Ubah data HSP."""

    KATEGORI_OPTIONS = ["Tenaga Kerja", "Bahan", "Peralatan"]

    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.data = data
        self.setWindowTitle("Tambah Data HSP" if data is None else "Ubah Data HSP")
        self.setModal(True)
        self.resize(500, 400)
        self.init_ui()
        if data:
            self.populate_data(data)
        self.setStyleSheet(get_global_stylesheet())

    def init_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        label = QLabel("Lampiran I: Database Harga Satuan Pokok...")
        apply_property(label, "heading", True)

        self.input_kode = QLineEdit()
        self.input_kode.setPlaceholderText("Contoh: L.01, B.01, P.01")
        form.addRow("Kode:", self.input_kode)

        self.input_uraian = QLineEdit()
        self.input_uraian.setPlaceholderText("Uraian komponen HSP")
        form.addRow("Uraian:", self.input_uraian)

        self.input_kategori = QComboBox()
        self.input_kategori.addItems(self.KATEGORI_OPTIONS)
        form.addRow("Kategori:", self.input_kategori)

        self.input_satuan = QLineEdit()
        self.input_satuan.setPlaceholderText("Contoh: OH, M2, M3, KG, BUAH")
        form.addRow("Satuan:", self.input_satuan)

        self.input_harga = QDoubleSpinBox()
        self.input_harga.setDecimals(2)
        self.input_harga.setMaximum(999999999999.99)
        self.input_harga.setGroupSeparatorShown(True)
        self.input_harga.setPrefix("Rp ")
        form.addRow("Harga Satuan:", self.input_harga)

        self.input_sumber = QLineEdit()
        self.input_sumber.setPlaceholderText("Nama vendor / sumber harga")
        form.addRow("Sumber/Vendor:", self.input_sumber)

        self.input_tanggal = QDateEdit()
        self.input_tanggal.setCalendarPopup(True)
        self.input_tanggal.setDate(QDate.currentDate())
        self.input_tanggal.setDisplayFormat("yyyy-MM-dd")
        form.addRow("Tanggal Survei:", self.input_tanggal)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_ok = QPushButton("Simpan")
        self.btn_ok.clicked.connect(self.accept)
        self.btn_ok.setDefault(True)
        btn_layout.addWidget(self.btn_ok)
        self.btn_cancel = QPushButton("Batal")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

    def populate_data(self, data):
        self.input_kode.setText(str(data.get('kode', '')))
        self.input_kode.setReadOnly(True)
        self.input_uraian.setText(str(data.get('uraian', '')))

        kategori = str(data.get('kategori', ''))
        idx = self.input_kategori.findText(kategori)
        if idx >= 0:
            self.input_kategori.setCurrentIndex(idx)

        self.input_satuan.setText(str(data.get('satuan', '')))
        self.input_harga.setValue(float(data.get('harga_satuan', 0)))
        self.input_sumber.setText(str(data.get('sumber_vendor', '')))

        tgl = data.get('tanggal_survei')
        if tgl:
            self.input_tanggal.setDate(QDate.fromString(str(tgl), "yyyy-MM-dd"))

    def get_data(self):
        return {
            'kode': self.input_kode.text().strip(),
            'uraian': self.input_uraian.text().strip(),
            'kategori': self.input_kategori.currentText(),
            'satuan': self.input_satuan.text().strip(),
            'harga_satuan': self.input_harga.value(),
            'sumber_vendor': self.input_sumber.text().strip() or None,
            'tanggal_survei': self.input_tanggal.date().toString("yyyy-MM-dd")
        }

    def validate(self):
        if not self.input_kode.text().strip():
            QMessageBox.warning(self, "Validasi", "Kode wajib diisi!")
            self.input_kode.setFocus()
            return False
        if not self.input_uraian.text().strip():
            QMessageBox.warning(self, "Validasi", "Uraian wajib diisi!")
            self.input_uraian.setFocus()
            return False
        if not self.input_satuan.text().strip():
            QMessageBox.warning(self, "Validasi", "Satuan wajib diisi!")
            self.input_satuan.setFocus()
            return False
        if self.input_harga.value() <= 0:
            QMessageBox.warning(self, "Validasi", "Harga satuan harus lebih dari 0!")
            self.input_harga.setFocus()
            return False
        return True


class TabHSP(QWidget):
    def __init__(self):
        super().__init__()
        self.model = HSPModel()
        self.setStyleSheet(get_global_stylesheet())
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        label = QLabel("Lampiran I: Database Harga Satuan Pokok Sektor Konstruksi (Upah, Bahan, Peralatan)")
        apply_property(label, "heading", True)
        layout.addWidget(label)

        toolbar = QHBoxLayout()

        self.btn_add = QPushButton("Tambah Data")
        self.btn_add.setIcon(self.style().standardIcon(self.style().SP_FileIcon))
        self.btn_add.clicked.connect(self.on_add)
        toolbar.addWidget(self.btn_add)

        self.btn_edit = QPushButton("Ubah Harga")
        self.btn_edit.setIcon(self.style().standardIcon(self.style().SP_FileDialogDetailedView))
        self.btn_edit.clicked.connect(self.on_edit)
        toolbar.addWidget(self.btn_edit)

        self.btn_delete = QPushButton("Hapus Data")
        self.btn_delete.setIcon(self.style().standardIcon(self.style().SP_TrashIcon))
        self.btn_delete.setStyleSheet("QPushButton { color: red; }")
        self.btn_delete.clicked.connect(self.on_delete)
        toolbar.addWidget(self.btn_delete)

        toolbar.addStretch()

        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.clicked.connect(self.load_data)
        toolbar.addWidget(self.btn_refresh)

        layout.addLayout(toolbar)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Kode", "Uraian Komponen", "Kategori", "Satuan",
            "Harga Satuan Dasar", "Sumber/Vendor"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.doubleClicked.connect(self.on_edit)
        layout.addWidget(self.table)

        self.load_data()

    def load_data(self):
        rows = self.model.get_all_hsp()
        self.table.setRowCount(0)
        for r_idx, row in enumerate(rows):
            self.table.insertRow(r_idx)
            self.table.setItem(r_idx, 0, QTableWidgetItem(str(row['id'])))
            self.table.setItem(r_idx, 1, QTableWidgetItem(str(row['kode'])))
            self.table.setItem(r_idx, 2, QTableWidgetItem(str(row['uraian'])))
            self.table.setItem(r_idx, 3, QTableWidgetItem(str(row['kategori'])))
            self.table.setItem(r_idx, 4, QTableWidgetItem(str(row['satuan'])))
            self.table.setItem(r_idx, 5, QTableWidgetItem(format_rp(row['harga_satuan'])))
            self.table.setItem(r_idx, 6, QTableWidgetItem(str(row['sumber_vendor'] or '')))

    def get_selected_kode(self):
        selected = self.table.currentRow()
        if selected < 0:
            return None
        kode_item = self.table.item(selected, 1)
        return kode_item.text() if kode_item else None

    def get_selected_row_data(self):
        selected = self.table.currentRow()
        if selected < 0:
            return None
        return {
            'id': self.table.item(selected, 0).text() if self.table.item(selected, 0) else None,
            'kode': self.table.item(selected, 1).text() if self.table.item(selected, 1) else None,
            'uraian': self.table.item(selected, 2).text() if self.table.item(selected, 2) else None,
            'kategori': self.table.item(selected, 3).text() if self.table.item(selected, 3) else None,
            'satuan': self.table.item(selected, 4).text() if self.table.item(selected, 4) else None,
            'harga_satuan': parse_rp(self.table.item(selected, 5).text()) if self.table.item(selected, 5) else 0,
            'sumber_vendor': self.table.item(selected, 6).text() if self.table.item(selected, 6) else None,
        }

    def on_add(self):
        dialog = HSPDialog(self, data=None)
        if dialog.exec_() == QDialog.Accepted:
            if not dialog.validate():
                return
            data = dialog.get_data()
            try:
                new_id = self.model.add_hsp(data)
                if new_id:
                    QMessageBox.information(self, "Sukses", f"Data HSP berhasil ditambahkan (ID: {new_id}).")
                    self.load_data()
                else:
                    QMessageBox.warning(self, "Gagal", "Gagal menambahkan data.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal menambah data: {str(e)}")

    def on_edit(self):
        kode = self.get_selected_kode()
        if not kode:
            QMessageBox.information(self, "Info", "Pilih baris data yang akan diubah terlebih dahulu.")
            return
        row_data = self.get_selected_row_data()
        dialog = HSPDialog(self, data=row_data)
        if dialog.exec_() == QDialog.Accepted:
            if not dialog.validate():
                return
            data = dialog.get_data()
            try:
                success = self.model.update_hsp(kode, data)
                if success:
                    QMessageBox.information(self, "Sukses", "Data HSP berhasil diperbarui.")
                    self.load_data()
                else:
                    QMessageBox.warning(self, "Gagal", "Data tidak ditemukan atau gagal diupdate.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal mengubah data: {str(e)}")

    def on_delete(self):
        kode = self.get_selected_kode()
        if not kode:
            QMessageBox.information(self, "Info", "Pilih baris data yang akan dihapus terlebih dahulu.")
            return
        row_data = self.get_selected_row_data()
        uraian = row_data.get('uraian', '') if row_data else ''
        reply = QMessageBox.question(
            self, "Konfirmasi Hapus",
            f"Yakin hapus data HSP?\nKode: {kode}\nUraian: {uraian}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                success = self.model.delete_hsp(kode)
                if success:
                    QMessageBox.information(self, "Sukses", "Data HSP berhasil dihapus.")
                    self.load_data()
                else:
                    QMessageBox.warning(self, "Gagal", "Data tidak ditemukan atau gagal dihapus.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal menghapus data: {str(e)}")