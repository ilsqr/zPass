#!/usr/bin/env python3
"""
zPass - Secure Password Manager
Main application entry point
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from src.ui.main_window import MainWindow
from src.config.settings import Settings
from src.utils.crypto import CryptoManager

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("zPass")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("zPass")
    app.setOrganizationDomain("zpass.local")
    
    # Enable high DPI scaling (PyQt6 handles this automatically)
    # app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    # app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    # Set application icon
    try:
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
    except Exception:
        pass  # Icon is optional
    
    # Initialize settings
    settings = Settings()
    
    # Create and show main window
    window = MainWindow(settings)
    window.show()
    
    # Start the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
