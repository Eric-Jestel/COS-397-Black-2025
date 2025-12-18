import tkinter as tk
from tkinter import ttk, messagebox

from app.config import PANEL_PAD
from app.widgets.plot import PlaceholderPlot

class InstrumentPageView(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        left = ttk.Frame(self, padding=PANEL_PAD)
        right = ttk.Frame(self, padding=PANEL_PAD)
        left.grid(row=0, column=0, sticky="nsew")
        right.grid(row=0, column=1, sticky="nsew")

        ttk.Label(left, text="Enter Username", font=("TkDefaultFont", 14, "bold")).pack(anchor="w")

        form = ttk.Frame(left)
        form.pack(fill="x", pady=(8, 10))
        ttk.Label(form, text="Username").grid(row=0, column=0, sticky="w")
        self.username_var = tk.StringVar(value=self.app.state.username)
        ttk.Entry(form, textvariable=self.username_var).grid(row=1, column=0, sticky="ew", pady=(4, 0))
        form.columnconfigure(0, weight=1)

        btn_row = ttk.Frame(left)
        btn_row.pack(fill="x", pady=(0, 10))
        ttk.Button(btn_row, text="Login", command=self.on_login).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ttk.Button(btn_row, text="Reset", command=self.on_reset_login).pack(side="left", expand=True, fill="x")

        ttk.Button(left, text="Take sample", command=self.on_take_sample).pack(fill="x", pady=(0, 8))
        ttk.Button(left, text="Advanced options", command=self.on_adv).pack(fill="x")

        instr = ttk.LabelFrame(left, text="Instructions")
        instr.pack(fill="both", expand=True, pady=(12, 0))
        self.instructions = tk.Text(instr, height=10, wrap="word")
        self.instructions.insert("1.0",
            "Step 1: Login\nExplanation of step 1,2…\n\n"
            "Step 2: Capture sample\nStep N: …\n\n"
            "(Prototype: replace with your final instruction behavior.)"
        )
        self.instructions.configure(state="disabled")
        self.instructions.pack(fill="both", expand=True, padx=6, pady=6)

        # Right side: plot placeholder for sample data/data viewer
        self.plot = PlaceholderPlot(right, title="Sample data / Data viewer")
        self.plot.pack(fill="both", expand=True)

        ttk.Button(right, text="Back to instrumentation page", command=lambda: self.app.show("setup")).pack(
            anchor="e", pady=(10, 0)
        )

    def on_login(self):
        self.app.state.username = self.username_var.get().strip()
        if not self.app.state.username:
            messagebox.showwarning("Login", "Please enter a username.")
            return
        # Prototype: success dialog
        messagebox.showinfo("Login", f"Logged in as: {self.app.state.username}")

    def on_reset_login(self):
        self.username_var.set("")
        self.app.state.username = ""

    def on_take_sample(self):
        # Prototype confirmation (maps to “Take sample confirmation popup” idea) :contentReference[oaicite:10]{index=10}
        ok = messagebox.askyesno("Take Sample", "Have you inserted the cuvette into the instrument?")
        if ok:
            # Prototype: append a fake filename
            fname = f"{self.app.state.username or 'user'}_sample_{len(self.app.state.sample_files)+1}.csv"
            self.app.state.sample_files.append(fname)
            messagebox.showinfo("Sample taken", f"Saved: {fname}\n(Prototype: upload status not implemented.)")

    def on_adv(self):
        messagebox.showinfo("Advanced options", "Prototype placeholder (wire to AdvancedOptionsDialog if desired).")
