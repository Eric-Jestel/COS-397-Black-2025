import tkinter as tk
from tkinter import ttk, messagebox

BTN_BG = "#F7F7F7"


class InstrumentPageView(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.configure(style="Proto.TFrame")

        PAD = 12
        GAP = 14

        # Grid layout
        self.grid_rowconfigure(0, weight=0, minsize=190)   # slightly shorter top row
        self.grid_rowconfigure(1, weight=1)

        self.grid_columnconfigure(0, weight=0, minsize=380)
        self.grid_columnconfigure(1, weight=0, minsize=380)
        self.grid_columnconfigure(2, weight=1, minsize=560)

        # Top row 
        login_panel = ttk.Frame(self, style="Panel.TFrame", padding=PAD)
        steps_panel = ttk.Frame(self, style="Panel.TFrame", padding=PAD)
        expl_panel = ttk.Frame(self, style="Panel.TFrame", padding=PAD)

        login_panel.grid(row=0, column=0, sticky="nsew", padx=(GAP, 0), pady=(GAP, 0))
        steps_panel.grid(row=0, column=1, sticky="nsew", padx=(GAP, 0), pady=(GAP, 0))
        expl_panel.grid(row=0, column=2, sticky="nsew", padx=(GAP, GAP), pady=(GAP, 0))

        # Bottom row 
        left_panel = ttk.Frame(self, style="Panel.TFrame", padding=PAD)
        plot_panel = ttk.Frame(self, style="Panel.TFrame", padding=PAD)

        left_panel.grid(row=1, column=0, sticky="nsew", padx=(GAP, 0), pady=(GAP, GAP))
        plot_panel.grid(row=1, column=1, columnspan=2, sticky="nsew", padx=(GAP, GAP), pady=(GAP, GAP))

        left_panel.grid_rowconfigure(0, weight=1)

        # Login 
        self._section_title(login_panel, "Enter Username")

        ttk.Label(login_panel, text="Username", font=("TkDefaultFont", 11, "italic")).pack(pady=(6, 6))
        self.username_var = tk.StringVar(value=self.app.state.username)

        ttk.Entry(login_panel, textvariable=self.username_var, justify="center").pack(
            fill="x", padx=18, pady=(0, 12)
        )

        btn_row = ttk.Frame(login_panel, style="Proto.TFrame")
        btn_row.pack(fill="x", padx=18)
        btn_row.grid_columnconfigure((0, 1), weight=1)

        self._boxed_button(btn_row, "Login", self.on_login).grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self._boxed_button(btn_row, "Reset", self.on_reset_login).grid(row=0, column=1, sticky="ew")

        # Instructions
        self._section_title(steps_panel, "Instructions")

        steps_inner = ttk.Frame(steps_panel, style="Proto.TFrame")
        steps_inner.pack(fill="both", expand=True, pady=(10, 0), padx=12)

        self._boxed_button_small(steps_inner, "Step 1: Login", lambda: self.set_explanation(1)).pack(fill="x", pady=6)
        self._boxed_button_small(steps_inner, "Step 2: Capture sample", lambda: self.set_explanation(2)).pack(fill="x", pady=6)
        self._boxed_button_small(steps_inner, "Step N: …", lambda: self.set_explanation(3)).pack(fill="x", pady=6)

        # Explanation 
        expl_inset = ttk.Frame(expl_panel, style="Inset.TFrame", padding=14)
        expl_inset.pack(fill="both", expand=True, padx=10, pady=(16, 10))

        self.expl_label = ttk.Label(
            expl_inset,
            text="Explanation of step 1,2…",
            justify="center",
            font=("TkDefaultFont", 12)
        )
        self.expl_label.place(relx=0.5, rely=0.5, anchor="center")

        
        # Large buttons + clean spacing
        action_box = ttk.Frame(left_panel, style="Proto.TFrame")
        action_box.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        action_box.grid_columnconfigure(0, weight=1)

        btn_take = self._boxed_button(action_box, "Take sample", self.on_take_sample_and_return)
        btn_take.grid(row=0, column=0, sticky="ew")

        btn_adv = self._boxed_button(action_box, "Advanced options", self.on_adv)
        btn_adv.grid(row=1, column=0, sticky="ew", pady=(12, 0))

        # Data viewer
        self._section_title(plot_panel, "Data viewer")

        inset = ttk.Frame(plot_panel, style="Inset.TFrame")
        inset.pack(fill="both", expand=True, padx=10, pady=(16, 10))

        canvas = tk.Canvas(inset, background="white", highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        canvas.create_text(
            0, 0,
            anchor="center",
            text=(
                "Sample data\n\nIncluded:\n"
                "X-axis title\nY-axis title\n"
                "X-axis ticks + labels\nY-axis ticks + labels\n\n"
                "On hover over a line: displays sample name"
            ),
            font=("TkDefaultFont", 14),
            fill="#333"
        )
        canvas.bind("<Configure>", lambda e: canvas.coords(1, e.width // 2, e.height // 2))

    # Helpers
    def _section_title(self, parent, text):
        ttk.Label(parent, text=text, font=("TkDefaultFont", 16, "bold")).pack()
        ttk.Separator(parent).pack(fill="x", pady=(10, 0))

    def _boxed_button(self, parent, text, command):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=BTN_BG,
            activebackground=BTN_BG,
            relief="solid",
            borderwidth=2,
            padx=14,
            pady=14,
            font=("TkDefaultFont", 13)
        )

    def _boxed_button_small(self, parent, text, command):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=BTN_BG,
            activebackground=BTN_BG,
            relief="solid",
            borderwidth=2,
            padx=12,
            pady=8,
            font=("TkDefaultFont", 12)
        )

    # Logic
    def set_explanation(self, step):
        self.expl_label.configure(text=f"Step {step} explanation placeholder.")

    def on_login(self):
        self.app.state.username = self.username_var.get().strip()
        if not self.app.state.username:
            messagebox.showwarning("Login", "Please enter a username.")
            return
        messagebox.showinfo("Login", f"Logged in as {self.app.state.username}")

    def on_reset_login(self):
        self.username_var.set("")
        self.app.state.username = ""

    def on_take_sample_and_return(self):
        messagebox.showinfo("Take sample", "Prototype: sample captured.")
        self.app.show("setup")

    def on_adv(self):
        messagebox.showinfo("Advanced options", "Prototype placeholder.")
