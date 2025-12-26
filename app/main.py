# app/main.py

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from ui import MainWindow


def main() -> None:
    """
    Entry point for the PDF Merge & Split Tool.
    Creates the QApplication
    Instantiates and shows MainWindow
    Starts the Qt event loop
    """
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    # Start Qt event loop and exit when window is closed
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
