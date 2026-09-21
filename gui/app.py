from PySide6.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout
from gui.split_tab import SplitTab
from gui.merge_tab import MergeTab
from gui.convert_tab import ConvertTab

class PDFToolApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Tool")
        self.resize(800, 600)
        
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.split_tab = SplitTab()
        self.merge_tab = MergeTab()
        self.convert_tab = ConvertTab()
        
        self.tabs.addTab(self.split_tab, "Split PDF")
        self.tabs.addTab(self.merge_tab, "Merge PDFs")
        self.tabs.addTab(self.convert_tab, "Convert to Word")
