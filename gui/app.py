import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from gui.split_tab import SplitTab
from gui.merge_tab import MergeTab
from gui.convert_tab import ConvertTab

class PDFToolApp(ttk.Window):
    def __init__(self):
        super().__init__(title='PDF Tool - Herramienta PDF', themename='cosmo', size=(750, 550), resizable=(True, True))
        self.minsize(650, 450)
        
        self.place_window_center()

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        self.split_tab = SplitTab(self.notebook)
        self.merge_tab = MergeTab(self.notebook)
        self.convert_tab = ConvertTab(self.notebook)

        self.notebook.add(self.split_tab, text='  ✂ Dividir  ')
        self.notebook.add(self.merge_tab, text='  📎 Unir  ')
        self.notebook.add(self.convert_tab, text='  📝 Convertir  ')

    def run(self):
        self.mainloop()
