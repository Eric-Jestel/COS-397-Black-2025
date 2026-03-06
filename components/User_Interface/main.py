from app.app import PrototypeApp
from pathlib import Path
import os

def main():
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    if (False):
        PROJECT_ROOT = r"C:\Users\Administrator\Documents\COS397Capstone\COS-397-Black-2025"
    print(f"Project root: {PROJECT_ROOT}")
    app = PrototypeApp(PROJECT_ROOT)
    app.run()


if __name__ == "__main__":
    main()
