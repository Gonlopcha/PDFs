import os
import sys
from PySide6.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout
from PySide6.QtGui import QIcon
from gui.split_tab import SplitTab
from gui.merge_tab import MergeTab
from gui.convert_tab import ConvertTab
from gui.excel_convert_tab import ExcelConvertTab
from gui.image_to_pdf_tab import ImageToPdfTab
from gui.pdf_to_image_tab import PdfToImageTab

def _find_icon():
    """Busca el icono en varias ubicaciones (desarrollo y compilado)."""
    # Directorio base del ejecutable o del script
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    candidates = [
        os.path.join(base, "icono.ico"),
        os.path.join(base, "assets", "icono.ico"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


class PDFToolApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Tool - Herramienta PDF")
        self.resize(800, 600)
        
        # Icono de la ventana y barra de tareas
        icon_path = _find_icon()
        if icon_path:
            self.setWindowIcon(QIcon(icon_path))
        
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.split_tab = SplitTab()
        self.merge_tab = MergeTab()
        self.convert_tab = ConvertTab()
        self.excel_convert_tab = ExcelConvertTab()
        self.image_to_pdf_tab = ImageToPdfTab()
        self.pdf_to_image_tab = PdfToImageTab()
        
        self.tabs.addTab(self.split_tab, "Split PDF")
        self.tabs.addTab(self.merge_tab, "Merge PDFs")
        self.tabs.addTab(self.convert_tab, "Convert to Word")
        self.tabs.addTab(self.excel_convert_tab, "Excel to PDF")
        self.tabs.addTab(self.image_to_pdf_tab, "Images to PDF")
        self.tabs.addTab(self.pdf_to_image_tab, "PDF to Images")
