import traceback
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                               QPushButton, QFileDialog, QProgressBar, 
                               QMessageBox, QRadioButton, QButtonGroup)
from PySide6.QtCore import QThread, Signal
from core.pdf_to_image import pdf_to_images

class PdfToImageWorker(QThread):
    progress = Signal(int, int)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, pdf_file, output_zip, mode):
        super().__init__()
        self.pdf_file = pdf_file
        self.output_zip = output_zip
        self.mode = mode

    def run(self):
        try:
            def callback(current, total):
                self.progress.emit(current, total)
                
            pdf_to_images(self.pdf_file, self.output_zip, mode=self.mode, callback=callback)
            self.finished.emit("Imágenes guardadas exitosamente en el archivo ZIP.")
        except Exception as e:
            self.error.emit(f"{str(e)}\n\nTraceback:\n{traceback.format_exc()}")

class PdfToImageTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Input File
        h_layout_in = QHBoxLayout()
        self.input_label = QLabel("Archivo PDF:")
        self.input_edit = QLineEdit()
        self.input_edit.setReadOnly(True)
        self.input_btn = QPushButton("Examinar")
        self.input_btn.clicked.connect(self.browse_input)
        h_layout_in.addWidget(self.input_label)
        h_layout_in.addWidget(self.input_edit)
        h_layout_in.addWidget(self.input_btn)
        layout.addLayout(h_layout_in)
        
        # Mode Selection
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Modo de Operación:")
        self.radio_pages = QRadioButton("Convertir Páginas a Imágenes")
        self.radio_extract = QRadioButton("Extraer Imágenes del PDF")
        self.radio_pages.setChecked(True)
        
        self.mode_group = QButtonGroup()
        self.mode_group.addButton(self.radio_pages)
        self.mode_group.addButton(self.radio_extract)
        
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.radio_pages)
        mode_layout.addWidget(self.radio_extract)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)

        # Output File
        h_layout_out = QHBoxLayout()
        self.output_label = QLabel("Archivo ZIP de Salida:")
        self.output_edit = QLineEdit()
        self.output_edit.setReadOnly(True)
        self.output_btn = QPushButton("Examinar")
        self.output_btn.clicked.connect(self.browse_output)
        h_layout_out.addWidget(self.output_label)
        h_layout_out.addWidget(self.output_edit)
        h_layout_out.addWidget(self.output_btn)
        layout.addLayout(h_layout_out)

        # Run Button
        self.run_btn = QPushButton("Procesar y Guardar en ZIP")
        self.run_btn.clicked.connect(self.run_process)
        layout.addWidget(self.run_btn)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        layout.addStretch()

    def browse_input(self):
        file, _ = QFileDialog.getOpenFileName(self, "Seleccionar PDF", "", "PDF Files (*.pdf)")
        if file:
            self.input_edit.setText(file)
            # Auto-fill output file based on input file if empty
            if not self.output_edit.text():
                import os
                base = os.path.splitext(file)[0]
                self.output_edit.setText(f"{base}_images.zip")

    def browse_output(self):
        file, _ = QFileDialog.getSaveFileName(self, "Guardar ZIP", "", "ZIP Files (*.zip)")
        if file:
            self.output_edit.setText(file)

    def run_process(self):
        pdf_file = self.input_edit.text()
        output_zip = self.output_edit.text()
        
        mode = "pages" if self.radio_pages.isChecked() else "extract"

        if not pdf_file or not output_zip:
            QMessageBox.warning(self, "Advertencia", "Por favor, seleccione el PDF de entrada y el archivo ZIP de salida.")
            return

        self.run_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        
        self.worker = PdfToImageWorker(pdf_file, output_zip, mode)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def update_progress(self, current, total):
        if total > 0:
            val = int((current / total) * 100)
            self.progress_bar.setValue(val)

    def on_finished(self, msg):
        self.progress_bar.setValue(100)
        QMessageBox.information(self, "Éxito", msg)
        self.run_btn.setEnabled(True)

    def on_error(self, err):
        self.progress_bar.setValue(0)
        self.run_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", f"Ocurrió un error:\n{err}")
