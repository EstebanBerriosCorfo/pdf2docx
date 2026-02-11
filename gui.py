from __future__ import annotations

import threading
import time
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image

from processor import convert_pdf_to_docx
from scanner import scan_inputs
from writer import output_path_for


class PdfToWordApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.title("PDF a Word")
        self.geometry("504x616")
        self.minsize(448, 568)

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.input_dir: Path | None = None
        self.input_path_var = tk.StringVar(value="Sin seleccionar")
        self.current_file_var = tk.StringVar(value="Archivo actual: -")
        self._start_time: float | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(pady=(20, 10))

        logo_path = (
            Path(__file__).resolve().parent
            / "assets"
            / "images"
            / "logo_corfo_azul.png"
        )
        logo_image = None
        if logo_path.exists():
            logo_image = ctk.CTkImage(
                light_image=Image.open(logo_path),
                dark_image=Image.open(logo_path),
                size=(64, 44),
            )

        logo_label = ctk.CTkLabel(
            header,
            text="",
            image=logo_image,
        )
        logo_label.pack(side="left", padx=(0, 12))

        title = ctk.CTkLabel(
            header,
            text="PDF a Word",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title.pack(side="left")

        pick_frame = ctk.CTkFrame(self)
        pick_frame.pack(fill="x", padx=20, pady=10)

        pick_button = ctk.CTkButton(
            pick_frame,
            text="Seleccionar carpeta",
            command=self.select_folder,
            width=126,
        )
        pick_button.pack(side="left", padx=10, pady=10)

        path_label = ctk.CTkLabel(
            pick_frame,
            textvariable=self.input_path_var,
            anchor="w",
            justify="left",
        )
        path_label.pack(side="left", fill="x", expand=True, padx=10)

        action_button = ctk.CTkButton(
            self,
            text="Generar Word",
            command=self.start_generation,
            height=28,
        )
        action_button.pack(pady=(10, 15))

        log_label = ctk.CTkLabel(self, text="Proceso")
        log_label.pack(anchor="w", padx=20)

        current_file_label = ctk.CTkLabel(
            self,
            textvariable=self.current_file_var,
            anchor="w",
        )
        current_file_label.pack(anchor="w", padx=20)

        self.progress_label = ctk.CTkLabel(self, text="Progreso: 0%")
        self.progress_label.pack(anchor="w", padx=20, pady=(0, 5))

        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 15))

        self.log_box = ctk.CTkTextbox(self, wrap="word")
        self.log_box.pack(fill="both", expand=True, padx=20, pady=(5, 20))
        self.log_box.configure(state="disabled")

        footer = ctk.CTkLabel(
            self,
            text=(
                "CORFO-2026 Subdirección de Operaciones y Mejora Continua | "
                "Comité Innova Chile"
            ),
            text_color="#6b6b6b",
        )
        footer.pack(pady=(0, 10))

    def select_folder(self) -> None:
        selected = filedialog.askdirectory()
        if selected:
            self.input_dir = Path(selected)
            self.input_path_var.set(str(self.input_dir))

    def start_generation(self) -> None:
        if not self.input_dir:
            messagebox.showerror(
                "Falta carpeta",
                "Selecciona la carpeta de entrada con PDFs.",
            )
            return

        self._append_log("Iniciando proceso...")
        self._append_log("------")
        thread = threading.Thread(
            target=self._run_generation,
            daemon=True,
        )
        thread.start()

    def _run_generation(self) -> None:
        try:
            scan = scan_inputs(self.input_dir, None)
        except Exception as exc:
            self._append_log(f"Error: {exc}")
            self._show_error("Error de entrada", str(exc))
            return

        failures: list[tuple[Path, str]] = []
        total = len(scan.inputs)
        processed = 0
        self._start_time = time.monotonic()
        self._update_progress(processed, total)
        for pdf_path in scan.inputs:
            docx_path = output_path_for(pdf_path, scan.output_dir)
            self._set_current_file(pdf_path.name)
            self._append_log(f"Procesando: {pdf_path.name}")
            try:
                convert_pdf_to_docx(pdf_path, docx_path)
                self._append_log(
                    f"Generado: {docx_path.name}"
                )
            except Exception as exc:
                message = str(exc)
                failures.append((pdf_path, message))
                self._append_log(
                    f"FALLO: {pdf_path.name} ({message})"
                )
            finally:
                processed += 1
                self._update_progress(processed, total)
                self._append_log("------")

        if failures:
            self._append_log(
                f"Proceso terminado con {len(failures)} fallas."
            )
            first = failures[0]
            self._show_error(
                "Proceso con fallas",
                f"Falló: {first[0].name}\n{first[1]}",
            )
        else:
            self._append_log("Proceso exitoso.")
            self._show_info("Proceso exitoso", "Documentos generados.")

        # Mantener el progreso final visible al terminar.

    def _append_log(self, text: str) -> None:
        def _write() -> None:
            self.log_box.configure(state="normal")
            self.log_box.insert("end", text + "\n")
            self.log_box.see("end")
            self.log_box.configure(state="disabled")

        self.after(0, _write)

    def _update_progress(
        self,
        processed: int,
        total: int,
    ) -> None:
        def _write() -> None:
            if total <= 0:
                percent = 0
            else:
                percent = int((processed / total) * 100)
            eta = self._estimate_eta(processed, total)
            eta_text = f" | ETA: {eta}" if eta else ""
            self.progress_label.configure(
                text=f"Progreso: {percent}% ({processed}/{total}){eta_text}"
            )
            self.progress_bar.set(
                0 if total <= 0 else processed / total
            )

        self.after(0, _write)

    def _set_current_file(self, name: str) -> None:
        self.after(0, lambda: self.current_file_var.set(
            f"Archivo actual: {name}"
        ))

    def _estimate_eta(
        self,
        processed: int,
        total: int,
    ) -> str | None:
        if self._start_time is None:
            return None
        elapsed = time.monotonic() - self._start_time
        if processed <= 0 or total <= 0:
            return None
        avg = elapsed / processed
        remaining = max(0.0, avg * (total - processed))
        return self._format_seconds(remaining)

    @staticmethod
    def _format_seconds(seconds: float) -> str:
        total = int(round(seconds))
        minutes, secs = divmod(total, 60)
        if minutes >= 60:
            hours, minutes = divmod(minutes, 60)
            return f"{hours:d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:d}:{secs:02d}"

    def _show_error(self, title: str, message: str) -> None:
        self.after(0, lambda: messagebox.showerror(title, message))

    def _show_info(self, title: str, message: str) -> None:
        self.after(0, lambda: messagebox.showinfo(title, message))


def main() -> int:
    app = PdfToWordApp()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
