# views/tab_rab_export.py
"""
Tab Rekapitulasi & Ekspor RAB / HPS — SE 47/SE/Dk/2026.

Fitur:
  • Pilih / Tambah / Edit / Hapus Proyek
  • Tambah Item dari Template AHSP (SDA/BM/CK)
  • Tambah Item Manual
  • Edit / Hapus Item
  • Ekspor Excel 3 blok (AHSP + SMKK + Rekap PPN)

BUG FIX (v2):
  • SMKK dihitung: biaya = subtotal_ahsp × koefisien
  • item_id disimpan di UserRole kolom 0 (untuk hapus)
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QComboBox, QFileDialog, QMessageBox,
    QGroupBox, QSpinBox, QAbstractItemView
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

from models.rab_model import RABModel
from models.smkk_model import SMKKModel
from utils.exporter import Exporter
from utils.helpers import format_rp
from config.theme import (
    make_heading, apply_property, PU_BLUE, PU_LIGHT_BLUE, PU_DARK_BLUE
)

from views.dialogs.rab_dialogs import (
    ProyekDialog, ItemAHSPDialog, ItemManualDialog
)


class TabRABExport(QWidget):
    def __init__(self):
        super().__init__()
        self.rab_model = RABModel()
        self.smkk_model = SMKKModel()
        self.current_proyek_id = None
        self.subtotal_ahsp = 0.0
        self.subtotal_smkk = 0.0
        self.komponen_smkk = []
        self.init_ui()
        self.load_proyek_list()

    # ==========================================================
    # UI
    # ==========================================================
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Header
        layout.addWidget(make_heading(
            "Rekapitulasi & Ekspor RAB / HPS — SE 47/SE/Dk/2026"
        ))
        sub = QLabel(
            "Ekspor menghasilkan 3 blok: (A) AHSP per item, "
            "(B) Biaya SMKK 9 komponen, (C) Rekap + PPN"
        )
        apply_property(sub, "subheading", True)
        layout.addWidget(sub)

        # === Pemilihan Proyek ===
        grp = QGroupBox("Manajemen Proyek & Item RAB")
        v = QVBoxLayout(grp)

        # Baris 1: proyek + PPN
        h1 = QHBoxLayout()
        h1.addWidget(QLabel("Proyek:"))
        self.combo_proyek = QComboBox()
        self.combo_proyek.setMinimumWidth(440)
        self.combo_proyek.currentIndexChanged.connect(self.on_proyek_changed)
        h1.addWidget(self.combo_proyek, 1)

        h1.addWidget(QLabel("PPN:"))
        self.spin_ppn = QSpinBox()
        self.spin_ppn.setRange(0, 25)
        self.spin_ppn.setValue(11)
        self.spin_ppn.setSuffix(" %")
        self.spin_ppn.valueChanged.connect(self._refresh_summary)
        h1.addWidget(self.spin_ppn)

        btn_new_proyek = QPushButton("+ Proyek Baru")
        btn_new_proyek.clicked.connect(self.on_new_proyek)
        h1.addWidget(btn_new_proyek)

        btn_edit_proyek = QPushButton("Edit")
        btn_edit_proyek.clicked.connect(self.on_edit_proyek)
        h1.addWidget(btn_edit_proyek)

        btn_del_proyek = QPushButton("Hapus")
        apply_property(btn_del_proyek, "accent", "danger")
        btn_del_proyek.clicked.connect(self.on_delete_proyek)
        h1.addWidget(btn_del_proyek)
        btn_kirim_smkk = QPushButton("⬆ Kirim ke Tab SMKK")
        btn_kirim_smkk.clicked.connect(self.on_kirim_ke_smkk)
        h1.addWidget(btn_kirim_smkk)

        v.addLayout(h1)

        # Baris 2: item actions + export
        h2 = QHBoxLayout()
        btn_add_ahsp = QPushButton("+ Item dari Template AHSP")
        apply_property(btn_add_ahsp, "accent", "success")
        btn_add_ahsp.clicked.connect(self.on_add_item_from_ahsp)
        h2.addWidget(btn_add_ahsp)

        btn_add_manual = QPushButton("+ Item Manual")
        btn_add_manual.clicked.connect(self.on_add_item_manual)
        h2.addWidget(btn_add_manual)

        btn_edit_item = QPushButton("Edit Item")
        btn_edit_item.clicked.connect(self.on_edit_item)
        h2.addWidget(btn_edit_item)

        btn_del_item = QPushButton("- Hapus Item")
        apply_property(btn_del_item, "accent", "danger")
        btn_del_item.clicked.connect(self.on_delete_item)
        h2.addWidget(btn_del_item)

        h2.addStretch()

        btn_export = QPushButton("Ekspor RAB/HPS ke Excel (.xlsx)")
        apply_property(btn_export, "accent", "gold")
        btn_export.clicked.connect(self.export_excel)
        h2.addWidget(btn_export)

        v.addLayout(h2)
        layout.addWidget(grp)

        # === Info Ringkas ===
        self.lbl_info = QLabel(
            "AHSP: Rp 0,00  |  SMKK: Rp 0,00  |  PPN: Rp 0,00  |  Grand Total: Rp 0,00"
        )
        self.lbl_info.setStyleSheet(
            f"font-size: 11pt; font-weight: bold; color: {PU_DARK_BLUE}; "
            f"background-color: {PU_LIGHT_BLUE}; padding: 8px; border-radius: 4px;"
        )
        layout.addWidget(self.lbl_info)

        # === Tabel RAB ===
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            "Divisi", "Kode Item", "Uraian Pekerjaan", "Satuan",
            "Volume", "Harga Dasar (D)", "Overhead %", "Harga Satuan (F)"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.doubleClicked.connect(self.on_edit_item)
        layout.addWidget(self.table, 1)

    # ==========================================================
    # PROYEK
    # ==========================================================
    def load_proyek_list(self):
        rows = self.rab_model.get_proyek_list()
        self.combo_proyek.blockSignals(True)
        self.combo_proyek.clear()
        for p in rows:
            self.combo_proyek.addItem(
                f"{p['nama_proyek']} — {p['lokasi']} ({p['tahun_anggaran']})",
                p["id"],
            )
        self.combo_proyek.blockSignals(False)
        if rows:
            self.current_proyek_id = rows[0]["id"]
            self.load_rab_data()
        else:
            self.current_proyek_id = None
            self.table.setRowCount(0)
            self.subtotal_ahsp = 0.0
            self.subtotal_smkk = 0.0
            self._refresh_summary()

    def on_proyek_changed(self):
        self.current_proyek_id = self.combo_proyek.currentData()
        if self.current_proyek_id:
            self.load_rab_data()

    def on_new_proyek(self):
        dlg = ProyekDialog(self)
        if dlg.exec_() != ProyekDialog.Accepted:
            return
        try:
            new_id = self.rab_model.create_proyek(**dlg.get_data())
            QMessageBox.information(self, "Sukses", f"Proyek baru dibuat (ID: {new_id})")
            self.load_proyek_list()
            idx = self.combo_proyek.findData(new_id)
            if idx >= 0:
                self.combo_proyek.setCurrentIndex(idx)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal membuat proyek: {e}")

    def on_edit_proyek(self):
        if not self.current_proyek_id:
            QMessageBox.warning(self, "Peringatan", "Pilih proyek terlebih dahulu.")
            return
        data = self.rab_model.get_proyek_by_id(self.current_proyek_id)
        if not data:
            return
        dlg = ProyekDialog(self, data=data)
        if dlg.exec_() != ProyekDialog.Accepted:
            return
        try:
            ok = self.rab_model.update_proyek(self.current_proyek_id, dlg.get_data())
            if ok:
                QMessageBox.information(self, "Sukses", "Proyek diperbarui.")
                self.load_proyek_list()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal update: {e}")

    def on_delete_proyek(self):
        if not self.current_proyek_id:
            QMessageBox.warning(self, "Peringatan", "Tidak ada proyek dipilih.")
            return
        nama = self.combo_proyek.currentText()
        reply = QMessageBox.question(
            self, "Konfirmasi",
            f"Hapus proyek:\n\n{nama}\n\nSemua item ikut terhapus!",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        try:
            self.rab_model.delete_proyek(self.current_proyek_id)
            QMessageBox.information(self, "Sukses", "Proyek dihapus.")
            self.current_proyek_id = None
            self.load_proyek_list()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal hapus: {e}")

    # ==========================================================
    # ITEM RAB
    # ==========================================================
    def on_add_item_from_ahsp(self):
        if not self.current_proyek_id:
            QMessageBox.warning(self, "Peringatan", "Pilih proyek terlebih dahulu.")
            return
        templates = self.rab_model.get_ahsp_templates()
        if not templates:
            QMessageBox.warning(self, "Peringatan",
                                "Belum ada template AHSP di database.")
            return

        dlg = ItemAHSPDialog(self, self.rab_model, templates)
        if dlg.exec_() != ItemAHSPDialog.Accepted:
            return
        data = dlg.get_data()
        if data["template_id"] is None:
            QMessageBox.warning(self, "Peringatan", "Pilih template!")
            return
        try:
            item_id, d_val, f_val = self.rab_model.add_item_from_ahsp(
                proyek_id=self.current_proyek_id,
                template_id=data["template_id"],
                divisi=data["divisi"],
                volume=data["volume"],
                overhead_pct=data["overhead_pct"],
            )
            QMessageBox.information(
                self, "Sukses",
                f"Item ditambahkan:\nD = {format_rp(d_val)}\nF = {format_rp(f_val)}"
            )
            self.load_rab_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menambah: {e}")

    def on_add_item_manual(self):
        if not self.current_proyek_id:
            QMessageBox.warning(self, "Peringatan", "Pilih proyek terlebih dahulu.")
            return
        dlg = ItemManualDialog(self)
        if dlg.exec_() != ItemManualDialog.Accepted:
            return
        try:
            self.rab_model.add_item_rab(
                proyek_id=self.current_proyek_id, **dlg.get_data()
            )
            QMessageBox.information(self, "Sukses", "Item ditambahkan.")
            self.load_rab_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menambah: {e}")

    def on_edit_item(self):
        row = self.table.currentRow()
        if row < 0:
            return
        item = self.table.item(row, 0)
        if item is None:
            return
        item_id = item.data(Qt.UserRole)
        if item_id is None:
            return

        data = self.rab_model.get_item_rab_by_id(item_id)
        if not data:
            QMessageBox.warning(self, "Peringatan", "Item tidak ditemukan.")
            return

        dlg = ItemManualDialog(self, data=data)
        if dlg.exec_() != ItemManualDialog.Accepted:
            return
        try:
            self.rab_model.update_item_rab(item_id, dlg.get_data())
            self.load_rab_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal edit: {e}")

    def on_delete_item(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Peringatan", "Pilih baris yang akan dihapus.")
            return
        item = self.table.item(row, 0)
        if item is None:
            return
        item_id = item.data(Qt.UserRole)
        if item_id is None:
            return

        uraian = self.table.item(row, 2).text() if self.table.item(row, 2) else ""
        reply = QMessageBox.question(
            self, "Konfirmasi",
            f"Hapus item:\n\n{uraian}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        try:
            self.rab_model.delete_item_rab(item_id)
            self.load_rab_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal hapus: {e}")

    # ==========================================================
    # LOAD DATA
    # ==========================================================
    def load_rab_data(self):
        if not self.current_proyek_id:
            return

        items = self.rab_model.get_item_rab(self.current_proyek_id) or []

        self.table.setRowCount(0)
        self.subtotal_ahsp = 0.0

        for r, it in enumerate(items):
            vol = float(it.get("volume", 0) or 0)
            hd = float(it.get("harga_dasar", 0) or 0)
            oh = float(it.get("overhead_pct", 10) or 10)
            hsp_f = hd * (1 + oh / 100.0)
            self.subtotal_ahsp += vol * hsp_f

            self.table.insertRow(r)

            # Divisi + simpan item_id di UserRole
            div_item = QTableWidgetItem(str(it.get("divisi", "")))
            div_item.setData(Qt.UserRole, it.get("id"))
            self.table.setItem(r, 0, div_item)

            self.table.setItem(r, 1, QTableWidgetItem(str(it.get("kode_item", ""))))
            self.table.setItem(r, 2, QTableWidgetItem(str(it.get("uraian_pekerjaan", ""))))
            self.table.setItem(r, 3, QTableWidgetItem(str(it.get("satuan", ""))))

            v_item = QTableWidgetItem(f"{vol:,.2f}")
            v_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(r, 4, v_item)

            hd_item = QTableWidgetItem(format_rp(hd))
            hd_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(r, 5, hd_item)

            oh_item = QTableWidgetItem(f"{oh:.2f}")
            oh_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(r, 6, oh_item)

            f_item = QTableWidgetItem(format_rp(hsp_f))
            f_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            f_item.setForeground(QColor(PU_BLUE))
            self.table.setItem(r, 7, f_item)

        # Hitung SMKK
        self.komponen_smkk = self._get_smkk_komponen_with_biaya(self.subtotal_ahsp)
        self.subtotal_smkk = sum(k["biaya"] for k in self.komponen_smkk)

        self._refresh_summary()

    def on_kirim_ke_smkk(self):
        """Buka tab SMKK dengan proyek ini terpilih."""
        if not self.current_proyek_id:
            QMessageBox.warning(self, "Peringatan", "Pilih proyek dulu.")
            return

        mw = self.window()
        if not hasattr(mw, "tab_smkk"):
            return
        tab_smkk = mw.tab_smkk

        # PENTING: pindah ke tab SMKK DULU
        # → memicu on_tab_changed → tab_smkk.load_proyek_list()
        # → combo proyek di SMKK refresh dari DB
        if hasattr(mw, "tabs"):
            mw.tabs.setCurrentWidget(tab_smkk)

        # Baru set proyek terpilih (setelah combo refresh)
        if hasattr(tab_smkk, "cb_proyek"):
            idx = tab_smkk.cb_proyek.findData(self.current_proyek_id)
            if idx >= 0:
                tab_smkk.cb_proyek.setCurrentIndex(idx)
                # Pastikan handler terpanggil walau index sama
                if hasattr(tab_smkk, "_on_proyek_smkk_changed"):
                    tab_smkk._on_proyek_smkk_changed()

    # ==========================================================
    # SMKK & REKAP
    # ==========================================================
    def _get_smkk_komponen_with_biaya(self, subtotal_ahsp):
        """
        Cek dulu apakah proyek ini sudah punya SMKK tersimpan di DB.
        Kalau ada → pakai itu.
        Kalau tidak → hitung ulang dari subtotal_ahsp × koefisien default.
        """
        # 1. Cek SMKK tersimpan
        if self.current_proyek_id:
            saved = self.smkk_model.get_by_proyek(self.current_proyek_id)
            if saved and saved.get("komponen"):
                # Pakai komponen tersimpan, tapi update biaya proporsional
                # ke subtotal_ahsp yang baru (kalau item berubah)
                nilai_tersimpan = saved.get("nilai_proyek", 0) or 0
                if nilai_tersimpan > 0 and subtotal_ahsp > 0:
                    # Proporsional: koefisien tetap, biaya dihitung ulang dari subtotal_ahsp
                    hasil = []
                    for k in saved["komponen"]:
                        koef = float(k.get("koefisien", 0))
                        hasil.append({
                            "kode": k.get("kode", ""),
                            "nama": k.get("nama", ""),
                            "satuan": k.get("satuan", "Ls"),
                            "koefisien": koef,
                            "biaya": round(subtotal_ahsp * koef, 2),
                        })
                    return hasil

        # 2. Fallback: hitung dari default DB
        komponen_db = self.smkk_model.get_all_komponen() or []
        hasil = []
        for k in komponen_db:
            nilai_default = float(k.get("nilai_default", 0) or 0)
            nilai_kustom = k.get("nilai_kustom", None)
            koef = float(nilai_kustom) if nilai_kustom not in (None, "", "-") else nilai_default
            biaya = round(subtotal_ahsp * koef, 2)
            hasil.append({
                "kode": k.get("kode", ""),
                "nama": k.get("nama", ""),
                "satuan": k.get("satuan", "Ls"),
                "koefisien": koef,
                "biaya": biaya,
            })
        return hasil

    def _refresh_summary(self):
        ppn_pct = float(self.spin_ppn.value())
        jumlah_sebelum_ppn = self.subtotal_ahsp + self.subtotal_smkk
        ppn = jumlah_sebelum_ppn * ppn_pct / 100.0
        grand = jumlah_sebelum_ppn + ppn

        # Deteksi sumber SMKK
        sumber = "default"
        if self.current_proyek_id:
            saved = self.smkk_model.get_by_proyek(self.current_proyek_id)
            if saved:
                sumber = f"disimpan {saved.get('created_at', '')[:10]}"

        self.lbl_info.setText(
            f"AHSP: {format_rp(self.subtotal_ahsp)}  |  "
            f"SMKK: {format_rp(self.subtotal_smkk)}  ({sumber})  |  "
            f"PPN ({ppn_pct:.0f}%): {format_rp(ppn)}  |  "
            f"Grand Total: {format_rp(grand)}"
        )

    # ==========================================================
    # EKSPOR
    # ==========================================================
    def export_excel(self):
        if not self.current_proyek_id:
            QMessageBox.warning(self, "Peringatan", "Pilih proyek terlebih dahulu!")
            return

        proyek_info = self.rab_model.get_proyek_by_id(self.current_proyek_id) or {}
        item_list = self.rab_model.get_item_rab(self.current_proyek_id) or []
        proyek_info["ppn_pct"] = float(self.spin_ppn.value())

        smkk_komponen = self._get_smkk_komponen_with_biaya(self.subtotal_ahsp)

        default_name = f"RAB_{proyek_info.get('nama_proyek', 'proyek').replace(' ', '_')}.xlsx"
        path, _ = QFileDialog.getSaveFileName(
            self, "Simpan File Excel RAB", default_name, "Excel Files (*.xlsx)"
        )
        if not path:
            return

        try:
            Exporter.export_rab_to_excel(
                proyek_info, item_list, path, smkk_komponen=smkk_komponen
            )
            QMessageBox.information(
                self, "Sukses Ekspor",
                f"RAB/HPS berhasil diekspor ke:\n{path}\n\n"
                f"Termasuk 3 blok: AHSP + SMKK + Rekap PPN"
            )
        except Exception as err:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Gagal Ekspor", str(err))