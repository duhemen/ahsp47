# main.py
"""
Entry point Aplikasi AHSP SE 47/SE/Dk/2026.
"""
import os
import sys
import traceback


def _setup_high_dpi():
    """Aktifkan High-DPI scaling sebelum QApplication dibuat."""
    os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
    try:
        from PyQt5.QtCore import Qt
        from PyQt5.QtWidgets import QApplication
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    except Exception:
        pass


def _ensure_db_dir():
    """Pastikan folder DB ada (khusus frozen / pertama kali)."""
    try:
        from config.settings import DB_PATH
        db_dir = os.path.dirname(DB_PATH)
        if db_dir and not os.path.isdir(db_dir):
            os.makedirs(db_dir, exist_ok=True)
    except Exception as e:
        print(f"[WARN] tidak dapat membuat folder DB: {e}")


def main():
    _setup_high_dpi()
    _ensure_db_dir()

    from PyQt5.QtWidgets import QApplication, QMessageBox
    from PyQt5.QtGui import QIcon

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("AHSP 47/2026")

    # Icon (opsional — skip kalau file tidak ada)
    try:
        from config.settings import ASSETS_DIR
        icon_path = os.path.join(ASSETS_DIR, "assets", "icon.ico")
        if os.path.isfile(icon_path):
            app.setWindowIcon(QIcon(icon_path))
    except Exception:
        pass

    try:
        from views.main_window import AHSPMainWindow
        window = AHSPMainWindow()
        window.show()
    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        QMessageBox.critical(
            None, "Gagal Memulai Aplikasi",
            f"Terjadi error saat inisialisasi:\n\n{e}\n\nLihat console untuk detail."
        )
        sys.exit(1)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()