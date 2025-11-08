from PyQt6.QtCore import QSettings
import os

NUM_SENSORS = 8
# standard PT100 (IEC 60751 Class B) constant:
ALPHA = 0.00385 #ohms/degree celsius
VREF = 3.3         # volts
IREF = 0.00215 #Amp. Measure this!
WIRE_RESISTANCE = 0.5 #ohms

def generate_default_settings(settings):
    settings.setValue("hardware/NUM_SENSORS", NUM_SENSORS)
    settings.setValue("hardware/VREF", VREF)
    settings.setValue("hardware/ALPHA", ALPHA)
    settings.setValue("hardware/IREF", IREF)

    settings.setValue("user/theme", "dark")
    settings.setValue("user/language", "en")

    settings.setValue("gui/display_log", False)
    settings.setValue("gui/display_connection_status", False)