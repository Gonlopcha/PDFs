import os
import traceback
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                               QPushButton, QFileDialog, QListWidget, QProgressBar, 
                               QMessageBox, QAbstractItemView, QComboBox)
from PySide6.QtCore import QThread, Signal
from core.excel_converter import convert_excel_batch
from core.system_monitor import procesar_excels_en_lotes, SystemMonitor

class ExcelConvertWorker(QThread):
    progress = Signal(float, int)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, excel_list, output_dir, orientation):
        super().__init__()
        self.excel_list = excel_list
        self.output_dir = output_dir
        self.orientation = orientation

    def run(self):
        try:
            self.total_converted = 0
            total_archivos = len(self.excel_list)
            
            def funcion_calculo(lote):
                # Callback detallado por cada archivo convertido dentro del lote actual
                def lote_callback(current_in_batch, total_in_batch):
                    self.progress.emit(self.total_converted + current_in_batch, total_archivos)
                    
                resultados = convert_excel_batch(lote, self.output_dir, self.orientation, callback=lote_callback)
                self.total_converted += len(lote)
                return resultados

            def batch_progress(procesados, total, mensaje):
                # Actualizaciones generales (inicio/fin de lote) del system monitor
                self.progress.emit(procesados, total)
                
            procesar_excels_en_lotes(self.excel_list, funcion_calculo, progress_callback=batch_progress)
            self.finished.emit("Archivos de Excel convertidos exitosamente (usando lotes de memoria).")
        except Exception as e:
            self.error.emit(f"{str(e)}\n\nTraceback:\n{traceback.format_exc()}")

class ExcelConvertTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # List of Excels
        h_layout_list = QHBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        h_layout_list.addWidget(self.list_widget)

        # Buttons for list
        v_layout_btns = QVBoxLayout()
        self.add_btn = QPushButton("Añadir Excels")
        self.add_btn.clicked.connect(self.add_excels)
        self.remove_btn = QPushButton("Eliminar Seleccionados")
        self.remove_btn.clicked.connect(self.remove_excels)
        
        v_layout_btns.addWidget(self.add_btn)
        v_layout_btns.addWidget(self.remove_btn)
        v_layout_btns.addStretch()
        h_layout_list.addLayout(v_layout_btns)
        
        layout.addLayout(h_layout_list)

        # Orientation
        h_layout_orient = QHBoxLayout()
        self.orient_label = QLabel("Orientación:")
        self.orient_combo = QComboBox()
        self.orient_combo.addItems(["Vertical", "Horizontal"])
        h_layout_orient.addWidget(self.orient_label)
        h_layout_orient.addWidget(self.orient_combo)
        h_layout_orient.addStretch()
        layout.addLayout(h_layout_orient)

        # Output Dir
        h_layout_out = QHBoxLayout()
        self.output_label = QLabel("Directorio de Salida:")
        self.output_edit = QLineEdit()
        self.output_btn = QPushButton("Buscar")
        self.output_btn.clicked.connect(self.browse_output)
        h_layout_out.addWidget(self.output_label)
        h_layout_out.addWidget(self.output_edit)
        h_layout_out.addWidget(self.output_btn)
        layout.addLayout(h_layout_out)

        # Run Button
        self.run_btn = QPushButton("Convertir Excel a PDF")
        self.run_btn.clicked.connect(self.run_convert)
        layout.addWidget(self.run_btn)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

    def add_excels(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Seleccionar Excels", "", "Excel Files (*.xlsx *.xls)")
        if files:
            self.list_widget.addItems(files)

    def remove_excels(self):
        for item in self.list_widget.selectedItems():
            self.list_widget.takeItem(self.list_widget.row(item))

    def browse_output(self):
        dir = QFileDialog.getExistingDirectory(self, "Seleccionar Directorio de Salida")
        if dir:
            self.output_edit.setText(dir)

    def run_convert(self):
        excel_list = [self.list_widget.item(i).text() for i in range(self.list_widget.count())]
        output_dir = self.output_edit.text()
        orientation = self.orient_combo.currentText()

        if not excel_list or not output_dir:
            QMessageBox.warning(self, "Advertencia", "Por favor añada archivos Excel y especifique el directorio de salida.")
            return

        # Verificar memoria antes de empezar para advertir si está muy baja
        SystemMonitor.check_and_warn(self)

        self.run_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        
        self.worker = ExcelConvertWorker(excel_list, output_dir, orientation)
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
