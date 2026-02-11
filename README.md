# pdf2docx

Sistema simple para convertir PDFs a documentos Word (DOCX).

## Requisitos

- Python 3.10+
- Dependencias: `pdf2docx`, `customtkinter`

## Instalacion

### Entorno virtual

```bash
python -m venv pdf_word
.\pdf_word\Scripts\activate
```

### Dependencias

```bash
pip install -r requirements.txt
```

## Uso

### Un archivo

```bash
python main.py .\\pdf\\archivo.pdf -o .\\output\\archivo.docx
```

### Carpeta completa

```bash
python main.py .\\pdf -o .\\output
```

La salida siempre se guarda en `Descargas` del usuario actual, dentro de una carpeta con la fecha del proceso (formato `YYYY-MM-DD`).  
Si se especifica `-o`:
- para un archivo, se usa el nombre del `.docx` pero se guarda en la carpeta de fecha;
- para una carpeta, se usa el nombre de la carpeta pero se crea dentro de la carpeta de fecha.

## Interfaz grafica

Instala dependencias y ejecuta:

```bash
python gui.py
```

La interfaz permite seleccionar una carpeta de entrada con PDFs, muestra la ruta elegida y ejecuta la generacion.  
Los resultados se guardan en `Descargas\\YYYY-MM-DD` del usuario actual.
