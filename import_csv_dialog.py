from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QFileDialog, QCheckBox
import csv

class ImportCsvDialog(QDialog):
    def __init__(self, parent=None):
        super(ImportCsvDialog, self).__init__(parent)
        self.setWindowTitle("Import CSV")
        self.layout = QVBoxLayout(self)

        # File selection
        self.file_layout = QHBoxLayout()
        self.file_label = QLabel("CSV File:")
        self.file_edit = QLineEdit()
        self.file_button = QPushButton("...")
        self.file_button.clicked.connect(self.select_file)
        self.file_layout.addWidget(self.file_label)
        self.file_layout.addWidget(self.file_edit)
        self.file_layout.addWidget(self.file_button)
        self.layout.addLayout(self.file_layout)

        # Delimiter
        self.delimiter_layout = QHBoxLayout()
        self.delimiter_label = QLabel("Delimiter:")
        self.delimiter_combo = QComboBox()
        self.delimiter_combo.addItems([",", ";"])
        self.delimiter_layout.addWidget(self.delimiter_label)
        self.delimiter_layout.addWidget(self.delimiter_combo)
        self.layout.addLayout(self.delimiter_layout)

        # X and Y fields
        self.x_layout = QHBoxLayout()
        self.x_label = QLabel("X Field:")
        self.x_combo = QComboBox()
        self.x_layout.addWidget(self.x_label)
        self.x_layout.addWidget(self.x_combo)
        self.layout.addLayout(self.x_layout)

        self.y_layout = QHBoxLayout()
        self.y_label = QLabel("Y Field:")
        self.y_combo = QComboBox()
        self.y_layout.addWidget(self.y_label)
        self.y_layout.addWidget(self.y_combo)
        self.layout.addLayout(self.y_layout)

        # Detect types checkbox
        self.detect_types_checkbox = QCheckBox("Detect field types")
        self.detect_types_checkbox.setChecked(False)
        self.layout.addWidget(self.detect_types_checkbox)

        # Buttons
        self.button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.button_layout.addWidget(self.ok_button)
        self.button_layout.addWidget(self.cancel_button)
        self.layout.addLayout(self.button_layout)

        self.file_edit.textChanged.connect(self.update_fields)

    def select_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if file_name:
            self.file_edit.setText(file_name)

    def update_fields(self, file_name):
        if file_name:
            try:
                with open(file_name, 'r') as f:
                    sniffer = csv.Sniffer()
                    dialect = sniffer.sniff(f.read(1024))
                    f.seek(0)
                    self.delimiter_combo.setCurrentText(dialect.delimiter)
                    reader = csv.reader(f, dialect)
                    header = next(reader)
                    self.x_combo.clear()
                    self.y_combo.clear()
                    self.x_combo.addItems(header)
                    self.y_combo.addItems(header)

                    # Auto-select X and Y fields if present
                    for field in header:
                        if field.lower() == 'x':
                            self.x_combo.setCurrentText(field)
                        if field.lower() == 'y':
                            self.y_combo.setCurrentText(field)
            except Exception as e:
                print(f"Error reading CSV header: {e}")

    def get_options(self):
        return {
            "file_path": self.file_edit.text(),
            "delimiter": self.delimiter_combo.currentText(),
            "x_field": self.x_combo.currentText(),
            "y_field": self.y_combo.currentText(),
            "detect_types": self.detect_types_checkbox.isChecked(),
        }