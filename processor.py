from __future__ import annotations

from pathlib import Path

from pdf2docx import Converter


def convert_pdf_to_docx(pdf_path: Path, docx_path: Path) -> None:
    docx_path.parent.mkdir(parents=True, exist_ok=True)
    converter = Converter(str(pdf_path))
    try:
        converter.convert(str(docx_path))
    finally:
        converter.close()
