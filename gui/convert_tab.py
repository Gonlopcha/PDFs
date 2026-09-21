import traceback
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                               QPushButton, QFileDialog, QListWidget, QProgressBar, 
                               QMessageBox, QAbstractItemView)
from PySide6.QtCore import QThread, Signal
from core.converter import convert_batch

class ConvertWorker(QThread):
    progress = Signal(int, int)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, pdf_list, output_dir):
        super().__init__()
        self.pdf_list = pdf_list
        self.output_dir = output_dir

    def run(self):
        try:
            def callback(current, total):
                self.progress.emit(current, total)
                
            convert_batch(self.pdf_list, self.output_dir, callback=callback)
            self.finished.emit("PDFs converted successfully.")
        except Exception as e:
            self.error.emit(f"{str(e)}\n\nTraceback:\n{traceback.format_exc()}")

class ConvertTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # List of PDFs
        h_layout_list = QHBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        h_layout_list.addWidget(self.list_widget)

        # Buttons for list
        v_layout_btns = QVBoxLayout()
        self.add_btn = QPushButton("Add PDFs")
        self.add_btn.clicked.connect(self.add_pdfs)
        self.remove_btn = QPushButton("Remove Selected")
        self.remove_btn.clicked.connect(self.remove_pdfs)
        
        v_layout_btns.addWidget(self.add_btn)
        v_layout_btns.addWidget(self.remove_btn)
        v_layout_btns.addStretch()
        h_layout_list.addLayout(v_layout_btns)
        
        layout.addLayout(h_layout_list)

        # Output Dir
        h_layout_out = QHBoxLayout()
        self.output_label = QLabel("Output Dir:")
        self.output_edit = QLineEdit()
        self.output_btn = QPushButton("Browse")
        self.output_btn.clicked.connect(self.browse_output)
        h_layout_out.addWidget(self.output_label)
        h_layout_out.addWidget(self.output_edit)
        h_layout_out.addWidget(self.output_btn)
        layout.addLayout(h_layout_out)

        # Run Button
        self.run_btn = QPushButton("Convert to Word")
        self.run_btn.clicked.connect(self.run_convert)
        layout.addWidget(self.run_btn)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

    def add_pdfs(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select PDFs", "", "PDF Files (*.pdf)")
        if files:
            self.list_widget.addItems(files)

    def remove_pdfs(self):
        for item in self.list_widget.selectedItems():
            self.list_widget.takeItem(self.list_widget.row(item))

    def browse_output(self):
        dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dir:
            self.output_edit.setText(dir)

    def run_convert(self):
        pdf_list = [self.list_widget.item(i).text() for i in range(self.list_widget.count())]
        output_dir = self.output_edit.text()

        if not pdf_list or not output_dir:
            QMessageBox.warning(self, "Warning", "Please add PDFs and specify output directory.")
            return

        self.run_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        
        self.worker = ConvertWorker(pdf_list, output_dir)
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
        QMessageBox.information(self, "Success", msg)
        self.run_btn.setEnabled(True)

    def on_error(self, err):
        self.progress_bar.setValue(0)
        self.run_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", f"An error occurred:\n{err}")
