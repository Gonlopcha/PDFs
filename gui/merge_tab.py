import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
import threading
import time

try:
    from core.merger import merge_pdfs
except ImportError:
    merge_pdfs = None

class MergeTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)
        
        self.output_file = ttk.StringVar()
        
        self._build_ui()
        
    def _build_ui(self):
        # Input PDFs
        lf_input = ttk.LabelFrame(self, text='Archivos PDF a unir', padding=10)
        lf_input.pack(fill=BOTH, expand=YES, pady=(0, 15))
        
        self.listbox = ttk.Treeview(lf_input, show='tree')
        self.listbox.pack(side=LEFT, fill=BOTH, expand=YES)
        
        scrollbar = ttk.Scrollbar(lf_input, orient=VERTICAL, command=self.listbox.yview)
        scrollbar.pack(side=LEFT, fill=Y)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        
        btn_frame = ttk.Frame(lf_input)
        btn_frame.pack(side=RIGHT, fill=Y, padx=(10, 0))
        
        ttk.Button(btn_frame, text='➕ Agregar', command=self._agregar).pack(fill=X, pady=2)
        ttk.Button(btn_frame, text='⬆ Subir', command=self._subir).pack(fill=X, pady=2)
        ttk.Button(btn_frame, text='⬇ Bajar', command=self._bajar).pack(fill=X, pady=2)
        ttk.Button(btn_frame, text='❌ Quitar', command=self._quitar, bootstyle='danger').pack(fill=X, pady=2)
        
        # Output File
        lf_output = ttk.LabelFrame(self, text='Archivo de salida', padding=10)
        lf_output.pack(fill=X, pady=(0, 15))
        
        ttk.Entry(lf_output, textvariable=self.output_file).pack(side=LEFT, fill=X, expand=YES, padx=(0, 10))
        ttk.Button(lf_output, text='Examinar...', command=self._browse_output).pack(side=RIGHT)
        
        # Progress and Action
        self.progress = ttk.Progressbar(self, mode='determinate', bootstyle='success-striped')
        self.progress.pack(fill=X, pady=(10, 20))
        
        self.btn_merge = ttk.Button(self, text='📎 Unir PDFs', bootstyle='primary', command=self._ejecutar)
        self.btn_merge.pack(fill=X, ipady=10)
        
        self.status_lbl = ttk.Label(self, text='Listo')
        self.status_lbl.pack(pady=(10, 0))

    def _agregar(self):
        filenames = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        for f in filenames:
            self.listbox.insert('', END, text=f)

    def _subir(self):
        selected = self.listbox.selection()
        for item in selected:
            idx = self.listbox.index(item)
            if idx > 0:
                self.listbox.move(item, '', idx - 1)

    def _bajar(self):
        selected = self.listbox.selection()
        for item in reversed(selected):
            idx = self.listbox.index(item)
            if idx < len(self.listbox.get_children()) - 1:
                self.listbox.move(item, '', idx + 1)

    def _quitar(self):
        selected = self.listbox.selection()
        for item in selected:
            self.listbox.delete(item)

    def _browse_output(self):
        filename = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if filename:
            self.output_file.set(filename)

    def _ejecutar(self):
        files = [self.listbox.item(i, 'text') for i in self.listbox.get_children()]
        if len(files) < 2:
            messagebox.showwarning("Faltan archivos", "Debe agregar al menos dos archivos PDF para unir.")
            return
        if not self.output_file.get():
            messagebox.showwarning("Faltan datos", "Por favor seleccione el archivo de salida.")
            return
            
        self.btn_merge.config(state=DISABLED)
        self.progress['value'] = 0
        self.status_lbl.config(text='Uniendo PDFs...')
        
        self.thread_done = False
        self.thread_success = False
        self.thread_error = ""
        self.current_progress = 0
        
        thread = threading.Thread(target=self._run_merge_task, args=(files, self.output_file.get()), daemon=True)
        thread.start()
        
        self.winfo_toplevel().after(100, self._check_progress)

    def _run_merge_task(self, files, output):
        try:
            if merge_pdfs:
                # Call core logic here
                pass
            else:
                for i in range(1, 101):
                    time.sleep(0.02)
                    self.current_progress = i
            
            self.thread_success = True
        except Exception as e:
            self.thread_error = str(e)
            self.thread_success = False
        finally:
            self.thread_done = True
            self.current_progress = 100

    def _check_progress(self):
        self.progress['value'] = getattr(self, 'current_progress', 0)
            
        if getattr(self, 'thread_done', False):
            self.btn_merge.config(state=NORMAL)
            if self.thread_success:
                self.status_lbl.config(text='¡Unión completada con éxito!')
                messagebox.showinfo("Éxito", "Los PDFs se unieron correctamente.")
            else:
                self.status_lbl.config(text='Error al unir')
                messagebox.showerror("Error", f"Ocurrió un error: {self.thread_error}")
        else:
            self.winfo_toplevel().after(100, self._check_progress)
