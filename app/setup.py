# setup.py
from setuptools import setup

APP = ['MainWindow.py']
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'Phoebe.icns',  # optional
    'packages': [],  # any extra packages
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
