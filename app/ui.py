# app/ui.py

from __future__ import annotations

import os
from typing import List, Optional

from PySide6.QtCore import Qt, QUrl, QSize
from PySide6.QtGui import QPixmap, QImage, QPainter
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QLabel,
    QFileDialog,
    QLineEdit,
    QGroupBox,
    QFormLayout,
    QSizePolicy,
    QStackedWidget,
    QScrollArea,
)

import fitz  # PyMuPDF for thumbnails

from pdf_engine import PdfEngine
from utils import show_error_dialog, show_info_dialog


class MainWindow(QMainWindow):
    """
    Main application window with menu-based navigation.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.setWindowTitle("PDF Tool")
        self.resize(900, 600)

        # Stacked widget to switch between pages
        self.stack = QStackedWidget()
        
        # Create all pages
        self.menu_page = self._create_menu_page()
        self.merge_page = MergePage(self)
        self.split_page = SplitPage(self)
        self.convert_page = ConvertPage(self)
        
        # Add pages to stack
        self.stack.addWidget(self.menu_page)
        self.stack.addWidget(self.merge_page)
        self.stack.addWidget(self.split_page)
        self.stack.addWidget(self.convert_page)
        
        self.setCentralWidget(self.stack)
        
    def _create_menu_page(self) -> QWidget:
        """Create the main menu page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        
        title = QLabel("PDF Tool")
        title.setStyleSheet("font-size: 32px; font-weight: bold; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel("Choose an operation:")
        subtitle.setStyleSheet("font-size: 16px; margin-bottom: 40px;")
        subtitle.setAlignment(Qt.AlignCenter)
        
        # Menu buttons
        btn_merge = QPushButton("Merge PDFs")
        btn_merge.setMinimumSize(250, 60)
        btn_merge.setStyleSheet("font-size: 16px;")
        btn_merge.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        
        btn_split = QPushButton("Split PDF")
        btn_split.setMinimumSize(250, 60)
        btn_split.setStyleSheet("font-size: 16px;")
        btn_split.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        
        btn_convert = QPushButton("Convert PDF to DOCX")
        btn_convert.setMinimumSize(250, 60)
        btn_convert.setStyleSheet("font-size: 16px;")
        btn_convert.clicked.connect(lambda: self.stack.setCurrentIndex(3))
        
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(btn_merge, alignment=Qt.AlignCenter)
        layout.addSpacing(15)
        layout.addWidget(btn_split, alignment=Qt.AlignCenter)
        layout.addSpacing(15)
        layout.addWidget(btn_convert, alignment=Qt.AlignCenter)
        layout.addStretch()
        
        return page
    
    def show_menu(self) -> None:
        """Return to main menu."""
        self.stack.setCurrentIndex(0)

    def show_menu(self) -> None:
        """Return to main menu."""
        self.stack.setCurrentIndex(0)


class MergePage(QWidget):
    """Page for merging PDFs with preview and drag-to-reorder."""
    
    def __init__(self, main_window: MainWindow, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.main_window = main_window
        self._build_ui()
        
    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        
        # Header with back button
        header = QHBoxLayout()
        btn_back = QPushButton("← Back to Menu")
        btn_back.clicked.connect(self.main_window.show_menu)
        header.addWidget(btn_back)
        header.addStretch()
        
        title = QLabel("Merge PDFs")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        instruction = QLabel("Drag & drop PDFs below or click Add. Drag items to reorder.")
        instruction.setStyleSheet("color: gray;")
        
        # PDF list with thumbnails and drag-to-reorder
        self.pdf_list = PDFListWidget()
        
        # Buttons
        btn_row = QHBoxLayout()
        btn_add = QPushButton("Add PDFs...")
        btn_add.clicked.connect(self.on_add_files)
        btn_clear = QPushButton("Clear All")
        btn_clear.clicked.connect(self.pdf_list.clear)
        btn_remove = QPushButton("Remove Selected")
        btn_remove.clicked.connect(self.on_remove_selected)
        
        btn_row.addWidget(btn_add)
        btn_row.addWidget(btn_clear)
        btn_row.addWidget(btn_remove)
        btn_row.addStretch()
        
        btn_merge = QPushButton("Merge to PDF...")
        btn_merge.setStyleSheet("font-size: 14px; padding: 10px;")
        btn_merge.clicked.connect(self.on_execute_merge)
        
        layout.addLayout(header)
        layout.addWidget(title)
        layout.addWidget(instruction)
        layout.addWidget(self.pdf_list)
        layout.addLayout(btn_row)
        layout.addWidget(btn_merge)
        
    def on_add_files(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select PDF files to merge", "", "PDF files (*.pdf)"
        )
        for path in files:
            self.pdf_list.add_pdf(path)
            
    def on_remove_selected(self) -> None:
        for item in self.pdf_list.selectedItems():
            self.pdf_list.takeItem(self.pdf_list.row(item))
            
    def on_execute_merge(self) -> None:
        paths = self.pdf_list.get_all_paths()
        if not paths:
            show_error_dialog(self, "No files", "Please add at least one PDF to merge.")
            return
            
        output_path, _ = QFileDialog.getSaveFileName(
            self, "Save merged PDF as...", "merged.pdf", "PDF files (*.pdf)"
        )
        if not output_path:
            return
            
        try:
            PdfEngine.merge_pdfs(paths, output_path)
            show_info_dialog(self, "Success", f"Merged PDF saved to:\n{output_path}")
            self.pdf_list.clear()
        except Exception as exc:
            show_error_dialog(self, "Merge failed", str(exc))


class SplitPage(QWidget):
    """Page for splitting PDFs with preview."""
    
    def __init__(self, main_window: MainWindow, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.main_window = main_window
        self.source_path: Optional[str] = None
        self._build_ui()
        
    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        btn_back = QPushButton("← Back to Menu")
        btn_back.clicked.connect(self.main_window.show_menu)
        header.addWidget(btn_back)
        header.addStretch()
        
        title = QLabel("Split PDF")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        # File selector with preview
        file_group = QGroupBox("Select PDF File")
        file_layout = QVBoxLayout(file_group)
        
        select_row = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        btn_select = QPushButton("Select PDF...")
        btn_select.clicked.connect(self.on_select_file)
        select_row.addWidget(self.file_label, stretch=1)
        select_row.addWidget(btn_select)
        
        self.preview_scroll = QScrollArea()
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setMinimumHeight(200)
        self.preview_container = QWidget()
        self.preview_layout = QHBoxLayout(self.preview_container)
        self.preview_scroll.setWidget(self.preview_container)
        
        file_layout.addLayout(select_row)
        file_layout.addWidget(QLabel("Preview (first 10 pages):"))
        file_layout.addWidget(self.preview_scroll)
        
        # Page range
        range_group = QGroupBox("Page Range")
        range_layout = QFormLayout(range_group)
        
        self.start_edit = QLineEdit()
        self.start_edit.setPlaceholderText("e.g., 1")
        self.start_edit.setMaximumWidth(100)
        
        self.end_edit = QLineEdit()
        self.end_edit.setPlaceholderText("e.g., 5")
        self.end_edit.setMaximumWidth(100)
        
        range_layout.addRow("Start page:", self.start_edit)
        range_layout.addRow("End page:", self.end_edit)
        
        btn_split = QPushButton("Split to PDF...")
        btn_split.setStyleSheet("font-size: 14px; padding: 10px;")
        btn_split.clicked.connect(self.on_execute_split)
        
        layout.addLayout(header)
        layout.addWidget(title)
        layout.addWidget(file_group)
        layout.addWidget(range_group)
        layout.addWidget(btn_split)
        layout.addStretch()
        
    def on_select_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select a PDF to split", "", "PDF files (*.pdf)"
        )
        if not file_path:
            return
            
        self.source_path = file_path
        self.file_label.setText(os.path.basename(file_path))
        self._load_preview(file_path)
        
    def _load_preview(self, pdf_path: str) -> None:
        """Load thumbnail previews of first 10 pages."""
        # Clear existing previews
        while self.preview_layout.count():
            child = self.preview_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        try:
            doc = fitz.open(pdf_path)
            max_pages = min(10, doc.page_count)
            
            for page_num in range(max_pages):
                page = doc[page_num]
                pix = page.get_pixmap(matrix=fitz.Matrix(0.3, 0.3))
                
                img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(img)
                
                page_widget = QWidget()
                page_layout = QVBoxLayout(page_widget)
                page_layout.setContentsMargins(5, 5, 5, 5)
                
                thumb_label = QLabel()
                thumb_label.setPixmap(pixmap)
                thumb_label.setStyleSheet("border: 1px solid #ccc;")
                
                num_label = QLabel(f"Page {page_num + 1}")
                num_label.setAlignment(Qt.AlignCenter)
                num_label.setStyleSheet("font-size: 10px;")
                
                page_layout.addWidget(thumb_label)
                page_layout.addWidget(num_label)
                
                self.preview_layout.addWidget(page_widget)
                
            self.preview_layout.addStretch()
            doc.close()
        except Exception as e:
            show_error_dialog(self, "Preview failed", f"Could not load preview: {e}")
            
    def on_execute_split(self) -> None:
        if not self.source_path:
            show_error_dialog(self, "No source file", "Please select a PDF to split.")
            return
            
        try:
            start_page = int(self.start_edit.text().strip())
            end_page = int(self.end_edit.text().strip())
        except ValueError:
            show_error_dialog(self, "Invalid input", "Start and end pages must be numbers.")
            return
            
        output_path, _ = QFileDialog.getSaveFileName(
            self, "Save split PDF as...", "split.pdf", "PDF files (*.pdf)"
        )
        if not output_path:
            return
            
        try:
            PdfEngine.split_pdf(self.source_path, start_page, end_page, output_path)
            show_info_dialog(self, "Success", f"Split PDF saved to:\n{output_path}")
        except Exception as exc:
            show_error_dialog(self, "Split failed", str(exc))


class ConvertPage(QWidget):
    """Page for converting PDF to DOCX."""
    
    def __init__(self, main_window: MainWindow, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.main_window = main_window
        self.source_path: Optional[str] = None
        self._build_ui()
        
    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        btn_back = QPushButton("← Back to Menu")
        btn_back.clicked.connect(self.main_window.show_menu)
        header.addWidget(btn_back)
        header.addStretch()
        
        title = QLabel("Convert PDF to DOCX")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        # File selector
        file_group = QGroupBox("Select PDF File")
        file_layout = QHBoxLayout(file_group)
        
        self.file_label = QLabel("No file selected")
        btn_select = QPushButton("Select PDF...")
        btn_select.clicked.connect(self.on_select_file)
        
        file_layout.addWidget(self.file_label, stretch=1)
        file_layout.addWidget(btn_select)
        
        btn_convert = QPushButton("Convert to DOCX...")
        btn_convert.setStyleSheet("font-size: 14px; padding: 10px;")
        btn_convert.clicked.connect(self.on_execute_convert)
        
        layout.addLayout(header)
        layout.addWidget(title)
        layout.addWidget(file_group)
        layout.addWidget(btn_convert)
        layout.addStretch()
        
    def on_select_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select a PDF to convert", "", "PDF files (*.pdf)"
        )
        if not file_path:
            return
            
        self.source_path = file_path
        self.file_label.setText(file_path)
        
    def on_execute_convert(self) -> None:
        if not self.source_path:
            show_error_dialog(self, "No source file", "Please select a PDF to convert.")
            return
            
        output_path, _ = QFileDialog.getSaveFileName(
            self, "Save DOCX as...", "output.docx", "Word files (*.docx)"
        )
        if not output_path:
            return
            
        try:
            PdfEngine.pdf_to_docx(self.source_path, output_path)
            show_info_dialog(self, "Success", f"DOCX file saved to:\n{output_path}")
        except Exception as exc:
            show_error_dialog(self, "Conversion failed", str(exc))


class PDFListWidget(QListWidget):
    """Custom list widget with PDF thumbnails and drag-to-reorder."""
class PDFListWidget(QListWidget):
    """Custom list widget with PDF thumbnails and drag-to-reorder."""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.InternalMove)  # Enable drag-to-reorder
        self.setSelectionMode(QListWidget.ExtendedSelection)
        self.setIconSize(QSize(100, 100))
        self.setSpacing(5)
        
    def add_pdf(self, file_path: str) -> None:
        """Add a PDF with thumbnail preview."""
        try:
            # Generate thumbnail
            doc = fitz.open(file_path)
            if doc.page_count > 0:
                page = doc[0]
                pix = page.get_pixmap(matrix=fitz.Matrix(0.2, 0.2))
                
                img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(img)
                
                # Create list item
                item = QListWidgetItem()
                item.setIcon(pixmap)
                item.setText(f"{os.path.basename(file_path)}\n{file_path}")
                item.setData(Qt.UserRole, file_path)  # Store full path
                
                self.addItem(item)
            doc.close()
        except Exception as e:
            # Fallback: add without thumbnail
            item = QListWidgetItem()
            item.setText(f"{os.path.basename(file_path)}\n{file_path}")
            item.setData(Qt.UserRole, file_path)
            self.addItem(item)
            
    def get_all_paths(self) -> List[str]:
        """Get all PDF paths in current order."""
        paths = []
        for i in range(self.count()):
            item = self.item(i)
            if item:
                path = item.data(Qt.UserRole)
                if path:
                    paths.append(path)
        return paths
        
    def dragEnterEvent(self, event) -> None:
        """Accept file drops or internal moves."""
        if event.mimeData().hasUrls() or event.source() == self:
            event.acceptProposedAction()
        else:
            event.ignore()
            
    def dragMoveEvent(self, event) -> None:
        """Accept drag moves."""
        if event.mimeData().hasUrls() or event.source() == self:
            event.acceptProposedAction()
        else:
            event.ignore()
            
    def dropEvent(self, event) -> None:
        """Handle external file drops."""
        if event.mimeData().hasUrls():
            # External file drop
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.lower().endswith('.pdf'):
                    self.add_pdf(file_path)
            event.acceptProposedAction()
        elif event.source() == self:
            # Internal reorder
            super().dropEvent(event)
        else:
            event.ignore()
