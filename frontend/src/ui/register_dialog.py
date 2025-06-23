"""
Registration dialog
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QLineEdit, QPushButton, QLabel, QTextEdit, 
                            QProgressBar, QFrame, QGroupBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont
from typing import Dict, Any
from ..config.settings import Settings
from ..api.client import APIClient
from ..utils.crypto import CryptoManager

class RegisterThread(QThread):
    """Thread for registration process"""
    finished = pyqtSignal(bool, dict)
    
    def __init__(self, server_url: str, username: str, email: str, password: str):
        super().__init__()
        self.server_url = server_url
        self.username = username
        self.email = email
        self.password = password
    
    def run(self):
        try:
            client = APIClient(self.server_url)
            success, response = client.register(self.username, self.email, self.password)
            self.finished.emit(success, response)
        except Exception as e:
            self.finished.emit(False, {"error": str(e)})

class RegisterDialog(QDialog):
    """Registration dialog"""
    
    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("zPass - Create Account")
        self.setModal(True)
        self.setFixedSize(450, 500)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Create Account")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        subtitle_label = QLabel("Join zPass to secure your passwords")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: gray; font-size: 12px;")
        layout.addWidget(subtitle_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Server info
        server_info = self.settings.get_current_server_info()
        server_label = QLabel(f"Server: {server_info['name']}")
        server_label.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(server_label)
        
        # Registration Form
        form_group = QGroupBox("Account Information")
        form_layout = QFormLayout(form_group)
        
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Enter your username")
        self.username_edit.textChanged.connect(self.validate_form)
        form_layout.addRow("Username:", self.username_edit)
        
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Enter your email")
        self.email_edit.textChanged.connect(self.validate_form)
        form_layout.addRow("Email:", self.email_edit)
        
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Enter your master password")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.textChanged.connect(self.validate_form)
        form_layout.addRow("Password:", self.password_edit)
        
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setPlaceholderText("Confirm your password")
        self.confirm_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_edit.textChanged.connect(self.validate_form)
        form_layout.addRow("Confirm Password:", self.confirm_password_edit)
        
        layout.addWidget(form_group)
        
        # Password strength indicator
        self.strength_label = QLabel()
        self.strength_label.setVisible(False)
        layout.addWidget(self.strength_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)
        
        # Warning
        warning_label = QLabel(
            "⚠️ Important: Your master password cannot be recovered. "
            "Make sure to remember it or store it in a safe place."
        )
        warning_label.setWordWrap(True)
        warning_label.setStyleSheet("color: orange; font-size: 11px; padding: 10px; background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 4px;")
        layout.addWidget(warning_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        button_layout.addStretch()
        
        self.register_btn = QPushButton("Create Account")
        self.register_btn.setDefault(True)
        self.register_btn.clicked.connect(self.register)
        self.register_btn.setEnabled(False)
        button_layout.addWidget(self.register_btn)
        
        layout.addLayout(button_layout)
        
        # Connect Enter key
        self.confirm_password_edit.returnPressed.connect(self.register)
    
    def validate_form(self):
        """Validate form inputs"""
        username = self.username_edit.text().strip()
        email = self.email_edit.text().strip()
        password = self.password_edit.text()
        confirm_password = self.confirm_password_edit.text()
        
        # Basic validation
        valid = bool(username and email and password and confirm_password)
        
        if valid:
            # Username validation
            if len(username) < 3:
                valid = False
            
            # Email validation
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                valid = False
            
            # Password validation
            if len(password) < 8:
                valid = False
            
            # Password confirmation
            if password != confirm_password:
                valid = False
        
        self.register_btn.setEnabled(valid)
        
        # Update password strength
        if password:
            self.update_password_strength(password)
        else:
            self.strength_label.setVisible(False)
    
    def update_password_strength(self, password: str):
        """Update password strength indicator"""
        score, description, suggestions = CryptoManager.check_password_strength(password)
        
        # Color based on strength
        if score >= 80:
            color = "green"
        elif score >= 60:
            color = "orange"
        elif score >= 40:
            color = "yellow"
        else:
            color = "red"
        
        strength_text = f"Password Strength: {description} ({score}/100)"
        if suggestions:
            strength_text += f"\\nSuggestions: {', '.join(suggestions[:3])}"
        
        self.strength_label.setText(strength_text)
        self.strength_label.setStyleSheet(f"color: {color}; font-size: 11px;")
        self.strength_label.setVisible(True)
    
    def register(self):
        """Perform registration"""
        username = self.username_edit.text().strip()
        email = self.email_edit.text().strip()
        password = self.password_edit.text()
        confirm_password = self.confirm_password_edit.text()
        
        # Final validation
        if not username or not email or not password:
            self.show_status("Please fill in all fields", "red")
            return
        
        if password != confirm_password:
            self.show_status("Passwords do not match", "red")
            return
        
        if len(password) < 8:
            self.show_status("Password must be at least 8 characters long", "red")
            return
        
        # Start registration process
        self.set_ui_enabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.show_status("Creating account...", "blue")
        
        server_url = self.settings.get_current_server_url()
        
        self.register_thread = RegisterThread(server_url, username, email, password)
        self.register_thread.finished.connect(self.on_register_finished)
        self.register_thread.start()
    
    def on_register_finished(self, success: bool, response: Dict[str, Any]):
        """Handle registration result"""
        self.set_ui_enabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            self.show_status("Account created successfully!", "green")
            QTimer.singleShot(2000, self.accept)
        else:
            error_msg = response.get('error', 'Registration failed')
            self.show_status(f"Registration failed: {error_msg}", "red")
    
    def show_status(self, message: str, color: str):
        """Show status message"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {color};")
        self.status_label.setVisible(True)
    
    def set_ui_enabled(self, enabled: bool):
        """Enable/disable UI elements"""
        self.username_edit.setEnabled(enabled)
        self.email_edit.setEnabled(enabled)
        self.password_edit.setEnabled(enabled)
        self.confirm_password_edit.setEnabled(enabled)
        self.register_btn.setEnabled(enabled and self.register_btn.isEnabled())
        self.cancel_btn.setEnabled(enabled)
