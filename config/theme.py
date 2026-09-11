# config/theme.py
"""
Tema UI Aplikasi AHSP 47/2026 — Warna Kementerian Pekerjaan Umum.
Palet: Biru PU + aksen Gold.
"""

# === Palet Warna Kementerian PU ===
PU_BLUE = "#004488"
PU_DARK_BLUE = "#002B5C"
PU_MID_BLUE = "#0066CC"
PU_LIGHT_BLUE = "#EAF2FA"
PU_VERY_LIGHT_BLUE = "#F5F9FD"
PU_GOLD = "#F5B301"
PU_GOLD_LIGHT = "#FFF3D6"
PU_GOLD_DARK = "#C68A00"
WHITE = "#FFFFFF"
GRAY = "#6C757D"
LIGHT_GRAY = "#F0F0F0"
BORDER_GRAY = "#CED4DA"
DANGER = "#C62828"
SUCCESS = "#2E7D32"
WARNING = "#EF6C00"


def get_global_stylesheet():
    """Stylesheet global untuk seluruh aplikasi."""
    return f"""
    QMainWindow, QDialog {{ background-color: {PU_LIGHT_BLUE}; }}
    QWidget {{ font-family: 'Segoe UI', 'Calibri', sans-serif; font-size: 10pt; }}

    /* ===== Tab Widget ===== */
    QTabWidget::pane {{
        background-color: {WHITE};
        border: 1px solid {PU_BLUE};
        top: -1px;
    }}
    QTabBar::tab {{
        background-color: {PU_LIGHT_BLUE};
        color: {PU_DARK_BLUE};
        padding: 9px 16px;
        border: 1px solid {PU_BLUE};
        border-bottom: none;
        margin-right: 2px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        font-weight: bold;
    }}
    QTabBar::tab:selected {{
        background-color: {PU_BLUE};
        color: {PU_GOLD};
    }}
    QTabBar::tab:hover:!selected {{
        background-color: {PU_MID_BLUE};
        color: {WHITE};
    }}

    /* ===== Group Box ===== */
    QGroupBox {{
        font-weight: bold;
        border: 1px solid {PU_BLUE};
        border-radius: 4px;
        margin-top: 14px;
        padding-top: 10px;
        background-color: {WHITE};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 6px;
        color: {PU_BLUE};
        background-color: {PU_LIGHT_BLUE};
    }}

    /* ===== Buttons ===== */
    QPushButton {{
        background-color: {PU_BLUE};
        color: {WHITE};
        border: 1px solid {PU_DARK_BLUE};
        border-radius: 4px;
        padding: 6px 14px;
        font-weight: bold;
        min-height: 18px;
    }}
    QPushButton:hover {{ background-color: {PU_MID_BLUE}; }}
    QPushButton:pressed {{ background-color: {PU_DARK_BLUE}; }}
    QPushButton:disabled {{ background-color: {LIGHT_GRAY}; color: {GRAY}; }}

    QPushButton[accent="gold"] {{
        background-color: {PU_GOLD};
        color: {PU_DARK_BLUE};
        border: 1px solid {PU_GOLD_DARK};
    }}
    QPushButton[accent="gold"]:hover {{ background-color: {PU_GOLD_LIGHT}; }}

    QPushButton[accent="danger"] {{
        background-color: {DANGER};
        color: {WHITE};
        border: 1px solid {DANGER};
    }}

    QPushButton[accent="success"] {{
        background-color: {SUCCESS};
        color: {WHITE};
        border: 1px solid {SUCCESS};
    }}

    /* ===== Tables ===== */
    QTableWidget {{
        background-color: {WHITE};
        alternate-background-color: {PU_VERY_LIGHT_BLUE};
        gridline-color: {BORDER_GRAY};
        selection-background-color: {PU_BLUE};
        selection-color: {PU_GOLD};
        border: 1px solid {PU_BLUE};
        border-radius: 3px;
    }}
    QHeaderView::section {{
        background-color: {PU_BLUE};
        color: {PU_GOLD};
        padding: 7px;
        border: none;
        border-right: 1px solid {PU_DARK_BLUE};
        border-bottom: 2px solid {PU_GOLD};
        font-weight: bold;
    }}
    QTableCornerButton::section {{ background-color: {PU_BLUE}; border: none; }}

    /* ===== Input Fields ===== */
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit, QDateEdit {{
        background-color: {WHITE};
        border: 1px solid {PU_BLUE};
        border-radius: 3px;
        padding: 5px 7px;
        selection-background-color: {PU_BLUE};
        selection-color: {PU_GOLD};
    }}
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus,
    QTextEdit:focus, QDateEdit:focus {{
        border: 2px solid {PU_GOLD};
    }}
    QComboBox::drop-down {{ border-left: 1px solid {PU_BLUE}; width: 22px; }}
    QComboBox::down-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 6px solid {PU_BLUE};
        margin-right: 6px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {WHITE};
        selection-background-color: {PU_BLUE};
        selection-color: {PU_GOLD};
        border: 1px solid {PU_BLUE};
    }}

    /* ===== Labels ===== */
    QLabel {{ color: {PU_DARK_BLUE}; }}
    QLabel[heading="true"] {{
        color: {PU_BLUE};
        font-size: 14pt;
        font-weight: bold;
        padding: 4px 0;
    }}
    QLabel[subheading="true"] {{
        color: {GRAY};
        font-style: italic;
        font-size: 9pt;
    }}
    QLabel[amount="true"] {{
        color: {PU_DARK_BLUE};
        font-weight: bold;
        font-size: 11pt;
    }}
    QLabel[grandtotal="true"] {{
        color: {DANGER};
        font-weight: bold;
        font-size: 13pt;
    }}

    /* ===== Splitter ===== */
    QSplitter::handle {{ background-color: {PU_LIGHT_BLUE}; width: 4px; }}
    QSplitter::handle:hover {{ background-color: {PU_GOLD}; }}

    /* ===== Scrollbar ===== */
    QScrollBar:vertical {{
        background: {PU_LIGHT_BLUE};
        width: 12px;
        border-radius: 6px;
    }}
    QScrollBar::handle:vertical {{
        background: {PU_BLUE};
        border-radius: 6px;
        min-height: 20px;
    }}
    QScrollBar::handle:vertical:hover {{ background: {PU_GOLD}; }}
    QScrollBar:horizontal {{
        background: {PU_LIGHT_BLUE};
        height: 12px;
        border-radius: 6px;
    }}
    QScrollBar::handle:horizontal {{
        background: {PU_BLUE};
        border-radius: 6px;
        min-width: 20px;
    }}
    QScrollBar::handle:horizontal:hover {{ background: {PU_GOLD}; }}
    """


def apply_property(widget, name, value=True):
    """Helper untuk mengaktifkan property dinamis di stylesheet."""
    widget.setProperty(name, value)
    widget.style().unpolish(widget)
    widget.style().polish(widget)


def make_heading(text: str):
    """Shortcut buat QLabel dengan style heading PU."""
    from PyQt5.QtWidgets import QLabel
    lbl = QLabel(text)
    apply_property(lbl, "heading", True)
    return lbl