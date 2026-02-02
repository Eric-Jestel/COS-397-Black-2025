# Tk root + frame router
import tkinter as tk
from tkinter import ttk

from app.config import APP_TITLE, WINDOW_MIN_SIZE
from app.state import UIState
from app.views.setup_page import SetupPageView
from app.views.instrument_page import InstrumentPageView


class PrototypeApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        self.root.minsize(*WINDOW_MIN_SIZE)

        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        # Page background
        style.configure("Proto.TFrame", background="#EDEBE6")

        # Section background
        style.configure(
            "Panel.TFrame", background="#DEDBD5", relief="solid", borderwidth=1
        )

        # White inset
        style.configure(
            "Inset.TFrame", background="white", relief="solid", borderwidth=1
        )

        self.state = UIState()

        container = ttk.Frame(self.root, padding=12)
        container.grid(row=0, column=0, sticky="nsew")
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        self.frames = {}
        for FrameCls, name in [
            (SetupPageView, "setup"),
            (InstrumentPageView, "session"),
        ]:
            frame = FrameCls(parent=container, app=self)
            frame.grid(row=0, column=0, sticky="nsew")
            self.frames[name] = frame

        self.show("setup")

    def show(self, name: str):
        self.frames[name].tkraise()

    def run(self):
        self.root.mainloop()
