from PyQt6.QtWidgets import QDialog, QVBoxLayout, QSpinBox, QCheckBox, QPushButton

class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Settings")

        layout = QVBoxLayout(self)

        # Example setting: dark mode
        self.dark_mode_check = QCheckBox("Enable dark mode")
        layout.addWidget(self.dark_mode_check)

        # Buttons
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

        # Load saved values
        self.load_settings()

    def load_settings(self):
        dark_mode = self.settings.get("user/theme")
        if dark_mode == "dark":
            self.dark_mode_check.setChecked(True)
        else:
            self.dark_mode_check.setChecked(False)

    def save_settings(self):
        if self.dark_mode_check.isChecked():
            self.settings.set("user/theme", "dark")
        else:
            self.settings.set("user/theme", "light")
        self.accept()  # closes the dialogs
