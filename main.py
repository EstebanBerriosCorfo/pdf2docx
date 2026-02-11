from __future__ import annotations

import argparse
from pathlib import Path
import sys

from processor import convert_pdf_to_docx
from scanner import scan_inputs
from writer import output_path_for


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert PDFs to Word (DOCX) files."
    )
    parser.add_argument(
        "input_path",
        type=Path,
        help="PDF file or directory containing PDFs",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Output DOCX file (single PDF) or output directory",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        scan = scan_inputs(args.input_path, args.output)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    failures: list[tuple[Path, str]] = []
    for pdf_path in scan.inputs:
        if scan.output_file is not None:
            docx_path = scan.output_file
        else:
            docx_path = output_path_for(pdf_path, scan.output_dir)

        try:
            convert_pdf_to_docx(pdf_path, docx_path)
            print(f"OK: {pdf_path.name} -> {docx_path}")
        except Exception as exc:
            message = str(exc)
            failures.append((pdf_path, message))
            print(f"FAIL: {pdf_path.name} ({message})", file=sys.stderr)

    if failures:
        print(
            f"Completed with {len(failures)} failure(s).",
            file=sys.stderr,
        )
        for pdf_path, message in failures:
            print(f"- {pdf_path.name}: {message}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
