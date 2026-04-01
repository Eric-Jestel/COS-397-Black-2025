from app.app import App
from pathlib import Path
import os
import sys


def main():
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    if True:
        PROJECT_ROOT = r"C:\Users\Agilent Cary 60\Documents\SoftwareDev - dont delete\COS-397-Black-2025"
    # TODO: Ensure the existence of config and folders
    print(f"Project root: {PROJECT_ROOT}")
    app = App(PROJECT_ROOT)
    app.run()


if __name__ == "__main__":
    main()
