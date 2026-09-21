#!/usr/bin/env python3
"""PDF Tool - Herramienta para dividir, unir y convertir archivos PDF.

Punto de entrada principal de la aplicación.
"""

import sys


def main():
    """Iniciar la aplicación PDF Tool."""
    try:
        from gui.app import PDFToolApp
    except ImportError as e:
        print(f"Error: No se pudieron importar las dependencias necesarias.")
        print(f"Ejecuta: pip install -r requirements.txt")
        print(f"Detalle: {e}")
        sys.exit(1)

    app = PDFToolApp()
    app.run()


if __name__ == "__main__":
    main()
