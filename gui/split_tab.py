"""Pestaña de división de PDF."""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
import threading

from core.splitter import split_by_ranges, split_every_n, split_all


class SplitTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)

        self.input_file = ttk.StringVar()
        self.split_mode = ttk.StringVar(value='ranges')
        self.output_dir = ttk.StringVar()

        # Variables de progreso compartidas con el hilo
        self.current_progress = 0
        self.total_steps = 1
        self.thread_done = False
        self.thread_success = False
        self.thread_error = ""
        self.result_files = []

        self._build_ui()

    def _build_ui(self):
        # Archivo PDF de entrada
        lf_input = ttk.LabelFrame(self, text='Archivo PDF de entrada', padding=10)
        lf_input.pack(fill=X, pady=(0, 15))

        ttk.Entry(lf_input, textvariable=self.input_file).pack(side=LEFT, fill=X, expand=YES, padx=(0, 10))
        ttk.Button(lf_input, text='Examinar...', command=self._browse_input).pack(side=RIGHT)

        # Modo de división
        lf_mode = ttk.LabelFrame(self, text='Modo de división', padding=10)
        lf_mode.pack(fill=X, pady=(0, 15))

        ttk.Radiobutton(lf_mode, text='Por rango de páginas', variable=self.split_mode,
                         value='ranges', command=self._update_mode_ui).grid(row=0, column=0, sticky=W, pady=5)
        ttk.Radiobutton(lf_mode, text='Cada N páginas', variable=self.split_mode,
                         value='every_n', command=self._update_mode_ui).grid(row=1, column=0, sticky=W, pady=5)
        ttk.Radiobutton(lf_mode, text='Todas las páginas individuales', variable=self.split_mode,
                         value='all', command=self._update_mode_ui).grid(row=2, column=0, sticky=W, pady=5)

        self.mode_frame = ttk.Frame(lf_mode)
        self.mode_frame.grid(row=0, column=1, rowspan=3, sticky=NSEW, padx=20)

        self.ranges_entry = ttk.Entry(self.mode_frame)
        self.ranges_entry.insert(0, 'Ej: 1-3, 5, 7-10')
        self.ranges_entry.bind('<FocusIn>', self._clear_placeholder)

        self.every_n_spinbox = ttk.Spinbox(self.mode_frame, from_=2, to=100, width=10)
        self.every_n_spinbox.set(2)

        self._update_mode_ui()

        # Carpeta de salida
        lf_output = ttk.LabelFrame(self, text='Carpeta de salida', padding=10)
        lf_output.pack(fill=X, pady=(0, 15))

        ttk.Entry(lf_output, textvariable=self.output_dir).pack(side=LEFT, fill=X, expand=YES, padx=(0, 10))
        ttk.Button(lf_output, text='Examinar...', command=self._browse_output).pack(side=RIGHT)

        # Barra de progreso
        self.progress = ttk.Progressbar(self, mode='determinate', bootstyle='success-striped')
        self.progress.pack(fill=X, pady=(10, 20))

        # Botón ejecutar
        self.btn_split = ttk.Button(self, text='✂ Dividir PDF', bootstyle='primary', command=self._ejecutar)
        self.btn_split.pack(fill=X, ipady=10)

        # Estado
        self.status_lbl = ttk.Label(self, text='Listo')
        self.status_lbl.pack(pady=(10, 0))

    def _clear_placeholder(self, event):
        """Limpia el texto de placeholder cuando el usuario hace clic."""
        if self.ranges_entry.get() == 'Ej: 1-3, 5, 7-10':
            self.ranges_entry.delete(0, END)

    def _update_mode_ui(self):
        self.ranges_entry.pack_forget()
        self.every_n_spinbox.pack_forget()

        mode = self.split_mode.get()
        if mode == 'ranges':
            self.ranges_entry.pack(fill=X, expand=YES)
        elif mode == 'every_n':
            self.every_n_spinbox.pack(fill=X, expand=YES)

    def _browse_input(self):
        filename = filedialog.askopenfilename(filetypes=[("Archivos PDF", "*.pdf")])
        if filename:
            self.input_file.set(filename)

    def _browse_output(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir.set(directory)

    def _ejecutar(self):
        """Valida las entradas y lanza la operación de división en un hilo."""
        input_path = self.input_file.get().strip()
        output_dir = self.output_dir.get().strip()

        if not input_path:
            messagebox.showwarning("Faltan datos", "Por favor seleccione el archivo PDF de entrada.")
            return
        if not output_dir:
            messagebox.showwarning("Faltan datos", "Por favor seleccione la carpeta de salida.")
            return

        mode = self.split_mode.get()
        if mode == 'ranges':
            range_text = self.ranges_entry.get().strip()
            if not range_text or range_text == 'Ej: 1-3, 5, 7-10':
                messagebox.showwarning("Faltan datos", "Por favor ingrese los rangos de páginas.")
                return
        elif mode == 'every_n':
            try:
                n_val = int(self.every_n_spinbox.get())
                if n_val < 1:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Valor inválido", "Ingrese un número válido mayor a 0.")
                return

        # Preparar estado
        self.btn_split.config(state=DISABLED)
        self.progress['value'] = 0
        self.current_progress = 0
        self.total_steps = 1
        self.thread_done = False
        self.thread_success = False
        self.thread_error = ""
        self.result_files = []
        self.status_lbl.config(text='Dividiendo PDF...')

        thread = threading.Thread(target=self._run_split_task, daemon=True)
        thread.start()

        self.winfo_toplevel().after(100, self._check_progress)

    def _progress_callback(self, current, total):
        """Callback que el hilo invoca para reportar progreso."""
        self.current_progress = current
        self.total_steps = total

    def _run_split_task(self):
        """Ejecuta la división real del PDF en un hilo secundario."""
        try:
            input_path = self.input_file.get().strip()
            output_dir = self.output_dir.get().strip()
            mode = self.split_mode.get()

            if mode == 'ranges':
                range_text = self.ranges_entry.get().strip()
                self.result_files = split_by_ranges(
                    input_path, range_text, output_dir, callback=self._progress_callback
                )
            elif mode == 'every_n':
                n_val = int(self.every_n_spinbox.get())
                self.result_files = split_every_n(
                    input_path, n_val, output_dir, callback=self._progress_callback
                )
            elif mode == 'all':
                self.result_files = split_all(
                    input_path, output_dir, callback=self._progress_callback
                )

            self.thread_success = True
        except Exception as e:
            self.thread_error = str(e)
            self.thread_success = False
        finally:
            self.thread_done = True

    def _check_progress(self):
        """Polling desde el hilo principal para actualizar la barra de progreso."""
        if self.total_steps > 0:
            pct = int((self.current_progress / self.total_steps) * 100)
            self.progress['value'] = pct

        if self.thread_done:
            self.progress['value'] = 100
            self.btn_split.config(state=NORMAL)
            if self.thread_success:
                n = len(self.result_files)
                self.status_lbl.config(text=f'¡División completada! {n} archivo(s) generado(s).')
                messagebox.showinfo(
                    "Éxito",
                    f"El PDF se dividió correctamente.\n\n"
                    f"Se generaron {n} archivo(s) en:\n{self.output_dir.get()}"
                )
            else:
                self.status_lbl.config(text='Error en la división')
                messagebox.showerror("Error", f"Ocurrió un error:\n{self.thread_error}")
        else:
            self.winfo_toplevel().after(100, self._check_progress)
