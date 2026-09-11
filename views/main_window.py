# views/main_window.py
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout
from PyQt5.QtGui import QIcon
from config.theme import get_global_stylesheet, PU_BLUE, PU_GOLD

from views.tab_laporan_hsp import TabLaporanHSP
from views.tab_hsp import TabHSP
from views.tab_acuan import TabAcuan
from views.tab_smkk import TabSMKK
from views.tab_ahsp import TabAHSP
from views.tab_usulan import TabUsulan
from views.tab_rab_export import TabRABExport


class AHSPMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aplikasi AHSP Sektor Konstruksi — SE 47/SE/Dk/2026")
        self.resize(1360, 860)
        self.setStyleSheet(get_global_stylesheet())
        self.proyek_aktif = None
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(8, 8, 8, 8)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # === Buat tab sekali, simpan referensinya ===
        self.tab_laporan = TabLaporanHSP()
        self.tab_hsp = TabHSP()
        self.tab_acuan = TabAcuan()
        self.tab_smkk = TabSMKK()
        self.tab_ahsp = TabAHSP()
        self.tab_usulan = TabUsulan()
        self.tab_rab = TabRABExport()

        self.tabs.addTab(self.tab_laporan, "  Laporan HSP Balai  ")
        self.tabs.addTab(self.tab_hsp, "  Lampiran I: Data HSP  ")
        self.tabs.addTab(self.tab_acuan, "  Lampiran II: Tabel Acuan  ")
        self.tabs.addTab(self.tab_smkk, "  Lampiran III: Biaya SMKK  ")
        self.tabs.addTab(self.tab_ahsp, "  Lampiran IV-VI: Kalkulator AHSP  ")
        self.tabs.addTab(self.tab_usulan, "  Lampiran VII: Pengajuan Usulan  ")
        self.tabs.addTab(self.tab_rab, "  Rekapitulasi & Ekspor RAB  ")

        self.tabs.currentChanged.connect(self.on_tab_changed)
        # Sync proyek aktif antara RAB dan SMKK
        if hasattr(self.tab_rab, "combo_proyek"):
            self.tab_rab.combo_proyek.currentIndexChanged.connect(self._sync_proyek)

    def _sync_proyek(self):
        pid = self.tab_rab.combo_proyek.currentData() if hasattr(self.tab_rab, "combo_proyek") else None
        self.proyek_aktif = pid

    def on_tab_changed(self, index):
        w = self.tabs.widget(index)
        if not w:
            return

        # Tab kalkulator AHSP: refresh template
        if hasattr(w, 'cb_template') and hasattr(w, 'load_templates_to_combo'):
            w.cb_template.blockSignals(True)
            cur_id = w.cb_template.currentData()
            w.cb_template.clear()
            w.cb_template.addItem("-- Pilih Analisis Pekerjaan --", None)
            w.load_templates_to_combo()
            idx = w.cb_template.findData(cur_id)
            if idx >= 0:
                w.cb_template.setCurrentIndex(idx)
            w.cb_template.blockSignals(False)
            if hasattr(w, 'load_template_details'):
                w.load_template_details()
            return

        # Tab SMKK: refresh combo proyek dari DB
        if hasattr(w, 'load_proyek_list'):
            w.load_proyek_list()
            if hasattr(w, 'hitung_smkk'):
                w.hitung_smkk()
            return

        # Tab RAB: refresh daftar proyek + reload data
        if hasattr(w, 'load_rab_data'):
            # Kalau ada method khusus refresh combo di RAB, panggil
            if hasattr(w, '_refresh_proyek_combo_only'):
                w._refresh_proyek_combo_only()
            w.load_rab_data()
            return

        # Fallback
        if hasattr(w, 'load_data'):
            w.load_data()