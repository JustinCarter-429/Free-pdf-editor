# app/utils.py

from __future__ import annotations

import os
import sys
from typing import Optional

from PySide6.QtWidgets import QMessageBox, QWidget


def resource_path(relative_path: str) -> str:
    """
    Resolve a path to a resource (icon, etc.) that works:
    When running from source
    When running from a PyInstaller-built .exe

    PyInstaller sets sys._MEIPASS to a temporary folder where it unpacks files.
    """
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base_path, relative_path)


def show_error_dialog(parent: Optional[QWidget], title: str, message: str) -> None:
    """
    Show a standardized error dialog.

    param parent: Qt parent widget (or None)
    param title:  dialog window title
    param message: message body
    """
    QMessageBox.critical(parent, title, message)


def show_info_dialog(parent: Optional[QWidget], title: str, message: str) -> None:
    """
    Show a standardized information dialog.
    """
    QMessageBox.information(parent, title, message)
