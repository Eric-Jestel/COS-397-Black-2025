import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from pathlib import Path

from app.dialogs.file_selector import ask_open_csv
from app.views.advanced_options import AdvancedOptionsDialog

BG = "#EDEBE6"


class SetupPageView(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        # Column widths are "locked" via minsize to keep the mockup look.
        self.grid_rowconfigure(0, weight=0, minsize=170)  # top info row
        self.grid_rowconfigure(1, weight=1)  # main content row grows

        self.grid_columnconfigure(0, weight=0, minsize=360)  # left control column
        self.grid_columnconfigure(1, weight=1, minsize=420)  # center column
        self.grid_columnconfigure(2, weight=1, minsize=420)  # right column

        # unify background for prototype
        self.configure(style="Proto.TFrame")

        # Panels
        title_card = ttk.Frame(self, style="ProtoCard.TFrame", padding=14)
        instr_top = ttk.Frame(self, style="ProtoCard.TFrame", padding=12)
        server_top = ttk.Frame(self, style="ProtoCard.TFrame", padding=12)

        left_controls = ttk.Frame(self, style="ProtoCard.TFrame", padding=14)
        plot_panel = ttk.Frame(self, style="ProtoCard.TFrame", padding=12)

        title_card.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        instr_top.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        server_top.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)

        left_controls.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        plot_panel.grid(
            row=1, column=1, columnspan=2, sticky="nsew", padx=10, pady=(0, 10)
        )

        # Title card
        ttk.Label(
            title_card, text="Chemistry", font=("TkDefaultFont", 22, "bold")
        ).pack(anchor="center")
        ttk.Label(
            title_card, text="Instrumentation", font=("TkDefaultFont", 22, "bold")
        ).pack(anchor="center")
        ttk.Separator(title_card).pack(fill="x", pady=10)

        ttk.Label(title_card, text="Developed by Jack of all Spades").pack()
        ttk.Label(title_card, text="Licensed under …, 2025").pack()
        ttk.Label(title_card, text="").pack()

        #  Top blocks
        self._build_top_block(
            parent=instr_top,
            title="Instrument information",
            info_text="Instrument information",
            status_title="Instrument\nconnection status",
            reconnect_cmd=self.on_reconnect_instrument,
        )

        self._build_top_block(
            parent=server_top,
            title="ICN Server\nInformation",
            info_text="Server Diagnostic\nInformation",
            status_title="Instrument\nconnection status",
            reconnect_cmd=self.on_reconnect_server,
        )

        # Left controls
        ttk.Label(left_controls, text="Blank", font=("TkDefaultFont", 12, "bold")).grid(
            row=0, column=0, sticky="w"
        )

        # button stack frame
        btn_frame = ttk.Frame(left_controls, style="Proto.TFrame")
        btn_frame.grid(row=1, column=0, sticky="nsew", pady=(8, 10))
        left_controls.grid_rowconfigure(1, weight=1)
        left_controls.grid_columnconfigure(0, weight=1)

        # Buttons in left columns nav
        self.button(btn_frame, "Capture Blank", self.on_capture_blank).pack(
            fill="x", pady=10
        )
        self.button(btn_frame, "Load Blank from File", self.on_load_blank).pack(
            fill="x", pady=10
        )
        self.button(btn_frame, "Reset Blank", self.on_reset_blank).pack(
            fill="x", pady=10
        )
        self.button(btn_frame, "Save Blank to File", self.on_save_blank).pack(
            fill="x", pady=10
        )

        self.button(
            left_controls, "Continue to main session", lambda: self.app.show("session")
        ).grid(row=2, column=0, sticky="ew", pady=(8, 8))

        self.button(left_controls, "Debugging mode", self.on_toggle_debug).grid(
            row=3, column=0, sticky="ew", pady=(8, 0)
        )

        # Plot panel
        plot_panel.grid_rowconfigure(0, weight=1)
        plot_panel.grid_columnconfigure(0, weight=1)

        plot_canvas = tk.Canvas(
            plot_panel,
            background="white",
            highlightthickness=1,
            highlightbackground="#A0A0A0",
        )
        plot_canvas.grid(row=0, column=0, sticky="nsew")

        # Center placeholder text
        plot_canvas.create_text(
            0,
            0,
            anchor="center",
            text="Blank spectra\n\nIncluded:\nX-axis title\nY-axis title\nX-axis ticks + labels\nY-axis ticks + labels",
            font=("TkDefaultFont", 16),
            fill="#333",
        )

        # Re-center when resized
        def _center_text(event):
            plot_canvas.coords(1, event.width // 2, event.height // 2)

        plot_canvas.bind("<Configure>", _center_text)

    def _build_top_block(self, parent, title, info_text, status_title, reconnect_cmd):
        # Layout inside top block: left info area, right status/reconnect column
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=0, minsize=200)
        parent.grid_rowconfigure(1, weight=1)

        ttk.Label(parent, text=title, font=("TkDefaultFont", 14, "bold")).grid(
            row=0, column=0, sticky="w", padx=(2, 8), pady=(0, 6)
        )

        info_box = ttk.Frame(parent, style="ProtoInset.TFrame", padding=12)
        info_box.grid(row=1, column=0, sticky="nsew", padx=(0, 10))

        ttk.Label(info_box, text=info_text, font=("TkDefaultFont", 16)).place(
            relx=0.5, rely=0.5, anchor="center"
        )

        status_col = ttk.Frame(parent, style="Proto.TFrame")
        status_col.grid(row=0, column=1, rowspan=2, sticky="nsew")

        status_label = ttk.Frame(status_col, style="ProtoInset.TFrame", padding=8)
        status_label.pack(fill="x")

        ttk.Label(status_label, text=status_title, justify="center").pack()

        self.button(status_col, "Reconnect", reconnect_cmd).pack(fill="x", pady=(20, 0))

    def button(self, parent, text, command):
        return tk.Button(
            parent,
            text=text,
            command=command,
            fg="black",
            relief="flat",
            padx=12,
            pady=14,
            font=("TkDefaultFont", 14),
        )

    # Stub handlers
    def on_capture_blank(self):
        target = (
            Path(self.app.controller.ServController.file_dir)
            / f"blank_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        code, blank_path = self.app.controller.takeBlank(str(target))
        if code == 0:
            self.app.state.blank_file_path = blank_path
            messagebox.showinfo("Capture Blank", f"Blank captured: {blank_path}")
        else:
            messagebox.showerror(
                "Capture Blank",
                self.app.controller.ErrorDictionary.get(code, f"Error code: {code}"),
            )

    def on_load_blank(self):
        path = ask_open_csv(self)
        if path:
            code = self.app.controller.setBlank(path)
            if code == 0:
                self.app.state.blank_file_path = path
                messagebox.showinfo("Load Blank", f"Loaded blank file:\n{path}")
            else:
                messagebox.showerror(
                    "Load Blank",
                    self.app.controller.ErrorDictionary.get(
                        code, f"Error code: {code}"
                    ),
                )

    def on_save_blank(self):
        if self.app.state.blank_file_path:
            messagebox.showinfo(
                "Save Blank",
                "Blank is already stored by the instrument bridge at:\n"
                f"{self.app.state.blank_file_path}",
            )
            return
        messagebox.showwarning("Save Blank", "No blank is currently loaded.")

    def on_reset_blank(self):
        if hasattr(self.app.controller.InstController, "clear_blank"):
            self.app.controller.InstController.clear_blank()
        self.app.state.blank_file_path = None

    def on_toggle_debug(self):
        self.app.state.debug_mode = not self.app.state.debug_mode
        debug_on = self.app.state.debug_mode
        self.app.controller.debug = debug_on
        self.app.controller.InstController.debug = debug_on
        self.app.controller.ServController.debug = debug_on
        messagebox.showinfo("Debug Mode", f"Debug mode {'enabled' if debug_on else 'disabled'}.")

    def on_reconnect_instrument(self):
        self.app.state.instrument_connected = self.app.controller.InstController.ping()
        if not self.app.state.instrument_connected:
            messagebox.showwarning("Instrument", "Instrument reconnect failed.")

    def on_reconnect_server(self):
        self.app.state.server_status = (
            "OK" if self.app.controller.ServController.connect() else "Disconnected"
        )
        if self.app.state.server_status != "OK":
            messagebox.showwarning("Server", "Server reconnect failed.")

    def open_advanced_options(self):
        AdvancedOptionsDialog(self, app=self.app)
