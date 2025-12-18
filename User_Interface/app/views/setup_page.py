from tkinter import ttk
from app.config import PANEL_PAD
from app.widgets.labeled_value import LabeledValue
from app.widgets.plot import PlaceholderPlot
from app.dialogs.file_selector import ask_open_csv
from app.views.advanced_options import AdvancedOptionsDialog

class SetupPageView(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        # Layout: left controls + right plot/status
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        left = ttk.Frame(self, padding=PANEL_PAD)
        right = ttk.Frame(self, padding=PANEL_PAD)
        left.grid(row=0, column=0, sticky="nsew")
        right.grid(row=0, column=1, sticky="nsew")

        # Header / branding (prototype)
        ttk.Label(left, text="Chemistry 1", font=("TkDefaultFont", 16, "bold")).pack(anchor="w")
        ttk.Label(left, text="Instrumentation", font=("TkDefaultFont", 12)).pack(anchor="w", pady=(0, 12))

        # Buttons (from page 1)
        btns = ttk.LabelFrame(left, text="Blank")
        btns.pack(fill="x", pady=(0, 12))

        ttk.Button(btns, text="Capture Blank", command=self.on_capture_blank).pack(fill="x", pady=4)
        ttk.Button(btns, text="Load Blank from File", command=self.on_load_blank).pack(fill="x", pady=4)
        ttk.Button(btns, text="Save Blank to File", command=self.on_save_blank).pack(fill="x", pady=4)
        ttk.Button(btns, text="Reset Blank", command=self.on_reset_blank).pack(fill="x", pady=4)

        # Debugging mode + continue (from page 1)
        bottom = ttk.Frame(left)
        bottom.pack(fill="x", pady=(8, 0))

        self.debug_var = ttk.Checkbutton(
            bottom,
            text="Debugging mode",
            command=self.on_toggle_debug
        )
        self.debug_var.pack(anchor="w", pady=(0, 10))

        ttk.Button(
            bottom,
            text="Continue to main session",
            command=lambda: self.app.show("session")
        ).pack(fill="x")

        ttk.Button(
            bottom,
            text="Advanced options",
            command=self.open_advanced_options
        ).pack(fill="x", pady=(8, 0))

        # Right side: plot + info panels
        right.columnconfigure(0, weight=1)

        self.plot = PlaceholderPlot(right, title="Blank spectra")
        self.plot.pack(fill="both", expand=True)

        info_row = ttk.Frame(right)
        info_row.pack(fill="x", pady=(10, 0))
        for i in range(3):
            info_row.columnconfigure(i, weight=1)

        # These mirror “Instrument information”, “ICN Server Information”, and connection status blocks (page 1)
        instrument_panel = ttk.LabelFrame(info_row, text="Instrument information")
        server_panel = ttk.LabelFrame(info_row, text="ICN Server Information")
        status_panel = ttk.LabelFrame(info_row, text="Connection")

        instrument_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        server_panel.grid(row=0, column=1, sticky="nsew", padx=(0, 8))
        status_panel.grid(row=0, column=2, sticky="nsew")

        self.instrument_id = LabeledValue(instrument_panel, "Instrument", "Spectrometer A")
        self.instrument_id.pack(anchor="w", padx=8, pady=8)

        self.server_status = LabeledValue(server_panel, "Server Diagnostic", self.app.state.server_status)
        self.server_status.pack(anchor="w", padx=8, pady=8)

        self.conn_status = LabeledValue(status_panel, "Instrument connection status",
                                        "Connected" if self.app.state.instrument_connected else "Disconnected")
        self.conn_status.pack(anchor="w", padx=8, pady=8)
        ttk.Button(status_panel, text="Reconnect", command=self.on_reconnect).pack(fill="x", padx=8, pady=(0, 8))

    # ---- Stub handlers (prototype) ----
    def on_capture_blank(self):
        # Prototype: flip a bit of state, update UI text
        self.app.state.blank_file_path = "captured_blank.csv (not saved)"
        # In a later iteration, you could render a simple polyline on the Canvas.

    def on_load_blank(self):
        path = ask_open_csv(self)
        if path:
            self.app.state.blank_file_path = path

    def on_save_blank(self):
        # Prototype: no file I/O yet
        pass

    def on_reset_blank(self):
        self.app.state.blank_file_path = None

    def on_toggle_debug(self):
        self.app.state.debug_mode = not self.app.state.debug_mode

    def on_reconnect(self):
        self.app.state.instrument_connected = True
        self.conn_status.set("Connected")

    def open_advanced_options(self):
        AdvancedOptionsDialog(self, app=self.app)
