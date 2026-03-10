"""
LabeledValue widget — PyQt6
Chemistry Instrumentation — Jack of all Spades

Replaces the old Tkinter LabeledValue stub.
A small stacked label/value pair used in status panels.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

TEXT_MAIN  = "#484848"
TEXT_MUTED = "#909090"


class LabeledValue(QWidget):
    """
    Displays a small descriptor label above a larger bold value.

    Usage
    -----
        lv = LabeledValue("Server Status", "OK")
        lv.set("Disconnected")
    """

    def __init__(self, label: str, value: str = "—", parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self._label_widget = QLabel(label)
        self._label_widget.setFont(QFont("Helvetica Neue", 9))
        self._label_widget.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self._label_widget.setStyleSheet(
            f"color: {TEXT_MUTED}; background: transparent; border: none;"
        )

        self._value_widget = QLabel(value)
        self._value_widget.setFont(QFont("Helvetica Neue", 10, QFont.Weight.Bold))
        self._value_widget.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self._value_widget.setStyleSheet(
            f"color: {TEXT_MAIN}; background: transparent; border: none;"
        )

        layout.addWidget(self._label_widget)
        layout.addWidget(self._value_widget)

    def set(self, value: str):
        """Update the displayed value."""
        self._value_widget.setText(value)

    def set_ok(self, value: str, ok: bool = True):
        """Update value and colour it green/red based on ok flag."""
        self._value_widget.setText(value)
        colour = "#50A060" if ok else "#B04040"
        self._value_widget.setStyleSheet(
            f"color: {colour}; background: transparent; border: none;"
        )