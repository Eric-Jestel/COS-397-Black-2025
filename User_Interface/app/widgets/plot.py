import tkinter as tk
from tkinter import ttk

class PlaceholderPlot(ttk.Frame):
    
    def __init__(self, parent, title: str):
        super().__init__(parent)
        ttk.Label(self, text=title, font=("TkDefaultFont", 11, "bold")).pack(anchor="w")
        self.canvas = tk.Canvas(self, height=260)
        self.canvas.pack(fill="both", expand=True, pady=(6, 0))
        self._draw_placeholder()

    def _draw_placeholder(self):
        self.canvas.delete("all")
        w = int(self.canvas.winfo_reqwidth())
        h = 260
        # axes
        self.canvas.create_line(50, 20, 50, h-40)
        self.canvas.create_line(50, h-40, w-20, h-40)
        self.canvas.create_text(60, 20, anchor="nw", text="(prototype plot area)")
        self.canvas.create_text(w//2, h-25, text="X-axis title / ticks")
        self.canvas.create_text(18, h//2, angle=90, text="Y-axis title / ticks")
