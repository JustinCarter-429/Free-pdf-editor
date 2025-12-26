# app/pdf_engine.py

from __future__ import annotations

import os
from typing import List

import fitz  # PyMuPDF
from pdf2docx import Converter


class PdfEngine:
    """
    Core operations:
    merge_pdfs: merge multiple PDFs into one file
    split_pdf:  extract a range of pages to a new file
    I may add more optiopns in the future.
    This class is UI-agnostic: it does not import PySide6 or any GUI modules.
    """

    @staticmethod
    def merge_pdfs(input_files: List[str], output_path: str) -> None:
        """
        Merge multiple PDF files into a single PDF.
         input_files: list of paths to .pdf files
        param output_path: path to the output merged PDF
        raises ValueError: if input list is empty
        raises FileNotFoundError: if any input file does not exist
        raises RuntimeError: if saving fails
        """
        if not input_files:
            raise ValueError("there is no input files provided to merge.")

        merged = fitz.open()  # empty document to collect pages

        try:
            for path in input_files:
                if not os.path.exists(path):
                    raise FileNotFoundError(f"File not found: {path}")

                # Open each PDF and append its pages
                with fitz.open(path) as src:
                    merged.insert_pdf(src)

            # Ensure output directory exists
            output_dir = os.path.dirname(os.path.abspath(output_path)) or "."
            if not os.path.isdir(output_dir):
                raise FileNotFoundError(f"Output directory does not exist: {output_dir}")

            merged.save(output_path)

        except Exception as exc:
            # Wrap any unexpected error in a RuntimeError so the UI can show it cleanly
            raise RuntimeError(f"Failed to merge PDFs: {exc}") from exc

        finally:
            merged.close()

    @staticmethod
    def split_pdf(input_file: str, start_page: int, end_page: int, output_path: str) -> None:
        """
        Extract a page range from a PDF and save it as a new PDF.

        :param input_file: path to the source PDF
        :param start_page: first page in the range (1-based)
        :param end_page:   last page in the range (1-based, inclusive)
        :param output_path: path to the output PDF
        :raises FileNotFoundError: if the input file does not exist
        :raises ValueError: if page range is invalid
        :raises RuntimeError: if saving fails
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Source file not found: {input_file}")

        try:
            with fitz.open(input_file) as src:
                total_pages = src.page_count  # total # of pages in PDF

                # Validate the page range
                if start_page < 1 or end_page < 1:
                    raise ValueError("Page numbers must be >= 1.")
                if start_page > end_page:
                    raise ValueError("Start page cannot be greater than end page.")
                if end_page > total_pages:
                    raise ValueError(
                        f"End page {end_page} exceeds document page count {total_pages}."
                    )

                # Create a new empty PDF and insert the requested pages
                new_doc = fitz.open()
                try:
                    new_doc.insert_pdf(
                        src,
                        from_page=start_page - 1,  # PyMuPDF is 0-based
                        to_page=end_page - 1,
                    )

                    output_dir = os.path.dirname(os.path.abspath(output_path)) or "."
                    if not os.path.isdir(output_dir):
                        raise FileNotFoundError(
                            f"Output directory does not exist: {output_dir}"
                        )

                    new_doc.save(output_path)
                finally:
                    new_doc.close()

        except Exception as exc:
            raise RuntimeError(f"Failed to split PDF: {exc}") from exc

    @staticmethod
    def pdf_to_docx(input_file: str, output_path: str) -> None:
        """
        Convert a PDF file to DOCX format.

        :param input_file: path to the source PDF
        :param output_path: path to the output DOCX file
        :raises FileNotFoundError: if the input file does not exist
        :raises RuntimeError: if conversion fails
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Source file not found: {input_file}")

        try:
            # Ensure output directory exists
            output_dir = os.path.dirname(os.path.abspath(output_path)) or "."
            if not os.path.isdir(output_dir):
                raise FileNotFoundError(
                    f"Output directory does not exist: {output_dir}"
                )

            # Convert PDF to DOCX
            cv = Converter(input_file)
            cv.convert(output_path)  # all pages by default
            cv.close()

        except Exception as exc:
            raise RuntimeError(f"Failed to convert PDF to DOCX: {exc}") from exc
