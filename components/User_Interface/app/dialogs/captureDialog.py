from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

# ── Palette ─────────────────────
BG = "#E4E4E4"
TEXT_MAIN = "#484848"
TEXT_MUTED = "#909090"


class CaptureWorker(QThread):
    """Runs a blocking capture function on a background thread."""
    finished = pyqtSignal(object)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def run(self):
        result = self._func(*self._args, **self._kwargs)
        self.finished.emit(result)


class CaptureDialog(QDialog):
    """
    Progress dialog shown while a capture is running.
    Includes a Cancel button; clicking it shows a confirmation prompt.
    If confirmed, emits `cancelled` and closes — the caller is responsible
    for discarding any in-progress data.
    """
    cancelled = pyqtSignal()

    def __init__(self, title="Capturing", message="Please wait...", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(340, 150)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.WindowTitleHint
        )
        self.setStyleSheet(f"background-color: {BG};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        msg = QLabel(message)
        msg.setFont(QFont("Helvetica Neue", 10))
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setWordWrap(True)
        msg.setStyleSheet(
            f"color: {TEXT_MAIN}; background: transparent; border: none;"
        )
        layout.addWidget(msg)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(32)
        cancel_btn.setFont(QFont("Helvetica Neue", 9))
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton          { background-color: #D32F2F; color: #FFFFFF;
                                   border: none; border-radius: 4px; padding: 5px 16px; }
            QPushButton:hover    { background-color: #C62828; }
            QPushButton:pressed  { background-color: #B71C1C; }
        """)
        cancel_btn.clicked.connect(self._on_cancel)
        layout.addWidget(cancel_btn)

    def _on_cancel(self):
        reply = QMessageBox.question(
            self,
            "Cancel Capture",
            "Are you sure you want to cancel?\nAny captured data will be discarded.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.cancelled.emit()
            self.done(0)

    def closeEvent(self, event):
        """Prevent the user from closing the dialog manually."""
        event.ignore()

    def reject(self):
        """Prevent ESC key from closing the dialog."""
        pass
