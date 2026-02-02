import tkinter as tk
from tkinter import ttk


class AdvancedOptionsDialog(tk.Toplevel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.title("Advanced Options")
        self.transient(parent.winfo_toplevel())
        self.grab_set()

        root = ttk.Frame(self, padding=12)
        root.pack(fill="both", expand=True)

        ttk.Label(
            root, text="Advanced Options", font=("TkDefaultFont", 14, "bold")
        ).pack(anchor="w")

        blank = ttk.LabelFrame(root, text="Blank options")
        blank.pack(fill="x", pady=(10, 0))

        ttk.Button(blank, text="Capture Blank", command=lambda: None).pack(
            fill="x", pady=4
        )
        ttk.Button(blank, text="Load Blank from File", command=lambda: None).pack(
            fill="x", pady=4
        )
        ttk.Button(blank, text="Reset Blank", command=lambda: None).pack(
            fill="x", pady=4
        )

        ttk.Button(root, text="Back to instrument page", command=self.destroy).pack(
            fill="x", pady=(12, 0)
        )
