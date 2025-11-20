from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QCheckBox, QPushButton, QApplication
)

class SensorSettings(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        print("Loading sensor settings.")
        self.setWindowTitle("Select which sensors to display.")
        self.settings = settings
        
        self.items = []
        for i in range(self.settings.get("hardware/NUM_SENSORS", type=int)):
            self.items.append(f"Sensor{i}")

        layout = QVBoxLayout(self)
        self.checkboxes = []

        # Create a checkbox for each item
        for text in self.items:
            cb = QCheckBox(text)
            self.checkboxes.append(cb)
            layout.addWidget(self.checkboxes[-1])

        for i in range(len(self.items)):
            self.checkboxes[i].setChecked(self.settings.get(f"hardware/temp_sensors/{i}", type=bool))

        # Add OK and Cancel buttons
        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        layout.addWidget(btn_ok)
        layout.addWidget(btn_cancel)

    # Helper method to get selected items
    def get_selected_items(self):
        return [cb.isChecked() for cb in self.checkboxes]

    def load_graphs(self):
        selected = self.get_selected_items()
        for i in range(self.settings.get("hardware/NUM_SENSORS", type=int)):
            self.settings.set(f"hardware/temp_sensors/{i}", selected[i])