from __future__ import annotations

from pathlib import Path


def output_path_for(input_pdf: Path, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / f"{input_pdf.stem}.docx"
