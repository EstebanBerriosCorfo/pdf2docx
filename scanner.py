from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List


@dataclass(frozen=True)
class ScanResult:
    inputs: List[Path]
    output_dir: Path
    output_file: Path | None


def scan_inputs(input_path: Path, output_path: Path | None) -> ScanResult:
    input_path = Path(input_path).resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input not found: {input_path}")

    download_root = Path.home() / "Downloads"
    dated_folder = datetime.now().strftime("%Y-%m-%d")
    default_output_dir = download_root / dated_folder

    if input_path.is_file():
        if input_path.suffix.lower() != ".pdf":
            raise ValueError("Input file must be a .pdf")

        output_file: Path | None = None
        if output_path is None:
            output_dir = default_output_dir
        else:
            output_path = Path(output_path)
            if output_path.suffix.lower() == ".docx":
                output_file = default_output_dir / output_path.name
                output_dir = default_output_dir
            else:
                output_dir = default_output_dir / output_path.name

        return ScanResult([input_path], output_dir, output_file)

    if input_path.is_dir():
        pdfs = sorted(
            p for p in input_path.iterdir()
            if p.is_file() and p.suffix.lower() == ".pdf"
        )
        if not pdfs:
            raise ValueError(f"No PDF files found in: {input_path}")

        if output_path is None:
            output_dir = default_output_dir
        else:
            output_dir = Path(output_path)
            if output_dir.suffix.lower() == ".docx":
                raise ValueError("For directories, output must be a folder.")
            output_dir = default_output_dir / output_dir.name

        return ScanResult(pdfs, output_dir, None)

    raise ValueError("Input path must be a file or directory")
