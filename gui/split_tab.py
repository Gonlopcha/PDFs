import os
import traceback
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                               QPushButton, QFileDialog, QRadioButton, QButtonGroup, 
                               QProgressBar, QMessageBox, QGroupBox)
from PySide6.QtCore import QThread, Signal
from core.splitter import split_by_ranges, split_every_n, split_all

class SplitWorker(QThread):
    progress = Signal(int, int)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, input_pdf, output_dir, split_type, param):
        super().__init__()
        self.input_pdf = input_pdf
        self.output_dir = output_dir
        self.split_type = split_type
        self.param = param

    def run(self):
        try:
            def callback(current, total):
                self.progress.emit(current, total)
                
            if self.split_type == "ranges":
                split_by_ranges(self.input_pdf, self.output_dir, self.param, callback=callback)
            elif self.split_type == "every_n":
                split_every_n(self.input_pdf, self.output_dir, int(self.param), callback=callback)
            elif self.split_type == "all":
                split_all(self.input_pdf, self.output_dir, callback=callback)
                
            self.finished.emit("PDF split successfully.")
        except Exception as e:
            self.error.emit(f"{str(e)}\n\nTraceback:\n{traceback.format_exc()}")

class SplitTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Input PDF
        h_layout1 = QHBoxLayout()
        self.input_label = QLabel("Input PDF:")
        self.input_edit = QLineEdit()
        self.input_btn = QPushButton("Browse")
        self.input_btn.clicked.connect(self.browse_input)
        h_layout1.addWidget(self.input_label)
        h_layout1.addWidget(self.input_edit)
        h_layout1.addWidget(self.input_btn)
        layout.addLayout(h_layout1)

        # Output Dir
        h_layout2 = QHBoxLayout()
        self.output_label = QLabel("Output Dir:")
        self.output_edit = QLineEdit()
        self.output_btn = QPushButton("Browse")
        self.output_btn.clicked.connect(self.browse_output)
        h_layout2.addWidget(self.output_label)
        h_layout2.addWidget(self.output_edit)
        h_layout2.addWidget(self.output_btn)
        layout.addLayout(h_layout2)

        # Split Options
        group = QGroupBox("Split Options")
        g_layout = QVBoxLayout()
        self.btn_group = QButtonGroup(self)
        
        self.rb_all = QRadioButton("Split All Pages")
        self.rb_all.setChecked(True)
        self.btn_group.addButton(self.rb_all, 1)
        g_layout.addWidget(self.rb_all)

        h_layout3 = QHBoxLayout()
        self.rb_ranges = QRadioButton("Split by Ranges:")
        self.btn_group.addButton(self.rb_ranges, 2)
        self.ranges_edit = QLineEdit()
        self.ranges_edit.setPlaceholderText("e.g. 1-3, 4-5")
        h_layout3.addWidget(self.rb_ranges)
        h_layout3.addWidget(self.ranges_edit)
        g_layout.addLayout(h_layout3)

        h_layout4 = QHBoxLayout()
        self.rb_every = QRadioButton("Split Every N Pages:")
        self.btn_group.addButton(self.rb_every, 3)
        self.every_edit = QLineEdit()
        self.every_edit.setPlaceholderText("e.g. 5")
        h_layout4.addWidget(self.rb_every)
        h_layout4.addWidget(self.every_edit)
        g_layout.addLayout(h_layout4)
        
        group.setLayout(g_layout)
        layout.addWidget(group)

        # Run Button
        self.run_btn = QPushButton("Split PDF")
        self.run_btn.clicked.connect(self.run_split)
        layout.addWidget(self.run_btn)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        layout.addStretch()

    def browse_input(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
        if file:
            self.input_edit.setText(file)

    def browse_output(self):
        dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dir:
            self.output_edit.setText(dir)

    def run_split(self):
        input_pdf = self.input_edit.text()
        output_dir = self.output_edit.text()

        if not input_pdf or not output_dir:
            QMessageBox.warning(self, "Warning", "Please select input PDF and output directory.")
            return

        split_type = "all"
        param = ""
        if self.rb_ranges.isChecked():
            split_type = "ranges"
            param = self.ranges_edit.text()
            if not param:
                QMessageBox.warning(self, "Warning", "Please specify ranges.")
                return
        elif self.rb_every.isChecked():
            split_type = "every_n"
            param = self.every_edit.text()
            if not param or not param.isdigit():
                QMessageBox.warning(self, "Warning", "Please specify a valid number for N.")
                return

        self.run_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        
        self.worker = SplitWorker(input_pdf, output_dir, split_type, param)
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
