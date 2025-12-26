# PDF Tool

A lightweight desktop utility for managing PDF files with an intuitive menu-driven interface.

![PDF Tool Screenshot](app/pdf_tool.png)

## Features

- **Merge PDFs** - Combine multiple PDF files with drag & drop support and thumbnail previews
- **Split PDF** - Extract page ranges with visual page previews
- **Convert to DOCX** - Transform PDF files to Word documents
- **Drag to Reorder** - Rearrange PDFs in merge list by dragging
- **PDF Previews** - See thumbnail previews before processing
- **Menu-driven UI** - Clean, focused interface for each operation
- Native desktop UI (PySide6 / Qt)
- Portable Windows executable available

## Download

**[Download Windows Executable](https://github.com/JustinCarter-429/Free-pdf-editor/releases)** - No installation required!

## Tech Stack

- Python 3.x
- [PyMuPDF](https://pymupdf.readthedocs.io/) for PDF manipulation and thumbnail generation
- [pdf2docx](https://github.com/ArtifexSoftware/pdf2docx) for PDF to DOCX conversion
- [PySide6](https://doc.qt.io/qtforpython/) for the GUI
- [PyInstaller](https://pyinstaller.org/) for packaging

## Installation (From Source)

1. Clone the repository:
   ```bash
   git clone https://github.com/JustinCarter-429/Free-pdf-editor.git
   cd Free-pdf-editor
   ```

2. Install dependencies:
   ```bash
   pip install -r app/requirements.txt
   ```

3. Run the application:
   ```bash
   python app/main.py
   ```

## Usage

1. Launch the application
2. Choose an operation from the main menu:
   - **Merge PDFs**: Add multiple PDFs, drag to reorder, then merge
   - **Split PDF**: Select a PDF, choose page range, then split
   - **Convert to DOCX**: Select a PDF and convert to Word format

## Building Executable

To build your own Windows executable:

```bash
cd app
python -m PyInstaller --onefile --windowed --name "PDFTool" main.py
```

The executable will be in `app/dist/PDFTool.exe`

## Developer

**Justin Carter**
- Email: Justincarter429@gmail.com
- School: University of Utah

## License

Free to use and modify.
