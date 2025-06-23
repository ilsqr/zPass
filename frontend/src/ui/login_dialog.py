"""
Login dialog with server selection
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QLineEdit, QPushButton, QLabel, QComboBox, 
                            QCheckBox, QGroupBox, QTextEdit, QMessageBox,
                            QProgressBar, QFrame, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPixmap, QIcon
import re
import platform
from typing import Dict, Any, Optional
from ..config.settings import Settings
from ..api.client import APIClient

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

class ServerTestThread(QThread):
    """Thread for testing server connection"""
    finished = pyqtSignal(bool, dict)
    
    def __init__(self, server_url: str):
        super().__init__()
        self.server_url = server_url
    
    def run(self):
        try:
            client = APIClient(self.server_url)
            success, response = client.test_connection()
            self.finished.emit(success, response)
        except Exception as e:
            self.finished.emit(False, {"error": str(e)})

class LoginThread(QThread):
    """Thread for login process"""
    finished = pyqtSignal(bool, dict)
    
    def __init__(self, server_url: str, username: str, password: str):
        super().__init__()
        self.server_url = server_url
        self.username = username
        self.password = password
    
    def run(self):
        try:
            client = APIClient(self.server_url)
            success, response = client.login(self.username, self.password)
            self.finished.emit(success, response)
        except Exception as e:
            self.finished.emit(False, {"error": str(e)})

class AddServerDialog(QDialog):
    """Dialog for adding custom server"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Custom Server")
        self.setModal(True)
        self.setFixedSize(400, 300)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Form
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("My Server")
        form_layout.addRow("Server Name:", self.name_edit)
        
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("https://my-server.com")
        form_layout.addRow("Server URL:", self.url_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Optional description...")
        self.description_edit.setMaximumHeight(80)
        form_layout.addRow("Description:", self.description_edit)
        
        layout.addLayout(form_layout)
        
        # Test button
        self.test_btn = QPushButton("Test Connection")
        self.test_btn.clicked.connect(self.test_connection)
        layout.addWidget(self.test_btn)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.add_btn = QPushButton("Add Server")
        self.add_btn.clicked.connect(self.accept)
        self.add_btn.setEnabled(False)
        button_layout.addWidget(self.add_btn)
        
        layout.addLayout(button_layout)
        
        # Connect text changes
        self.name_edit.textChanged.connect(self.validate_form)
        self.url_edit.textChanged.connect(self.validate_form)
    
    def validate_form(self):
        """Validate form inputs"""
        name = self.name_edit.text().strip()
        url = self.url_edit.text().strip()
        
        # Basic validation
        valid = bool(name and url)
        if valid:
            # URL format validation
            url_pattern = r'^https?://.+'
            valid = re.match(url_pattern, url) is not None
        
        self.add_btn.setEnabled(valid)
    
    def test_connection(self):
        """Test connection to server"""
        url = self.url_edit.text().strip()
        if not url:
            return
        
        self.test_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.status_label.setText("Testing connection...")
        
        self.test_thread = ServerTestThread(url)
        self.test_thread.finished.connect(self.on_test_finished)
        self.test_thread.start()
    
    def on_test_finished(self, success: bool, response: Dict[str, Any]):
        """Handle test connection result"""
        self.test_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            self.status_label.setText("✅ Connection successful!")
            self.status_label.setStyleSheet("color: green;")
        else:
            error_msg = response.get('error', 'Unknown error')
            self.status_label.setText(f"❌ Connection failed: {error_msg}")
            self.status_label.setStyleSheet("color: red;")
    
    def get_server_data(self) -> Dict[str, str]:
        """Get server data from form"""
        return {
            "name": self.name_edit.text().strip(),
            "url": self.url_edit.text().strip().rstrip('/'),
            "description": self.description_edit.toPlainText().strip()
        }

class LoginDialog(QDialog):
    """Login dialog with server selection"""
    
    login_successful = pyqtSignal(dict, object)  # user_data, api_client
    
    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.api_client = None
        self.setWindowTitle("zPass - Login")
        self.setModal(True)
        self.setFixedSize(450, 550)
        self.setup_ui()
        self.load_servers()
        self.apply_theme()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Logo/Title
        title_label = QLabel("🔐 zPass")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        subtitle_label = QLabel("Secure Password Manager")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: gray; font-size: 12px;")
        layout.addWidget(subtitle_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Server Selection Group
        server_group = QGroupBox("Server Selection")
        server_layout = QVBoxLayout(server_group)
        
        server_combo_layout = QHBoxLayout()
        self.server_combo = QComboBox()
        self.server_combo.currentTextChanged.connect(self.on_server_changed)
        server_combo_layout.addWidget(QLabel("Server:"))
        server_combo_layout.addWidget(self.server_combo, 1)
        
        self.add_server_btn = QPushButton("+")
        self.add_server_btn.setMaximumWidth(30)
        self.add_server_btn.setToolTip("Add Custom Server")
        self.add_server_btn.clicked.connect(self.add_custom_server)
        server_combo_layout.addWidget(self.add_server_btn)
        
        server_layout.addLayout(server_combo_layout)
        
        # Server info
        self.server_info_label = QLabel()
        self.server_info_label.setWordWrap(True)
        self.server_info_label.setStyleSheet("color: gray; font-size: 11px; padding: 5px;")
        server_layout.addWidget(self.server_info_label)
        
        # Connection status
        self.connection_status = QLabel()
        self.connection_status.setVisible(False)
        server_layout.addWidget(self.connection_status)
        
        layout.addWidget(server_group)
        
        # Login Form Group
        login_group = QGroupBox("Login Credentials")
        form_layout = QFormLayout(login_group)
        
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Username or Email")
        form_layout.addRow("Username:", self.username_edit)
        
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Master Password")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Password:", self.password_edit)
        
        # Options
        options_layout = QHBoxLayout()
        self.remember_checkbox = QCheckBox("Remember credentials")
        self.remember_checkbox.setChecked(self.settings.get_remember_credentials())
        options_layout.addWidget(self.remember_checkbox)
        options_layout.addStretch()
        
        form_layout.addRow(options_layout)
        
        layout.addWidget(login_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.register_btn = QPushButton("Create Account")
        self.register_btn.clicked.connect(self.show_register_dialog)
        button_layout.addWidget(self.register_btn)
        
        button_layout.addStretch()
        
        self.login_btn = QPushButton("Login")
        self.login_btn.setDefault(True)
        self.login_btn.clicked.connect(self.login)
        button_layout.addWidget(self.login_btn)
        
        layout.addLayout(button_layout)
        
        # Connect Enter key
        self.password_edit.returnPressed.connect(self.login)
        
        # Auto-test connection timer
        self.test_timer = QTimer()
        self.test_timer.setSingleShot(True)
        self.test_timer.timeout.connect(self.test_current_server)
    
    def load_servers(self):
        """Load available servers into combo box"""
        self.server_combo.clear()
        servers = self.settings.get_servers()
        
        current_server = self.settings._current_server
        
        for server_id, server_info in servers.items():
            display_name = f"{server_info['name']}"
            self.server_combo.addItem(display_name, server_id)
            
            # Set current selection
            if server_id == current_server:
                self.server_combo.setCurrentText(display_name)
        
        self.update_server_info()
    
    def on_server_changed(self):
        """Handle server selection change"""
        current_data = self.server_combo.currentData()
        if current_data:
            self.settings.set_current_server(current_data)
            self.update_server_info()
            
            # Test connection after short delay
            self.test_timer.start(1000)
    
    def update_server_info(self):
        """Update server information display"""
        server_info = self.settings.get_current_server_info()
        info_text = f"URL: {server_info['url']}"
        if server_info.get('description'):
            info_text += f"\\n{server_info['description']}"
        
        self.server_info_label.setText(info_text)
        self.connection_status.setVisible(False)
    
    def test_current_server(self):
        """Test connection to current server"""
        server_url = self.settings.get_current_server_url()
        
        self.connection_status.setText("Testing connection...")
        self.connection_status.setStyleSheet("color: orange;")
        self.connection_status.setVisible(True)
        
        self.test_thread = ServerTestThread(server_url)
        self.test_thread.finished.connect(self.on_connection_test_finished)
        self.test_thread.start()
    
    def on_connection_test_finished(self, success: bool, response: Dict[str, Any]):
        """Handle connection test result"""
        if success:
            self.connection_status.setText("✅ Connected")
            self.connection_status.setStyleSheet("color: green;")
        else:
            error_msg = response.get('error', 'Unknown error')
            self.connection_status.setText(f"❌ Connection failed")
            self.connection_status.setStyleSheet("color: red;")
            self.connection_status.setToolTip(error_msg)
    
    def add_custom_server(self):
        """Show dialog to add custom server"""
        dialog = AddServerDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            server_data = dialog.get_server_data()
            
            # Generate server ID
            server_id = server_data['name'].lower().replace(' ', '_')
            
            # Add server
            if self.settings.add_custom_server(server_id, **server_data):
                self.load_servers()
                
                # Select the new server
                for i in range(self.server_combo.count()):
                    if self.server_combo.itemData(i) == server_id:
                        self.server_combo.setCurrentIndex(i)
                        break
                
                QMessageBox.information(self, "Success", "Custom server added successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to add custom server.")
    
    def show_register_dialog(self):
        """Show registration dialog"""
        # Import here to avoid circular imports
        from .register_dialog import RegisterDialog
        
        dialog = RegisterDialog(self.settings, self)
        dialog.exec()
    
    def login(self):
        """Perform login"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        if not username or not password:
            self.show_status("Please enter username and password", "red")
            return
        
        # Save remember preference
        self.settings.set_remember_credentials(self.remember_checkbox.isChecked())
        
        # Start login process
        self.set_ui_enabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.show_status("Logging in...", "blue")
        
        server_url = self.settings.get_current_server_url()
        
        self.login_thread = LoginThread(server_url, username, password)
        self.login_thread.finished.connect(self.on_login_finished)
        self.login_thread.start()
    
    def on_login_finished(self, success: bool, response: Dict[str, Any]):
        """Handle login result"""
        self.set_ui_enabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            self.show_status("Login successful!", "green")
            
            # Create API client with token
            self.api_client = APIClient(self.settings.get_current_server_url())
            if 'access_token' in response:
                self.api_client.set_access_token(response['access_token'])
            
            # Emit success signal
            user_data = response.get('user', {})
            self.login_successful.emit(user_data, self.api_client)
            
            # Close dialog
            QTimer.singleShot(1000, self.accept)
        else:
            error_msg = response.get('error', 'Login failed')
            self.show_status(f"Login failed: {error_msg}", "red")
    
    def show_status(self, message: str, color: str):
        """Show status message"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {color};")
        self.status_label.setVisible(True)
    
    def set_ui_enabled(self, enabled: bool):
        """Enable/disable UI elements"""
        self.server_combo.setEnabled(enabled)
        self.add_server_btn.setEnabled(enabled)
        self.username_edit.setEnabled(enabled)
        self.password_edit.setEnabled(enabled)
        self.remember_checkbox.setEnabled(enabled)
        self.login_btn.setEnabled(enabled)
        self.register_btn.setEnabled(enabled)
    
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
                QComboBox::down-arrow { 
                    image: none; 
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
                QCheckBox::indicator { 
                    width: 18px; 
                    height: 18px; 
                }
                QCheckBox::indicator:unchecked { 
                    background-color: #3c3c3c; 
                    border: 1px solid #555; 
                }
                QCheckBox::indicator:checked { 
                    background-color: #0078d4; 
                    border: 1px solid #0078d4; 
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
                QTextEdit { 
                    background-color: #3c3c3c; 
                    border: 1px solid #555; 
                    color: #ffffff; 
                }
                QProgressBar { 
                    border: 1px solid #555; 
                    border-radius: 5px; 
                    text-align: center; 
                    background-color: #3c3c3c;
                }
                QProgressBar::chunk { 
                    background-color: #0078d4; 
                    border-radius: 5px; 
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
