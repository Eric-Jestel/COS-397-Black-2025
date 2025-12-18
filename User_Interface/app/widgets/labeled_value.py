from tkinter import ttk


class LabeledValue(ttk.Frame):
    def __init__(self, parent, label: str, value: str = "-"):
        super().__init__(parent)
        self._label = ttk.Label(self, text=label)
        self._value = ttk.Label(self, text=value, font=("TkDefaultFont", 10, "bold"))

        self._label.grid(row=0, column=0, sticky="w")
        self._value.grid(row=1, column=0, sticky="w")

    def set(self, value: str):
        self._value.configure(text=value)
