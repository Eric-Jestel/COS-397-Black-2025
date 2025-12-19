import tkinter as tk
from tkinter import ttk, messagebox
from app.views.advanced_options import AdvancedOptionsDialog

BTN_BG = "#F7F7F7"


def _center_dialog(self, dialog):
    dialog.update_idletasks()
    root = self.winfo_toplevel()

    x = root.winfo_rootx() + (root.winfo_width() // 2) - (dialog.winfo_width() // 2)
    y = root.winfo_rooty() + (root.winfo_height() // 2) - (dialog.winfo_height() // 2)
    dialog.geometry(f"+{x}+{y}")


class InstrumentPageView(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.configure(style="Proto.TFrame")

        PAD = 12
        GAP = 14

        # Grid layout
        self.grid_rowconfigure(0, weight=0, minsize=190)  # slightly shorter top row
        self.grid_rowconfigure(1, weight=1)

        self.grid_columnconfigure(0, weight=0, minsize=380)
        self.grid_columnconfigure(1, weight=0, minsize=380)
        self.grid_columnconfigure(2, weight=1, minsize=560)

        # Top row
        login_panel = ttk.Frame(self, style="ProtoCard.TFrame", padding=PAD)
        steps_panel = ttk.Frame(self, style="ProtoCard.TFrame", padding=PAD)
        expl_panel = ttk.Frame(self, style="ProtoCard.TFrame", padding=PAD)

        login_panel.grid(row=0, column=0, sticky="nsew", padx=(GAP, 0), pady=(GAP, 0))
        steps_panel.grid(row=0, column=1, sticky="nsew", padx=(GAP, 0), pady=(GAP, 0))
        expl_panel.grid(row=0, column=2, sticky="nsew", padx=(GAP, GAP), pady=(GAP, 0))

        # Bottom row
        left_panel = ttk.Frame(self, style="ProtoCard.TFrame", padding=PAD)
        plot_panel = ttk.Frame(self, style="ProtoCard.TFrame", padding=PAD)

        left_panel.grid(row=1, column=0, sticky="nsew", padx=(GAP, 0), pady=(GAP, GAP))
        plot_panel.grid(
            row=1,
            column=1,
            columnspan=2,
            sticky="nsew",
            padx=(GAP, GAP),
            pady=(GAP, GAP),
        )

        left_panel.grid_rowconfigure(0, weight=1)
        left_panel.grid_columnconfigure(0, weight=1)

        # Login
        self._section_title(login_panel, "Login")

        login_body = ttk.Frame(login_panel, style="Proto.TFrame")
        login_body.pack(fill="x", expand=False, padx=0, pady=(8, 0))

        login_body.grid_columnconfigure(0, weight=1)

        self.user_label = ttk.Label(
            login_body,
            text="",
            font=("TkDefaultFont", 11, "italic"),
            anchor="center",
            justify="center",
        )
        self.user_label.grid(row=0, column=0, sticky="ew", pady=(6, 14))

        controls = ttk.Frame(login_body, style="Proto.TFrame")
        controls.grid(row=1, column=0, sticky="ew", padx=18)
        controls.grid_columnconfigure(0, weight=1)

        self.login_controls = ttk.Frame(controls, style="Proto.TFrame")
        self.login_controls.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        self.login_controls.grid_columnconfigure(0, weight=1)

        self.username_var = tk.StringVar(value="")
        self.username_entry = ttk.Entry(
            self.login_controls, textvariable=self.username_var, justify="center"
        )
        self.username_entry.grid(row=0, column=0, sticky="ew")

        self.buttons_row = ttk.Frame(controls, style="Proto.TFrame")
        self.buttons_row.grid(row=1, column=0, sticky="ew")
        self.buttons_row.grid_columnconfigure((0, 1), weight=1)

        self.login_btn = self._boxed_button(self.buttons_row, "Login", self.on_login)
        self.reset_btn = self._boxed_button(
            self.buttons_row, "Reset", self.on_reset_login
        )

        self.login_btn.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.reset_btn.grid(row=0, column=1, sticky="ew")

        # Instructions
        self._section_title(steps_panel, "Instructions")

        steps_inner = ttk.Frame(steps_panel, style="Proto.TFrame")
        steps_inner.pack(fill="both", expand=True, pady=(10, 0), padx=12)

        self._boxed_button_small(
            steps_inner, "Step 1: Login", "Login with ICN account username"
        ).pack(fill="x", pady=6)
        self._boxed_button_small(
            steps_inner,
            "Step 2: Capture sample",
            'Insert Cuvette. Close Machine. Click "Take Sample"',
        ).pack(fill="x", pady=6)
        self._boxed_button_small(
            steps_inner, "Step 3: Reset", "Click the reset button when finished"
        ).pack(fill="x", pady=6)

        # Explanation
        expl_inset = ttk.Frame(expl_panel, style="ProtoInset.TFrame", padding=12)
        expl_inset.pack(fill="both", expand=True, padx=10, pady=(16, 10))

        self.expl_label = ttk.Label(
            expl_inset,
            text="Explanation of step 1,2…",
            justify="center",
            font=("TkDefaultFont", 14),
        )
        self.expl_label.place(relx=0.5, rely=0.5, anchor="center")

        action_box = ttk.Frame(left_panel, style="Proto.TFrame")
        action_box.grid(row=1, column=0, sticky="ew", padx=0, pady=(10, 10))
        action_box.grid_columnconfigure(0, weight=1)

        btn_take = self._boxed_button(
            action_box, "Take sample", self.on_take_sample_and_return
        )
        btn_take.grid(row=0, column=0, sticky="ew")

        btn_adv = self._boxed_button(action_box, "Advanced options", self.on_adv)
        btn_adv.grid(row=1, column=0, sticky="ew", pady=(12, 0))

        # Data viewer
        plot_panel.grid_rowconfigure(0, weight=1)
        plot_panel.grid_columnconfigure(0, weight=1)

        canvas = tk.Canvas(plot_panel, background="white", highlightthickness=0)
        canvas.grid(row=0, column=0, sticky="nsew")

        canvas.create_text(
            0,
            0,
            anchor="center",
            text=(
                "Sample data\n\nIncluded:\n"
                "X-axis title\nY-axis title\n"
                "X-axis ticks + labels\nY-axis ticks + labels\n\n"
                "On hover over a line: displays sample name"
            ),
            font=("TkDefaultFont", 14),
            fill="#333",
        )

        def _center_text(event):
            canvas.coords(1, event.width // 2, event.height // 2)

        canvas.bind("<Configure>", _center_text)

    # Helpers
    def _section_title(self, parent, text):
        ttk.Label(parent, text=text, font=("TkDefaultFont", 14, "bold")).pack(
            anchor="w"
        )
        ttk.Separator(parent).pack(fill="x", pady=(8, 0))

    def _boxed_button(self, parent, text, command):
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

    def _boxed_button_small(self, parent, text, command):
        # Same styling as SetupPage, but slightly tighter for the step list.
        return tk.Button(
            parent,
            text=text,
            command=command,
            fg="black",
            relief="flat",
            padx=12,
            pady=10,
            font=("TkDefaultFont", 13),
        )

    def on_login(self):
        username = self.username_var.get().strip()
        if not username:
            messagebox.showwarning("Login", "Please enter a username.")
            return

        self.app.state.username = username
        self.user_label.config(text=f"Current User: {username}")

        # Hide entry row
        self.login_controls.grid_remove()

        # Hide login button
        self.login_btn.grid_remove()

        # Center Reset by letting it span both columns
        self.reset_btn.grid_configure(column=0, columnspan=2, padx=0)

    def on_reset_login(self):
        self.app.state.username = ""
        self.user_label.config(text="")
        self.username_var.set("")

        self.login_controls.grid()
        self.login_btn.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.reset_btn.grid_configure(column=1, columnspan=1, padx=0)

        self.username_entry.focus_set()

    def on_take_sample_and_return(self):
        messagebox.showinfo("Take sample", "Prototype: sample captured.")

    def on_adv(self):
        # Prevent duplicate dialogs
        if getattr(self, "_adv_dialog", None) and self._adv_dialog.winfo_exists():
            self._adv_dialog.lift()
            self._adv_dialog.focus_force()
            return

        self._adv_dialog = AdvancedOptionsDialog(self, self.app)

        _center_dialog(self, self._adv_dialog)
