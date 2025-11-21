from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtCore import QSettings
import os

class SettingsManager(QObject):
    settings_changed = pyqtSignal(str, object)  # key, new_value

    def __init__(self, path="./pt100_controller_config"):
        super().__init__()
        self.config_folder = os.path.relpath(path)

        print("Settings initalizing")
        if not os.path.exists(self.config_folder):
            print("Settings not found. Creating settings with default values.")
            os.makedirs(self.config_folder, exist_ok=True)  # create folder if it doesn't exist
            config_file = os.path.join(self.config_folder, "settings.ini")
            open(config_file, "w").close()
            self._settings = QSettings(config_file, QSettings.Format.IniFormat)
            self._settings.setValue("hardware/NUM_SENSORS", 8)
            self._settings.setValue("hardware/VREF", 3.7) #3.3 V nominal
            self._settings.setValue("hardware/ALPHA", 0.00385)
            self._settings.setValue("hardware/IREF", 0.00215)

            self._settings.setValue("user/theme", "dark")
            self._settings.setValue("user/language", "en")

            self._settings.setValue("gui/display_log", False)
            self._settings.setValue("gui/display_connection_status", False)
            self._settings.setValue("gui/buffer_length", 1000)
            self._settings.setValue("gui/graph_update_rate", 50) #50 = 20 fps

            for i in range(self.get("hardware/NUM_SENSORS")):
                self._settings.setValue(f"hardware/temp_sensors/{i}", True)
        else:
            config_file = os.path.join(self.config_folder, "settings.ini")
            self._settings = QSettings(config_file, QSettings.Format.IniFormat)

    def get(self, key, default=None, type=None):
        if type==int:
            return int(self._settings.value(key, type))
        if type==float:
            return float(self._settings.value(key, type))
        if type==bool:
            if self._settings.value(key, str) == "false":
                return False
            elif self._settings.value(key, str) == "true":
                return True
            else:
                return self._settings.value(key, type)
        return self._settings.value(key, type)

    def set(self, key, value):
        self._settings.setValue(key, value)
        self.settings_changed.emit(key, value)
