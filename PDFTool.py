import sys
import warnings
# Ignore fitz warnings
warnings.filterwarnings("ignore", module="fitz")

from PySide6.QtWidgets import QApplication
from gui.app import PDFToolApp

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = PDFToolApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
