import traceback
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                               QPushButton, QFileDialog, QListWidget, QProgressBar, 
                               QMessageBox, QAbstractItemView)
from PySide6.QtCore import QThread, Signal
from core.image_to_pdf import images_to_pdf

class ImageToPdfWorker(QThread):
    progress = Signal(int, int)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, image_list, output_file):
        super().__init__()
        self.image_list = image_list
        self.output_file = output_file

    def run(self):
        try:
            def callback(current, total):
                self.progress.emit(current, total)
                
            images_to_pdf(self.image_list, self.output_file, callback=callback)
            self.finished.emit("Imágenes convertidas a PDF exitosamente.")
        except Exception as e:
            self.error.emit(f"{str(e)}\n\nTraceback:\n{traceback.format_exc()}")

class ImageToPdfTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # List of Images
        h_layout_list = QHBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        h_layout_list.addWidget(self.list_widget)

        # Buttons for list
        v_layout_btns = QVBoxLayout()
        self.add_btn = QPushButton("Añadir Imágenes")
        self.add_btn.clicked.connect(self.add_images)
        self.remove_btn = QPushButton("Eliminar Selección")
        self.remove_btn.clicked.connect(self.remove_images)
        self.up_btn = QPushButton("Mover Arriba")
        self.up_btn.clicked.connect(self.move_up)
        self.down_btn = QPushButton("Mover Abajo")
        self.down_btn.clicked.connect(self.move_down)
        
        v_layout_btns.addWidget(self.add_btn)
        v_layout_btns.addWidget(self.remove_btn)
        v_layout_btns.addWidget(self.up_btn)
        v_layout_btns.addWidget(self.down_btn)
        v_layout_btns.addStretch()
        h_layout_list.addLayout(v_layout_btns)
        
        layout.addLayout(h_layout_list)

        # Output File
        h_layout_out = QHBoxLayout()
        self.output_label = QLabel("PDF de Salida:")
        self.output_edit = QLineEdit()
        self.output_btn = QPushButton("Examinar")
        self.output_btn.clicked.connect(self.browse_output)
        h_layout_out.addWidget(self.output_label)
        h_layout_out.addWidget(self.output_edit)
        h_layout_out.addWidget(self.output_btn)
        layout.addLayout(h_layout_out)

        # Run Button
        self.run_btn = QPushButton("Convertir Imágenes a PDF")
        self.run_btn.clicked.connect(self.run_conversion)
        layout.addWidget(self.run_btn)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

    def add_images(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Seleccionar Imágenes", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff *.webp)")
        if files:
            self.list_widget.addItems(files)

    def remove_images(self):
        for item in self.list_widget.selectedItems():
            self.list_widget.takeItem(self.list_widget.row(item))

    def move_up(self):
        current_row = self.list_widget.currentRow()
        if current_row > 0:
            item = self.list_widget.takeItem(current_row)
            self.list_widget.insertItem(current_row - 1, item)
            self.list_widget.setCurrentRow(current_row - 1)

    def move_down(self):
        current_row = self.list_widget.currentRow()
        if current_row < self.list_widget.count() - 1 and current_row != -1:
            item = self.list_widget.takeItem(current_row)
            self.list_widget.insertItem(current_row + 1, item)
            self.list_widget.setCurrentRow(current_row + 1)

    def browse_output(self):
        file, _ = QFileDialog.getSaveFileName(self, "Guardar PDF", "", "PDF Files (*.pdf)")
        if file:
            self.output_edit.setText(file)

    def run_conversion(self):
        image_list = [self.list_widget.item(i).text() for i in range(self.list_widget.count())]
        output_file = self.output_edit.text()

        if not image_list or not output_file:
            QMessageBox.warning(self, "Advertencia", "Por favor, añada imágenes y especifique el archivo de salida.")
            return

        self.run_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        
        self.worker = ImageToPdfWorker(image_list, output_file)
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
