# views/dialogs/rab_dialogs.py
"""
Dialog-dialog CRUD untuk Tab RAB:
  • ProyekDialog        — tambah/edit proyek
  • ItemAHSPDialog      — tambah item dari template AHSP
  • ItemManualDialog    — tambah/edit item manual
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QDialogButtonBox,
    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QLabel, QMessageBox,
    QPlainTextEdit
)
from PyQt5.QtCore import Qt

from utils.helpers import format_rp
from config.theme import get_global_stylesheet, apply_property


# ==========================================================
# DIALOG PROYEK
# ==========================================================
class ProyekDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.data = data
        self.setWindowTitle("Tambah Proyek Baru" if data is None else "Edit Proyek")
        self.setMinimumWidth(520)
        self.setStyleSheet(get_global_stylesheet())
        self._init_ui()
        if data:
            self._populate(data)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.inp_nama = QLineEdit()
        self.inp_lokasi = QLineEdit()
        self.inp_instansi = QLineEdit("Dinas Pekerjaan Umum")
        self.inp_tahun = QSpinBox()
        self.inp_tahun.setRange(2020, 2100)
        self.inp_tahun.setValue(2026)
        self.inp_overhead = QDoubleSpinBox()
        self.inp_overhead.setRange(0.0, 15.0)
        self.inp_overhead.setValue(10.0)
        self.inp_overhead.setSuffix(" %")
        self.inp_ppn = QDoubleSpinBox()
        self.inp_ppn.setRange(0.0, 25.0)
        self.inp_ppn.setValue(11.0)
        self.inp_ppn.setSuffix(" %")

        form.addRow("Nama Proyek*:", self.inp_nama)
        form.addRow("Lokasi*:", self.inp_lokasi)
        form.addRow("Instansi:", self.inp_instansi)
        form.addRow("Tahun Anggaran:", self.inp_tahun)
        form.addRow("Overhead Default:", self.inp_overhead)
        form.addRow("PPN Default:", self.inp_ppn)

        layout.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self._on_ok)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _populate(self, d):
        self.inp_nama.setText(str(d.get("nama_proyek", "")))
        self.inp_lokasi.setText(str(d.get("lokasi", "")))
        self.inp_instansi.setText(str(d.get("instansi", "")))
        self.inp_tahun.setValue(int(d.get("tahun_anggaran", 2026)))
        self.inp_overhead.setValue(float(d.get("overhead_pct", 10.0)))
        self.inp_ppn.setValue(float(d.get("ppn_pct", 11.0)))

    def _on_ok(self):
        if not self.inp_nama.text().strip():
            QMessageBox.warning(self, "Validasi", "Nama proyek wajib diisi!")
            return
        if not self.inp_lokasi.text().strip():
            QMessageBox.warning(self, "Validasi", "Lokasi wajib diisi!")
            return
        self.accept()

    def get_data(self):
        return {
            "nama_proyek": self.inp_nama.text().strip(),
            "lokasi": self.inp_lokasi.text().strip(),
            "instansi": self.inp_instansi.text().strip(),
            "tahun_anggaran": self.inp_tahun.value(),
            "overhead_pct": self.inp_overhead.value(),
            "ppn_pct": self.inp_ppn.value(),
        }


# ==========================================================
# DIALOG ITEM DARI TEMPLATE AHSP
# ==========================================================
class ItemAHSPDialog(QDialog):
    def __init__(self, parent, rab_model, templates):
        super().__init__(parent)
        self.rab_model = rab_model
        self.templates = templates
        self.setWindowTitle("Tambah Item dari Template AHSP")
        self.setMinimumWidth(620)
        self.setStyleSheet(get_global_stylesheet())
        self._init_ui()
        self._refresh_harga()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        # Filter bidang
        self.cb_bidang = QComboBox()
        self.cb_bidang.addItem("-- Semua Bidang --", None)
        for b in sorted({t["bidang"] for t in self.templates}):
            self.cb_bidang.addItem(b, b)
        self.cb_bidang.currentIndexChanged.connect(self._refresh_templates)
        form.addRow("Filter Bidang:", self.cb_bidang)

        # Combo template
        self.cb_template = QComboBox()
        self.cb_template.setMinimumWidth(540)
        self.cb_template.currentIndexChanged.connect(self._refresh_harga)
        form.addRow("Template AHSP*:", self.cb_template)

        # Divisi
        self.inp_divisi = QLineEdit("DIVISI 1 - UMUM")
        form.addRow("Divisi:", self.inp_divisi)

        # Volume
        self.inp_volume = QDoubleSpinBox()
        self.inp_volume.setRange(0.0, 1e9)
        self.inp_volume.setDecimals(4)
        self.inp_volume.setValue(1.0)
        form.addRow("Volume*:", self.inp_volume)

        # Overhead
        self.inp_overhead = QDoubleSpinBox()
        self.inp_overhead.setRange(0.0, 15.0)
        self.inp_overhead.setValue(10.0)
        self.inp_overhead.setSuffix(" %")
        self.inp_overhead.valueChanged.connect(self._refresh_harga)
        form.addRow("Overhead & Profit:", self.inp_overhead)

        # Preview
        self.lbl_preview = QLabel("—")
        apply_property(self.lbl_preview, "amount", True)
        form.addRow("Preview D → F:", self.lbl_preview)

        layout.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

        self._refresh_templates()

    def _refresh_templates(self):
        bidang = self.cb_bidang.currentData()
        self.cb_template.blockSignals(True)
        self.cb_template.clear()
        self.cb_template.addItem("-- Pilih Template --", None)

        for t in self.templates:
            if bidang and t["bidang"] != bidang:
                continue
            label = f"[{t['bidang']}] {t['kode_pekerjaan']} — {t['nama_pekerjaan']}"
            self.cb_template.addItem(label, t["id"])
        self.cb_template.blockSignals(False)
        self._refresh_harga()

    def _refresh_harga(self):
        tid = self.cb_template.currentData()
        if tid is None:
            self.lbl_preview.setText("—")
            return
        try:
            d, f = self.rab_model.hitung_dan_f_dari_template(
                tid, self.inp_overhead.value()
            )
            self.lbl_preview.setText(
                f"D = {format_rp(d)}   →   F = {format_rp(f)}"
            )
        except Exception as e:
            self.lbl_preview.setText(f"Error: {e}")

    def get_data(self):
        tid = self.cb_template.currentData()
        return {
            "template_id": tid,
            "divisi": self.inp_divisi.text().strip(),
            "volume": self.inp_volume.value(),
            "overhead_pct": self.inp_overhead.value(),
        }


# ==========================================================
# DIALOG ITEM MANUAL
# ==========================================================
class ItemManualDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.data = data
        self.setWindowTitle("Tambah Item Manual" if data is None else "Edit Item")
        self.setMinimumWidth(520)
        self.setStyleSheet(get_global_stylesheet())
        self._init_ui()
        if data:
            self._populate(data)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.inp_divisi = QLineEdit("DIVISI 1 - UMUM")
        self.inp_kode = QLineEdit("X.01")
        self.inp_uraian = QLineEdit()
        self.inp_satuan = QLineEdit("m3")

        self.inp_volume = QDoubleSpinBox()
        self.inp_volume.setRange(0.0, 1e9)
        self.inp_volume.setDecimals(4)
        self.inp_volume.setValue(1.0)

        self.inp_harga = QDoubleSpinBox()
        self.inp_harga.setRange(0.0, 1e15)
        self.inp_harga.setDecimals(2)
        self.inp_harga.setGroupSeparatorShown(True)
        self.inp_harga.setPrefix("Rp ")
        self.inp_harga.valueChanged.connect(self._refresh_preview)

        self.inp_overhead = QDoubleSpinBox()
        self.inp_overhead.setRange(0.0, 15.0)
        self.inp_overhead.setValue(10.0)
        self.inp_overhead.setSuffix(" %")
        self.inp_overhead.valueChanged.connect(self._refresh_preview)

        self.lbl_preview = QLabel("—")
        apply_property(self.lbl_preview, "amount", True)

        form.addRow("Divisi:", self.inp_divisi)
        form.addRow("Kode Item:", self.inp_kode)
        form.addRow("Uraian*:", self.inp_uraian)
        form.addRow("Satuan*:", self.inp_satuan)
        form.addRow("Volume*:", self.inp_volume)
        form.addRow("Harga Dasar (D):", self.inp_harga)
        form.addRow("Overhead & Profit:", self.inp_overhead)
        form.addRow("Preview F = D × (1 + oh%):", self.lbl_preview)

        layout.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self._on_ok)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

        self._refresh_preview()

    def _refresh_preview(self):
        d = self.inp_harga.value()
        f = d * (1 + self.inp_overhead.value() / 100.0)
        self.lbl_preview.setText(f"F = {format_rp(f)}")

    def _populate(self, d):
        self.inp_divisi.setText(str(d.get("divisi", "")))
        self.inp_kode.setText(str(d.get("kode_item", "")))
        self.inp_uraian.setText(str(d.get("uraian_pekerjaan", "")))
        self.inp_satuan.setText(str(d.get("satuan", "")))
        self.inp_volume.setValue(float(d.get("volume", 1.0)))
        self.inp_harga.setValue(float(d.get("harga_dasar", 0.0)))
        self.inp_overhead.setValue(float(d.get("overhead_pct", 10.0)))

    def _on_ok(self):
        if not self.inp_uraian.text().strip():
            QMessageBox.warning(self, "Validasi", "Uraian wajib diisi!")
            return
        if not self.inp_satuan.text().strip():
            QMessageBox.warning(self, "Validasi", "Satuan wajib diisi!")
            return
        self.accept()

    def get_data(self):
        return {
            "divisi": self.inp_divisi.text().strip(),
            "kode_item": self.inp_kode.text().strip(),
            "uraian_pekerjaan": self.inp_uraian.text().strip(),
            "satuan": self.inp_satuan.text().strip(),
            "volume": self.inp_volume.value(),
            "harga_dasar": self.inp_harga.value(),
            "overhead_pct": self.inp_overhead.value(),
        }