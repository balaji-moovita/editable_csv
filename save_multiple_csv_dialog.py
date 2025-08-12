from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QFileDialog, QLabel

class SaveMultipleCsvDialog(QDialog):
    def __init__(self, parent=None):
        super(SaveMultipleCsvDialog, self).__init__(parent)
        self.setWindowTitle("Save All to Folder")
        self.selected_folder = ""
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Folder selection
        folder_layout = QHBoxLayout()
        self.folder_edit = QLineEdit()
        self.folder_edit.setReadOnly(True)
        self.folder_edit.setPlaceholderText("Select a folder to save all layers...")
        folder_layout.addWidget(self.folder_edit)

        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.browse_button)
        main_layout.addLayout(folder_layout)

        # Save/Cancel buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", "")
        if folder:
            self.selected_folder = folder
            self.folder_edit.setText(folder)
            self.save_button.setEnabled(True)

    def get_selected_folder(self):
        return self.selected_folder