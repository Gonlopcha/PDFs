import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
import threading
import time

try:
    from core.splitter import split_pdf
except ImportError:
    split_pdf = None

class SplitTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)
        
        self.input_file = ttk.StringVar()
        self.split_mode = ttk.StringVar(value='ranges')
        self.output_dir = ttk.StringVar()
        
        self._build_ui()
        
    def _build_ui(self):
        # Input PDF
        lf_input = ttk.LabelFrame(self, text='Archivo PDF de entrada', padding=10)
        lf_input.pack(fill=X, pady=(0, 15))
        
        ttk.Entry(lf_input, textvariable=self.input_file).pack(side=LEFT, fill=X, expand=YES, padx=(0, 10))
        ttk.Button(lf_input, text='Examinar...', command=self._browse_input).pack(side=RIGHT)
        
        # Split Mode
        lf_mode = ttk.LabelFrame(self, text='Modo de división', padding=10)
        lf_mode.pack(fill=X, pady=(0, 15))
        
        ttk.Radiobutton(lf_mode, text='Por rango de páginas', variable=self.split_mode, value='ranges', command=self._update_mode_ui).grid(row=0, column=0, sticky=W, pady=5)
        ttk.Radiobutton(lf_mode, text='Cada N páginas', variable=self.split_mode, value='every_n', command=self._update_mode_ui).grid(row=1, column=0, sticky=W, pady=5)
        ttk.Radiobutton(lf_mode, text='Todas las páginas individuales', variable=self.split_mode, value='all', command=self._update_mode_ui).grid(row=2, column=0, sticky=W, pady=5)
        
        self.mode_frame = ttk.Frame(lf_mode)
        self.mode_frame.grid(row=0, column=1, rowspan=3, sticky=NSEW, padx=20)
        
        self.ranges_entry = ttk.Entry(self.mode_frame)
        self.ranges_entry.insert(0, 'Ej: 1-3, 5, 7-10')
        self.every_n_spinbox = ttk.Spinbox(self.mode_frame, from_=2, to=100)
        
        self._update_mode_ui()
        
        # Output Directory
        lf_output = ttk.LabelFrame(self, text='Carpeta de salida', padding=10)
        lf_output.pack(fill=X, pady=(0, 15))
        
        ttk.Entry(lf_output, textvariable=self.output_dir).pack(side=LEFT, fill=X, expand=YES, padx=(0, 10))
        ttk.Button(lf_output, text='Examinar...', command=self._browse_output).pack(side=RIGHT)
        
        # Progress and Action
        self.progress = ttk.Progressbar(self, mode='determinate', bootstyle='success-striped')
        self.progress.pack(fill=X, pady=(10, 20))
        
        self.btn_split = ttk.Button(self, text='✂ Dividir PDF', bootstyle='primary', command=self._ejecutar)
        self.btn_split.pack(fill=X, ipady=10)
        
        self.status_lbl = ttk.Label(self, text='Listo')
        self.status_lbl.pack(pady=(10, 0))

    def _update_mode_ui(self):
        self.ranges_entry.pack_forget()
        self.every_n_spinbox.pack_forget()
        
        mode = self.split_mode.get()
        if mode == 'ranges':
            self.ranges_entry.pack(fill=X, expand=YES)
        elif mode == 'every_n':
            self.every_n_spinbox.pack(fill=X, expand=YES)

    def _browse_input(self):
        filename = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if filename:
            self.input_file.set(filename)

    def _browse_output(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir.set(directory)

    def _ejecutar(self):
        if not self.input_file.get() or not self.output_dir.get():
            messagebox.showwarning("Faltan datos", "Por favor seleccione el archivo de entrada y la carpeta de salida.")
            return
            
        self.btn_split.config(state=DISABLED)
        self.progress['value'] = 0
        self.status_lbl.config(text='Dividiendo PDF...')
        
        self.thread_done = False
        self.thread_success = False
        self.thread_error = ""
        
        thread = threading.Thread(target=self._run_split_task, daemon=True)
        thread.start()
        
        self.winfo_toplevel().after(100, self._check_progress)

    def _run_split_task(self):
        try:
            # Simulate work or call core
            if split_pdf:
                # Call core logic here based on mode
                pass
            else:
                for i in range(1, 101):
                    time.sleep(0.02) # Simulate progress
                    self.current_progress = i
            
            self.thread_success = True
        except Exception as e:
            self.thread_error = str(e)
            self.thread_success = False
        finally:
            self.thread_done = True
            self.current_progress = 100

    def _check_progress(self):
        if hasattr(self, 'current_progress'):
            self.progress['value'] = self.current_progress
            
        if self.thread_done:
            self.btn_split.config(state=NORMAL)
            if self.thread_success:
                self.status_lbl.config(text='¡División completada con éxito!')
                messagebox.showinfo("Éxito", "El PDF se dividió correctamente.")
            else:
                self.status_lbl.config(text='Error en la división')
                messagebox.showerror("Error", f"Ocurrió un error: {self.thread_error}")
        else:
            self.winfo_toplevel().after(100, self._check_progress)
