# views/tab_smkk.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QTextEdit, QFileDialog, QAbstractItemView
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt

from database.db_manager import DBManager
from config.theme import (
    make_heading, apply_property, PU_BLUE, PU_GOLD, PU_LIGHT_BLUE, PU_DARK_BLUE
)
from config.settings import RISIKO_KECIL, RISIKO_SEDANG, RISIKO_BESAR, DEFAULT_PPN, SE_NOMOR
from config.constants import SMKK_KOMPONEN, RASIO_PETUGAS_K3
from utils.helpers import format_rp
from config.theme import (
    make_heading, apply_property, get_global_stylesheet,
    PU_BLUE, PU_GOLD, PU_LIGHT_BLUE, PU_DARK_BLUE
)

from PyQt5.QtWidgets import QComboBox  # sudah ada, cek
from utils.helpers import format_rp  # sudah ada

class TabSMKK(QWidget):
    """Kalkulator Biaya Penerapan SMKK — Lampiran III SE 47/2026."""

    def __init__(self):
        super().__init__()
        self.db = DBManager()
        self.init_ui()
        self.setStyleSheet(get_global_stylesheet())
        self.load_proyek_list()      # ← GANTI dari self._load_proyek_combo()
        self.hitung_smkk()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        layout.addWidget(make_heading("Biaya Penerapan SMKK — Lampiran III SE 47/SE/Dk/2026"))

        # === Panel Sinkronisasi Proyek ===
        grp_sync = QGroupBox("Sinkronisasi dengan Proyek RAB")
        hs = QHBoxLayout(grp_sync)
        hs.addWidget(QLabel("Proyek:"))
        self.cb_proyek = QComboBox()
        self.cb_proyek.setMinimumWidth(420)
        self.cb_proyek.currentIndexChanged.connect(self._on_proyek_smkk_changed)
        hs.addWidget(self.cb_proyek, 1)

        btn_load = QPushButton("⬇ Muat dari Proyek")
        btn_load.clicked.connect(self._muat_dari_proyek)
        hs.addWidget(btn_load)

        btn_simpan = QPushButton("💾 Simpan ke Proyek")
        apply_property(btn_simpan, "accent", "gold")
        btn_simpan.clicked.connect(self._simpan_ke_proyek)
        hs.addWidget(btn_simpan)

        layout.addWidget(grp_sync)

        # === A. Data Proyek ===
        grp_in = QGroupBox("A. Data Proyek & Tingkat Risiko")
        form = QFormLayout(grp_in)

        self.txt_nama = QLineEdit("Proyek Konstruksi")
        form.addRow("Nama Proyek:", self.txt_nama)

        self.spin_nilai = QDoubleSpinBox()
        self.spin_nilai.setMaximum(1e15)
        self.spin_nilai.setGroupSeparatorShown(True)
        self.spin_nilai.setPrefix("Rp ")
        self.spin_nilai.setDecimals(2)
        self.spin_nilai.setValue(10_000_000_000.0)
        form.addRow("Nilai Proyek (HPS/Kontrak):", self.spin_nilai)

        self.cb_risiko = QComboBox()
        self.cb_risiko.addItems([RISIKO_KECIL, RISIKO_SEDANG, RISIKO_BESAR])
        self.cb_risiko.setCurrentText(RISIKO_SEDANG)
        form.addRow("Tingkat Risiko Keselamatan Konstruksi:", self.cb_risiko)

        self.spin_pekerja = QSpinBox()
        self.spin_pekerja.setRange(0, 100000)
        self.spin_pekerja.setValue(50)
        form.addRow("Jumlah Tenaga Kerja (orang):", self.spin_pekerja)

        self.spin_ppn = QDoubleSpinBox()
        self.spin_ppn.setRange(0.0, 25.0)
        self.spin_ppn.setValue(DEFAULT_PPN)
        self.spin_ppn.setSuffix(" %")
        self.spin_ppn.setDecimals(2)
        form.addRow("PPN:", self.spin_ppn)

        btn_hitung = QPushButton("Hitung Biaya SMKK")
        apply_property(btn_hitung, "accent", "gold")
        btn_hitung.clicked.connect(self.hitung_smkk)
        form.addRow(btn_hitung)

        layout.addWidget(grp_in)

        # === B. Personel ===
        grp_pers = QGroupBox("B. Kebutuhan Personel Keselamatan Konstruksi")
        vp = QVBoxLayout(grp_pers)
        self.txt_personel = QTextEdit()
        self.txt_personel.setReadOnly(True)
        self.txt_personel.setMaximumHeight(130)
        self.txt_personel.setFont(QFont("Consolas", 9))
        self.txt_personel.setStyleSheet(
            f"background-color: {PU_LIGHT_BLUE}; border: 1px solid {PU_BLUE};"
        )
        vp.addWidget(self.txt_personel)
        layout.addWidget(grp_pers)

        # === C. Tabel 9 komponen ===
        grp_komp = QGroupBox("C. Tabel Komponen Biaya SMKK (A s.d I) — Lampiran III")
        vk = QVBoxLayout(grp_komp)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Kode", "Komponen Biaya SMKK", "Satuan",
            "Koefisien", "Biaya (Rp)", "Bukti Dukung"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        self.table.setAlternatingRowColors(True)
        self.table.itemChanged.connect(self._on_koef_changed)
        vk.addWidget(self.table)

        btn_row = QHBoxLayout()
        btn_reset = QPushButton("Reset Koefisien Default")
        btn_reset.clicked.connect(self._isi_komponen_default)
        btn_export = QPushButton("Ekspor SMKK ke .txt")
        apply_property(btn_export, "accent", "gold")
        btn_export.clicked.connect(self.export_smkk)
        btn_row.addWidget(btn_reset)
        btn_row.addStretch()
        btn_row.addWidget(btn_export)
        vk.addLayout(btn_row)

        layout.addWidget(grp_komp, 1)

        # === D. Rekap ===
        grp_rekap = QGroupBox("D. Rekapitulasi")
        fr = QFormLayout(grp_rekap)
        self.lbl_subtotal = QLabel("Rp 0,00")
        apply_property(self.lbl_subtotal, "amount", True)
        self.lbl_ppn = QLabel("Rp 0,00")
        apply_property(self.lbl_ppn, "amount", True)
        self.lbl_total = QLabel("Rp 0,00")
        apply_property(self.lbl_total, "grandtotal", True)

        fr.addRow("Subtotal SMKK (A - I):", self.lbl_subtotal)
        fr.addRow("PPN:", self.lbl_ppn)
        fr.addRow("TOTAL BIAYA SMKK:", self.lbl_total)
        layout.addWidget(grp_rekap)

        self._isi_komponen_default()

    # ==========================================================
    def _isi_komponen_default(self):
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        for k in SMKK_KOMPONEN:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(k["kode"]))
            self.table.setItem(r, 1, QTableWidgetItem(k["nama"]))
            self.table.setItem(r, 2, QTableWidgetItem("Ls"))
            koef_item = QTableWidgetItem(f"{self.KOEF_DEFAULT.get(k['kode'], 0.0015):.6f}")
            koef_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(r, 3, koef_item)
            self.table.setItem(r, 4, QTableWidgetItem("0.00"))
            self.table.setItem(r, 5, QTableWidgetItem(""))
        self.table.blockSignals(False)
        self.hitung_smkk()

    KOEF_DEFAULT = {
        "A": 0.0015, "B": 0.0030, "C": 0.0030, "D": 0.0010,
        "E": 0.0015, "F": 0.0020, "G": 0.0015, "H": 0.0010, "I": 0.0015,
    }

    def _on_koef_changed(self, item):
        if item.column() == 3:
            self.hitung_smkk()

    # ==========================================================
    # SINKRONISASI PROYEK
    # ==========================================================
    def load_proyek_list(self):
        """
        Public method — dipanggil main_window.on_tab_changed saat tab diaktifkan.
        Reload daftar proyek dari DB, preserve pilihan saat ini.
        """
        from models.rab_model import RABModel
        rm = RABModel()
        try:
            rows = rm.get_proyek_list()
        except Exception:
            rows = []

        # Simpan pilihan saat ini
        current_pid = self.cb_proyek.currentData()

        self.cb_proyek.blockSignals(True)
        self.cb_proyek.clear()
        self.cb_proyek.addItem("-- Tidak terkait proyek --", None)
        for p in rows:
            self.cb_proyek.addItem(
                f"{p['nama_proyek']} — {p['lokasi']} ({p['tahun_anggaran']})",
                p["id"],
            )

        # Restore pilihan kalau masih ada
        if current_pid is not None:
            idx = self.cb_proyek.findData(current_pid)
            if idx >= 0:
                self.cb_proyek.setCurrentIndex(idx)

        self.cb_proyek.blockSignals(False)

    # Alias untuk backward compat
    def _load_proyek_combo(self):
        self.load_proyek_list()

    def _on_proyek_smkk_changed(self):
        pid = self.cb_proyek.currentData()
        if pid:
            self._muat_dari_proyek()

    def _muat_dari_proyek(self):
        pid = self.cb_proyek.currentData()
        if not pid:
            QMessageBox.information(
                self, "Info",
                "Pilih proyek terlebih dahulu di combo atas."
            )
            return

        from models.rab_model import RABModel
        from models.smkk_model import SMKKModel

        rm = RABModel()
        sm = SMKKModel()

        proyek = rm.get_proyek_by_id(pid)
        if not proyek:
            return

        # Isi data proyek
        self.txt_nama.setText(proyek.get("nama_proyek", ""))

        nilai_kontrak = float(proyek.get("nilai_kontrak") or 0)
        if nilai_kontrak > 0:
            self.spin_nilai.setValue(nilai_kontrak)
        else:
            # Fallback: hitung subtotal AHSP dari item
            items = rm.get_item_rab(pid) or []
            subtotal = sum(
                float(it.get("volume", 0)) *
                float(it.get("harga_dasar", 0)) *
                (1 + float(it.get("overhead_pct", 10)) / 100.0)
                for it in items
            )
            if subtotal > 0:
                self.spin_nilai.setValue(subtotal)
                QMessageBox.information(
                    self, "Info",
                    f"Proyek belum punya nilai kontrak.\n"
                    f"Diisi dari subtotal AHSP item: {format_rp(subtotal)}\n\n"
                    f"Ubah manual jika perlu."
                )

        # Cek apakah sudah ada SMKK tersimpan
        saved = sm.get_by_proyek(pid)
        if saved:
            # Restore risiko & pekerja
            idx = self.cb_risiko.findText(saved["risiko"])
            if idx >= 0:
                self.cb_risiko.setCurrentIndex(idx)
            self.spin_pekerja.setValue(int(saved["jumlah_pekerja"] or 0))

            # Restore koefisien kustom dari detail
            komp = saved.get("komponen", [])
            if komp:
                self.table.blockSignals(True)
                for r in range(self.table.rowCount()):
                    kode = self.table.item(r, 0).text() if self.table.item(r, 0) else ""
                    for k in komp:
                        if k.get("kode") == kode:
                            self.table.setItem(
                                r, 3,
                                QTableWidgetItem(f"{float(k.get('koefisien', 0)):.6f}")
                            )
                            break
                self.table.blockSignals(False)

        self.hitung_smkk()
        QMessageBox.information(
            self, "Sukses",
            f"Data dimuat dari proyek:\n{proyek.get('nama_proyek')}"
        )

    def _simpan_ke_proyek(self):
        pid = self.cb_proyek.currentData()
        if not pid:
            QMessageBox.warning(
                self, "Peringatan",
                "Pilih proyek di combo atas terlebih dahulu."
            )
            return

        # Pastikan sudah dihitung
        self.hitung_smkk()

        # Kumpulkan komponen
        komponen = []
        for r in range(self.table.rowCount()):
            try:
                kode = self.table.item(r, 0).text()
                nama = self.table.item(r, 1).text()
                satuan = self.table.item(r, 2).text()

                # Koefisien: "0.001500" → 0.0015
                koef_str = (self.table.item(r, 3).text() or "0").replace(",", ".")
                koef = float(koef_str)

                # Biaya: "560,340.00" → 560340.00
                # FIX: HANYA hapus pemisah ribuan (,), PERTAHANKAN titik desimal
                biaya_str = (self.table.item(r, 4).text() or "0").replace(",", "")
                biaya = float(biaya_str) if biaya_str else 0.0
            except (ValueError, AttributeError):
                continue

            komponen.append({
                "kode": kode, "nama": nama, "satuan": satuan,
                "koefisien": koef, "biaya": biaya,
            })

        # Hitung ulang rekap (jangan andalkan label)
        subtotal = sum(k["biaya"] for k in komponen)
        ppn_pct = self.spin_ppn.value() / 100.0
        ppn = subtotal * ppn_pct
        total = subtotal + ppn

        # Sanity check — proteksi kalau angka > 1 triliun (curiga bug)
        if total > 1e12:
            QMessageBox.warning(
                self, "Angka Tidak Wajar",
                f"Total SMKK = Rp {total:,.0f} — terlalu besar.\n"
                f"Cek nilai proyek / koefisien sebelum menyimpan."
            )
            return

        from models.smkk_model import SMKKModel
        sm = SMKKModel()

        try:
            sm.save_to_proyek(
                proyek_id=pid,
                nama_proyek=self.txt_nama.text(),
                nilai_proyek=self.spin_nilai.value(),
                risiko=self.cb_risiko.currentText(),
                jumlah_pekerja=self.spin_pekerja.value(),
                komponen=komponen,
                subtotal=subtotal,
                ppn=ppn,
                total=total,
            )

            # Update nilai kontrak di proyek_rab juga
            from models.rab_model import RABModel
            rm = RABModel()
            rm.update_nilai_kontrak(pid, self.spin_nilai.value())

            QMessageBox.information(
                self, "Sukses",
                f"SMKK disimpan ke proyek.\n\n"
                f"Subtotal : {format_rp(subtotal)}\n"
                f"PPN      : {format_rp(ppn)}\n"
                f"Total    : {format_rp(total)}\n\n"
                f"Nilai kontrak proyek juga diperbarui."
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Gagal menyimpan: {e}")

    # ==========================================================
    def _hitung_personel(self, pekerja, risiko):
        hasil = []
        if risiko == RISIKO_KECIL:
            jml = max(1, -(-pekerja // RASIO_PETUGAS_K3["Kecil"]))
            hasil.append({"peran": "Petugas K3 Konstruksi", "jumlah": jml,
                          "keterangan": f"1 per {RASIO_PETUGAS_K3['Kecil']} pekerja"})
        elif risiko == RISIKO_SEDANG:
            hasil.append({"peran": "Ahli K3 Konstruksi Muda",
                          "jumlah": 1, "keterangan": "Pimpinan UKK"})
            jml = max(1, -(-pekerja // RASIO_PETUGAS_K3["Sedang"]))
            hasil.append({"peran": "Petugas K3 Konstruksi", "jumlah": jml,
                          "keterangan": f"1 per {RASIO_PETUGAS_K3['Sedang']} pekerja"})
        else:
            hasil.append({"peran": "Ahli K3 Konstruksi Utama/Madya",
                          "jumlah": 1, "keterangan": "Pimpinan UKK (pengalaman ≥ 3 tahun)"})
            jml = max(1, -(-pekerja // RASIO_PETUGAS_K3["Besar"]))
            hasil.append({"peran": "Petugas K3 Konstruksi", "jumlah": jml,
                          "keterangan": f"1 per {RASIO_PETUGAS_K3['Besar']} pekerja"})
            if pekerja > 100:
                hasil.append({"peran": "Ahli K3 Konstruksi Madya",
                              "jumlah": 1,
                              "keterangan": "Tambahan untuk > 100 pekerja"})
        return hasil

    # ==========================================================
    def hitung_smkk(self):
        nilai = self.spin_nilai.value()
        risiko = self.cb_risiko.currentText()
        pekerja = self.spin_pekerja.value()

        if nilai <= 0:
            return

        personel = self._hitung_personel(pekerja, risiko)
        lines = [
            f"Tingkat Risiko : {risiko}",
            f"Jumlah Pekerja : {pekerja} orang",
            "-" * 60,
        ]
        for p in personel:
            lines.append(f"  • {p['peran']}: {p['jumlah']} orang  ({p['keterangan']})")
        self.txt_personel.setPlainText("\n".join(lines))

        subtotal = 0.0
        self.table.blockSignals(True)
        for r in range(self.table.rowCount()):
            try:
                koef = float((self.table.item(r, 3).text() or "0").replace(",", "."))
            except (ValueError, AttributeError):
                koef = 0.0
            biaya = nilai * koef
            biaya_item = QTableWidgetItem(f"{biaya:,.2f}")
            biaya_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            biaya_item.setForeground(QColor(PU_BLUE))
            self.table.setItem(r, 4, biaya_item)
            subtotal += biaya
        self.table.blockSignals(False)

        ppn_pct = self.spin_ppn.value() / 100.0
        ppn = subtotal * ppn_pct
        total = subtotal + ppn

        self.lbl_subtotal.setText(format_rp(subtotal))
        self.lbl_ppn.setText(format_rp(ppn))
        self.lbl_total.setText(format_rp(total))

    # ==========================================================
    def export_smkk(self):
        default = f"SMKK_{self.txt_nama.text().replace(' ', '_')}.txt"
        path, _ = QFileDialog.getSaveFileName(self, "Simpan SMKK", default, "Text (*.txt)")
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("=" * 78 + "\n")
                fh.write(f"BIAYA PENERAPAN SMKK (Lampiran III SE {SE_NOMOR})\n")
                fh.write("=" * 78 + "\n\n")
                fh.write(f"Nama Proyek    : {self.txt_nama.text()}\n")
                fh.write(f"Nilai Proyek   : {format_rp(self.spin_nilai.value())}\n")
                fh.write(f"Tingkat Risiko : {self.cb_risiko.currentText()}\n")
                fh.write(f"Jumlah Pekerja : {self.spin_pekerja.value()} orang\n\n")
                fh.write("B. KEBUTUHAN PERSONEL\n")
                fh.write(self.txt_personel.toPlainText() + "\n\n")
                fh.write("C. TABEL KOMPONEN BIAYA SMKK\n")
                fh.write("-" * 78 + "\n")
                for r in range(self.table.rowCount()):
                    fh.write(
                        f"{self.table.item(r,0).text():>3} | "
                        f"{self.table.item(r,1).text():<45} | "
                        f"{self.table.item(r,3).text():>10} | "
                        f"Rp {self.table.item(r,4).text()}\n"
                    )
                fh.write("-" * 78 + "\n")
                fh.write(f"Subtotal : {self.lbl_subtotal.text()}\n")
                fh.write(f"PPN      : {self.lbl_ppn.text()}\n")
                fh.write(f"TOTAL    : {self.lbl_total.text()}\n")
            QMessageBox.information(self, "Sukses", f"SMKK disimpan ke:\n{path}")
        except Exception as ex:
            QMessageBox.critical(self, "Error", str(ex))