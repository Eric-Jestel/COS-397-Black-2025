from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# ── Palette ─────────────────────
BG = "#E4E4E4"
BG_BTN = "#C8C8C8"
BG_BTN_HOV = "#BEBEBE"
BG_BTN_PRS = "#B0B0B0"
BORDER = "#CACACA"
TEXT_MAIN = "#484848"
TEXT_BTN = "#3A3A3A"


class StyledButton(QPushButton):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFont(QFont("Helvetica Neue", 9))
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_BTN};
                color: {TEXT_BTN};
                border: none;
                border-radius: 4px;
                padding: 5px 16px;
            }}
            QPushButton:hover   {{ background-color: {BG_BTN_HOV}; }}
            QPushButton:pressed {{ background-color: {BG_BTN_PRS}; }}
            """)


class AdvancedOptionsDialog(QDialog):
    def __init__(self, parent=None, app=None):
        super().__init__(parent)
        self.app = app
        self.setWindowTitle("Advanced Options")
        self.setModal(True)
        self.setMinimumWidth(320)
        self.setStyleSheet(f"background-color: {BG};")

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        title = QLabel("Advanced Options")
        title.setFont(QFont("Georgia", 13, QFont.Weight.Bold))
        title.setStyleSheet(
            f"color: {TEXT_MAIN}; background: transparent; border: none;"
        )
        root.addWidget(title)

        subtitle = QLabel("FOR TA USE ONLY")
        subtitle.setFont(QFont("Helvetica Neue", 9))
        subtitle.setStyleSheet(
            "color: #CC0000; background: transparent; border: none;"
        )
        root.addWidget(subtitle)

        # Back button
        back_btn = StyledButton("Go back to setup page")
        back_btn.clicked.connect(self._go_to_setup)
        root.addWidget(back_btn)

    def _go_to_setup(self):
        self.accept()
        if self.app:
            self.app.go_to_setup_page()
