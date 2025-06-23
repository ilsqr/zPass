"""
Settings Dialog
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                            QLineEdit, QPushButton, QLabel, QTextEdit,
                            QComboBox, QCheckBox, QSpinBox, QGroupBox,
                            QMessageBox, QTabWidget, QWidget, QSlider,
                            QFileDialog, QColorDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from typing import Dict, Any, Optional
import os
import platform
from ..config.settings import Settings

# Windows API için import'lar
if platform.system() == "Windows":
    try:
        import ctypes
        from ctypes import wintypes
        
        # Windows API constants
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        DWMWA_USE_IMMERSIVE_DARK_MODE_BEFORE_20H1 = 19
        
        # Windows API fonksiyonları
        dwmapi = ctypes.windll.dwmapi
        
        def set_window_dark_mode(hwnd, use_dark_mode):
            """Windows pencere başlık çubuğunu karanlık moda çevir"""
            try:
                # Windows 10 20H1 ve sonrası için
                result = dwmapi.DwmSetWindowAttribute(
                    hwnd, 
                    DWMWA_USE_IMMERSIVE_DARK_MODE,
                    ctypes.byref(ctypes.c_int(use_dark_mode)),
                    ctypes.sizeof(ctypes.c_int)
                )
                
                # Eğer başarısız olursa eski versiyonu dene (Windows 10 1903-1909)
                if result != 0:
                    dwmapi.DwmSetWindowAttribute(
                        hwnd,
                        DWMWA_USE_IMMERSIVE_DARK_MODE_BEFORE_20H1,
                        ctypes.byref(ctypes.c_int(use_dark_mode)),
                        ctypes.sizeof(ctypes.c_int)
                    )
                
                return True
            except:
                return False
                
    except ImportError:
        def set_window_dark_mode(hwnd, use_dark_mode):
            return False
else:
    def set_window_dark_mode(hwnd, use_dark_mode):
        return False

class AppearanceTab(QWidget):
    """Appearance settings tab"""
    
    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Theme settings
        theme_group = QGroupBox("Theme")
        theme_layout = QFormLayout(theme_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["System", "Light", "Dark", "Auto"])
        theme_layout.addRow("Theme:", self.theme_combo)
        
        # Font settings
        font_group = QGroupBox("Font")
        font_layout = QFormLayout(font_group)
        
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems(["System Default", "Arial", "Helvetica", "Times New Roman", "Courier New"])
        font_layout.addRow("Font Family:", self.font_family_combo)
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(10)
        font_layout.addRow("Font Size:", self.font_size_spin)
        
        # Window settings
        window_group = QGroupBox("Window")
        window_layout = QFormLayout(window_group)
        
        self.remember_size_check = QCheckBox("Remember window size and position")
        window_layout.addRow(self.remember_size_check)
        
        self.minimize_to_tray_check = QCheckBox("Minimize to system tray")
        window_layout.addRow(self.minimize_to_tray_check)
        
        self.start_minimized_check = QCheckBox("Start minimized")
        window_layout.addRow(self.start_minimized_check)
        
        layout.addWidget(theme_group)
        layout.addWidget(font_group)
        layout.addWidget(window_group)
        layout.addStretch()
    
    def load_settings(self):
        """Load settings from config"""
        self.theme_combo.setCurrentText(self.settings.get_theme())
        self.font_family_combo.setCurrentText(self.settings.get_font_family())
        self.font_size_spin.setValue(self.settings.get_font_size())
        self.remember_size_check.setChecked(self.settings.get_remember_window_state())
        self.minimize_to_tray_check.setChecked(self.settings.get_minimize_to_tray())
        self.start_minimized_check.setChecked(self.settings.get_start_minimized())
    
    def save_settings(self):
        """Save settings to config"""
        self.settings.set_theme(self.theme_combo.currentText())
        self.settings.set_font_family(self.font_family_combo.currentText())
        self.settings.set_font_size(self.font_size_spin.value())
        self.settings.set_remember_window_state(self.remember_size_check.isChecked())
        self.settings.set_minimize_to_tray(self.minimize_to_tray_check.isChecked())
        self.settings.set_start_minimized(self.start_minimized_check.isChecked())

class SecurityTab(QWidget):
    """Security settings tab"""
    
    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Auto-lock settings
        lock_group = QGroupBox("Auto Lock")
        lock_layout = QFormLayout(lock_group)
        
        self.auto_lock_check = QCheckBox("Enable auto-lock")
        lock_layout.addRow(self.auto_lock_check)
        
        self.lock_timeout_spin = QSpinBox()
        self.lock_timeout_spin.setRange(1, 60)
        self.lock_timeout_spin.setValue(15)
        self.lock_timeout_spin.setSuffix(" minutes")
        lock_layout.addRow("Lock after:", self.lock_timeout_spin)
        
        self.lock_on_minimize_check = QCheckBox("Lock when minimized")
        lock_layout.addRow(self.lock_on_minimize_check)
        
        self.lock_on_focus_lost_check = QCheckBox("Lock when focus is lost")
        lock_layout.addRow(self.lock_on_focus_lost_check)
        
        # Password generation defaults
        gen_group = QGroupBox("Password Generation Defaults")
        gen_layout = QFormLayout(gen_group)
        
        self.default_length_spin = QSpinBox()
        self.default_length_spin.setRange(8, 64)
        self.default_length_spin.setValue(16)
        gen_layout.addRow("Default Length:", self.default_length_spin)
        
        self.include_uppercase_check = QCheckBox("Include uppercase letters")
        self.include_uppercase_check.setChecked(True)
        gen_layout.addRow(self.include_uppercase_check)
        
        self.include_lowercase_check = QCheckBox("Include lowercase letters")
        self.include_lowercase_check.setChecked(True)
        gen_layout.addRow(self.include_lowercase_check)
        
        self.include_numbers_check = QCheckBox("Include numbers")
        self.include_numbers_check.setChecked(True)
        gen_layout.addRow(self.include_numbers_check)
        
        self.include_symbols_check = QCheckBox("Include symbols")
        self.include_symbols_check.setChecked(True)
        gen_layout.addRow(self.include_symbols_check)
        
        # Clipboard settings
        clipboard_group = QGroupBox("Clipboard")
        clipboard_layout = QFormLayout(clipboard_group)
        
        self.clear_clipboard_check = QCheckBox("Clear clipboard after copying")
        clipboard_layout.addRow(self.clear_clipboard_check)
        
        self.clipboard_timeout_spin = QSpinBox()
        self.clipboard_timeout_spin.setRange(5, 300)
        self.clipboard_timeout_spin.setValue(30)
        self.clipboard_timeout_spin.setSuffix(" seconds")
        clipboard_layout.addRow("Clear after:", self.clipboard_timeout_spin)
        
        layout.addWidget(lock_group)
        layout.addWidget(gen_group)
        layout.addWidget(clipboard_group)
        layout.addStretch()
    
    def load_settings(self):
        """Load settings from config"""
        self.auto_lock_check.setChecked(self.settings.get_auto_lock_enabled())
        self.lock_timeout_spin.setValue(self.settings.get_auto_lock_timeout())
        self.lock_on_minimize_check.setChecked(self.settings.get_lock_on_minimize())
        self.lock_on_focus_lost_check.setChecked(self.settings.get_lock_on_focus_lost())
        
        self.default_length_spin.setValue(self.settings.get_default_password_length())
        self.include_uppercase_check.setChecked(self.settings.get_include_uppercase())
        self.include_lowercase_check.setChecked(self.settings.get_include_lowercase())
        self.include_numbers_check.setChecked(self.settings.get_include_numbers())
        self.include_symbols_check.setChecked(self.settings.get_include_symbols())
        
        self.clear_clipboard_check.setChecked(self.settings.get_clear_clipboard())
        self.clipboard_timeout_spin.setValue(self.settings.get_clipboard_timeout())
    
    def save_settings(self):
        """Save settings to config"""
        self.settings.set_auto_lock_enabled(self.auto_lock_check.isChecked())
        self.settings.set_auto_lock_timeout(self.lock_timeout_spin.value())
        self.settings.set_lock_on_minimize(self.lock_on_minimize_check.isChecked())
        self.settings.set_lock_on_focus_lost(self.lock_on_focus_lost_check.isChecked())
        
        self.settings.set_default_password_length(self.default_length_spin.value())
        self.settings.set_include_uppercase(self.include_uppercase_check.isChecked())
        self.settings.set_include_lowercase(self.include_lowercase_check.isChecked())
        self.settings.set_include_numbers(self.include_numbers_check.isChecked())
        self.settings.set_include_symbols(self.include_symbols_check.isChecked())
        
        self.settings.set_clear_clipboard(self.clear_clipboard_check.isChecked())
        self.settings.set_clipboard_timeout(self.clipboard_timeout_spin.value())

class SyncTab(QWidget):
    """Sync settings tab"""
    
    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Server settings
        server_group = QGroupBox("Server Settings")
        server_layout = QFormLayout(server_group)
        
        self.server_type_combo = QComboBox()
        self.server_type_combo.addItems(["Official Server", "Custom Server", "Local (Localhost)"])
        self.server_type_combo.currentTextChanged.connect(self.on_server_type_changed)
        server_layout.addRow("Server Type:", self.server_type_combo)
        
        self.custom_server_edit = QLineEdit()
        self.custom_server_edit.setPlaceholderText("https://your-server.com:5000")
        server_layout.addRow("Custom Server URL:", self.custom_server_edit)
        
        # Sync settings
        sync_group = QGroupBox("Synchronization")
        sync_layout = QFormLayout(sync_group)
        
        self.auto_sync_check = QCheckBox("Enable automatic synchronization")
        sync_layout.addRow(self.auto_sync_check)
        
        self.sync_interval_spin = QSpinBox()
        self.sync_interval_spin.setRange(1, 60)
        self.sync_interval_spin.setValue(5)
        self.sync_interval_spin.setSuffix(" minutes")
        sync_layout.addRow("Sync interval:", self.sync_interval_spin)
        
        self.sync_on_startup_check = QCheckBox("Sync on startup")
        sync_layout.addRow(self.sync_on_startup_check)
        
        self.sync_on_changes_check = QCheckBox("Sync immediately on changes")
        sync_layout.addRow(self.sync_on_changes_check)
        
        layout.addWidget(server_group)
        layout.addWidget(sync_group)
        layout.addStretch()
    
    def on_server_type_changed(self, server_type: str):
        """Handle server type change"""
        self.custom_server_edit.setEnabled(server_type == "Custom Server")
    
    def load_settings(self):
        """Load settings from config"""
        server_type = self.settings.get_server_type()
        self.server_type_combo.setCurrentText(server_type)
        self.custom_server_edit.setText(self.settings.get_custom_server_url())
        self.on_server_type_changed(server_type)
        
        self.auto_sync_check.setChecked(self.settings.get_auto_sync_enabled())
        self.sync_interval_spin.setValue(self.settings.get_sync_interval())
        self.sync_on_startup_check.setChecked(self.settings.get_sync_on_startup())
        self.sync_on_changes_check.setChecked(self.settings.get_sync_on_changes())
    
    def save_settings(self):
        """Save settings to config"""
        self.settings.set_server_type(self.server_type_combo.currentText())
        self.settings.set_custom_server_url(self.custom_server_edit.text())
        
        self.settings.set_auto_sync_enabled(self.auto_sync_check.isChecked())
        self.settings.set_sync_interval(self.sync_interval_spin.value())
        self.settings.set_sync_on_startup(self.sync_on_startup_check.isChecked())
        self.settings.set_sync_on_changes(self.sync_on_changes_check.isChecked())

class SettingsDialog(QDialog):
    """Main settings dialog"""
    
    settings_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = Settings()
        self.setup_ui()
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumSize(600, 500)
        self.apply_theme()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Settings")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # Appearance tab
        self.appearance_tab = AppearanceTab(self.settings)
        self.tabs.addTab(self.appearance_tab, "Appearance")
        
        # Security tab
        self.security_tab = SecurityTab(self.settings)
        self.tabs.addTab(self.security_tab, "Security")
        
        # Sync tab
        self.sync_tab = SyncTab(self.settings)
        self.tabs.addTab(self.sync_tab, "Sync")
        
        layout.addWidget(self.tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        reply = QMessageBox.question(
            self, "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.settings.reset_to_defaults()
            self.appearance_tab.load_settings()
            self.security_tab.load_settings()
            self.sync_tab.load_settings()
    
    def save_settings(self):
        """Save all settings"""
        try:
            self.appearance_tab.save_settings()
            self.security_tab.save_settings()
            self.sync_tab.save_settings()
            
            self.settings_changed.emit()
            QMessageBox.information(self, "Settings", "Settings saved successfully!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")
    
    def apply_theme(self):
        """Apply current theme to the dialog"""
        theme = self.settings.get_theme()
        is_dark_mode = theme == "Dark"
        
        if is_dark_mode:
            self.setStyleSheet("""
                QDialog { 
                    background-color: #2b2b2b; 
                    color: #ffffff; 
                }
                QTabWidget::pane { 
                    background-color: #2b2b2b; 
                    border: 1px solid #555; 
                }
                QTabWidget::tab-bar { 
                    alignment: left; 
                }
                QTabBar::tab { 
                    background-color: #3c3c3c; 
                    color: #ffffff; 
                    padding: 8px 16px; 
                    margin-right: 2px; 
                    border: 1px solid #555;
                    border-bottom: none;
                }
                QTabBar::tab:selected { 
                    background-color: #0078d4; 
                }
                QTabBar::tab:hover { 
                    background-color: #404040; 
                }
                QLabel { 
                    color: #ffffff; 
                    background-color: transparent;
                }
                QLineEdit { 
                    background-color: #3c3c3c; 
                    border: 1px solid #555; 
                    padding: 8px; 
                    color: #ffffff;
                    border-radius: 4px;
                }
                QPushButton { 
                    background-color: #0078d4; 
                    color: white; 
                    border: none; 
                    padding: 10px 16px; 
                    border-radius: 4px; 
                    font-weight: bold;
                }
                QPushButton:hover { 
                    background-color: #106ebe; 
                }
                QPushButton:pressed { 
                    background-color: #005a9e; 
                }
                QComboBox { 
                    background-color: #3c3c3c; 
                    border: 1px solid #555; 
                    padding: 5px; 
                    color: #ffffff;
                    border-radius: 4px;
                }
                QComboBox::drop-down { 
                    border: none; 
                }
                QComboBox QAbstractItemView { 
                    background-color: #3c3c3c; 
                    color: #ffffff; 
                    selection-background-color: #0078d4; 
                }
                QCheckBox { 
                    color: #ffffff; 
                }
                QCheckBox::indicator:unchecked { 
                    background-color: #3c3c3c; 
                    border: 1px solid #555; 
                }
                QCheckBox::indicator:checked { 
                    background-color: #0078d4; 
                    border: 1px solid #0078d4; 
                }
                QSpinBox { 
                    background-color: #3c3c3c; 
                    border: 1px solid #555; 
                    color: #ffffff; 
                    padding: 5px;
                    border-radius: 4px;
                }
                QSlider::groove:horizontal { 
                    background-color: #3c3c3c; 
                    height: 4px; 
                    border-radius: 2px; 
                }
                QSlider::handle:horizontal { 
                    background-color: #0078d4; 
                    width: 16px; 
                    height: 16px; 
                    margin: -6px 0; 
                    border-radius: 8px; 
                }
                QGroupBox { 
                    font-weight: bold; 
                    border: 1px solid #555; 
                    margin: 5px 0px; 
                    padding-top: 10px;
                    color: #ffffff;
                }
                QGroupBox::title { 
                    subcontrol-origin: margin; 
                    left: 10px; 
                    padding: 0px 5px;
                }
            """)
        else:
            self.setStyleSheet("")  # Use default light theme
        
        # Windows title bar'ını ayarla
        if platform.system() == "Windows":
            try:
                hwnd = int(self.winId())
                set_window_dark_mode(hwnd, is_dark_mode)
            except:
                pass  # Hata durumunda sessizce devam et
