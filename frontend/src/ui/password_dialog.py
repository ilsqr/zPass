"""
Password Add/Edit Dialog
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QLineEdit, QPushButton, QLabel, QTextEdit, 
                            QComboBox, QCheckBox, QSpinBox, QGroupBox,
                            QMessageBox, QTabWidget, QWidget, QSlider,
                            QProgressBar)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Dict, Any, Optional, List
import secrets
import string
import re
from datetime import datetime
from ..utils.crypto import CryptoManager
from ..config.settings import Settings

class PasswordGeneratorWidget(QWidget):
    """Password generator widget"""
    
    password_generated = pyqtSignal(str)
    
    def __init__(self, settings=None):
        super().__init__()
        self.settings = settings
        self.setup_ui()
        self.load_defaults()
    
    def load_defaults(self):
        """Load default values from settings"""
        if self.settings:
            self.length_slider.setValue(self.settings.get_default_password_length())
            self.uppercase_cb.setChecked(self.settings.get_include_uppercase())
            self.lowercase_cb.setChecked(self.settings.get_include_lowercase())
            self.numbers_cb.setChecked(self.settings.get_include_numbers())
            self.symbols_cb.setChecked(self.settings.get_include_symbols())
            self.update_length_label(self.length_slider.value())
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Length setting
        length_layout = QHBoxLayout()
        length_layout.addWidget(QLabel("Length:"))
        
        self.length_slider = QSlider(Qt.Orientation.Horizontal)
        self.length_slider.setMinimum(8)
        self.length_slider.setMaximum(64)
        self.length_slider.setValue(16)
        self.length_slider.valueChanged.connect(self.update_length_label)
        length_layout.addWidget(self.length_slider)
        
        self.length_label = QLabel("16")
        length_layout.addWidget(self.length_label)
        
        layout.addLayout(length_layout)
        
        # Character options
        options_group = QGroupBox("Character Options")
        options_layout = QVBoxLayout(options_group)
        
        self.uppercase_cb = QCheckBox("Uppercase letters (A-Z)")
        self.uppercase_cb.setChecked(True)
        options_layout.addWidget(self.uppercase_cb)
        
        self.lowercase_cb = QCheckBox("Lowercase letters (a-z)")
        self.lowercase_cb.setChecked(True)
        options_layout.addWidget(self.lowercase_cb)
        
        self.numbers_cb = QCheckBox("Numbers (0-9)")
        self.numbers_cb.setChecked(True)
        options_layout.addWidget(self.numbers_cb)
        
        self.symbols_cb = QCheckBox("Symbols (!@#$%^&*)")
        self.symbols_cb.setChecked(True)
        options_layout.addWidget(self.symbols_cb)
        
        self.exclude_ambiguous_cb = QCheckBox("Exclude ambiguous characters (0, O, l, I)")
        self.exclude_ambiguous_cb.setChecked(False)
        options_layout.addWidget(self.exclude_ambiguous_cb)
        
        layout.addWidget(options_group)
        
        # Generated password display
        password_layout = QVBoxLayout()
        password_layout.addWidget(QLabel("Generated Password:"))
        
        self.password_display = QLineEdit()
        self.password_display.setReadOnly(True)
        self.password_display.setFont(QFont("Consolas", 12))
        password_layout.addWidget(self.password_display)
        
        # Password strength
        self.strength_bar = QProgressBar()
        self.strength_bar.setMaximum(100)
        password_layout.addWidget(self.strength_bar)
        
        self.strength_label = QLabel()
        password_layout.addWidget(self.strength_label)
        
        layout.addLayout(password_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        generate_btn = QPushButton("Generate Password")
        generate_btn.clicked.connect(self.generate_password)
        button_layout.addWidget(generate_btn)
        
        use_btn = QPushButton("Use This Password")
        use_btn.clicked.connect(self.use_password)
        button_layout.addWidget(use_btn)
        
        layout.addLayout(button_layout)
        
        # Generate initial password
        self.generate_password()
    
    def update_length_label(self, value):
        """Update length label"""
        self.length_label.setText(str(value))
    
    def generate_password(self):
        """Generate a new password"""
        length = self.length_slider.value()
        
        # Build character set
        chars = ""
        if self.uppercase_cb.isChecked():
            chars += string.ascii_uppercase
        if self.lowercase_cb.isChecked():
            chars += string.ascii_lowercase
        if self.numbers_cb.isChecked():
            chars += string.digits
        if self.symbols_cb.isChecked():
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # Exclude ambiguous characters if requested
        if self.exclude_ambiguous_cb.isChecked():
            ambiguous = "0Ol1I"
            chars = ''.join(c for c in chars if c not in ambiguous)
        
        if not chars:
            chars = string.ascii_letters + string.digits
        
        # Generate password
        password = ''.join(secrets.choice(chars) for _ in range(length))
        self.password_display.setText(password)
        
        # Update strength indicator
        score, description, suggestions = CryptoManager.check_password_strength(password)
        self.strength_bar.setValue(score)
        
        if score >= 80:
            color = "green"
        elif score >= 60:
            color = "orange"
        else:
            color = "red"
        
        self.strength_label.setText(f"{description} ({score}/100)")
        self.strength_label.setStyleSheet(f"color: {color};")
    
    def use_password(self):
        """Emit signal to use the generated password"""
        password = self.password_display.text()
        if password:
            self.password_generated.emit(password)

class PasswordDialog(QDialog):
    """Dialog for adding/editing passwords"""
    
    def __init__(self, categories: List[str], password_data: Optional[Dict[str, Any]] = None, parent=None, settings=None):
        super().__init__(parent)
        self.categories = categories
        self.password_data = password_data
        self.settings = settings
        self.is_edit_mode = password_data is not None
        
        self.setWindowTitle("Edit Password" if self.is_edit_mode else "Add Password")
        self.setModal(True)
        self.setMinimumSize(500, 600)
        
        self.setup_ui()
        
        if self.is_edit_mode:
            self.load_password_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = "Edit Password" if self.is_edit_mode else "Add New Password"
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # Password details tab
        details_tab = QWidget()
        self.setup_details_tab(details_tab)
        self.tabs.addTab(details_tab, "Password Details")
        
        # Password generator tab
        generator_tab = PasswordGeneratorWidget(self.settings)
        generator_tab.password_generated.connect(self.use_generated_password)
        self.tabs.addTab(generator_tab, "Password Generator")
        
        layout.addWidget(self.tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        button_layout.addStretch()
        
        self.save_btn = QPushButton("Update" if self.is_edit_mode else "Save")
        self.save_btn.setDefault(True)
        self.save_btn.clicked.connect(self.save_password)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
    
    def setup_details_tab(self, tab):
        """Setup password details tab"""
        layout = QVBoxLayout(tab)
        
        # Basic information group
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout(basic_group)
        
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("e.g., Gmail Account")
        basic_layout.addRow("Title*:", self.title_edit)
        
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Username or email")
        basic_layout.addRow("Username:", self.username_edit)
        
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Email address")
        basic_layout.addRow("Email:", self.email_edit)
        
        # Password field with show/hide and strength
        password_layout = QHBoxLayout()
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Enter password")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.textChanged.connect(self.update_password_strength)
        password_layout.addWidget(self.password_edit)
        
        self.show_password_btn = QPushButton("👁")
        self.show_password_btn.setMaximumWidth(40)
        self.show_password_btn.setCheckable(True)
        self.show_password_btn.clicked.connect(self.toggle_password_visibility)
        password_layout.addWidget(self.show_password_btn)
        
        basic_layout.addRow("Password*:", password_layout)
        
        # Password strength indicator
        self.password_strength_bar = QProgressBar()
        self.password_strength_bar.setMaximum(100)
        basic_layout.addRow("Strength:", self.password_strength_bar)
        
        self.password_strength_label = QLabel()
        basic_layout.addRow("", self.password_strength_label)
        
        layout.addWidget(basic_group)
        
        # Website and category group
        website_group = QGroupBox("Website & Category")
        website_layout = QFormLayout(website_group)
        
        self.website_edit = QLineEdit()
        self.website_edit.setPlaceholderText("https://example.com")
        website_layout.addRow("Website:", self.website_edit)
        
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.addItems([""] + self.categories)
        website_layout.addRow("Category:", self.category_combo)
        
        layout.addWidget(website_group)
        
        # Additional information group
        additional_group = QGroupBox("Additional Information")
        additional_layout = QFormLayout(additional_group)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Additional notes or information...")
        self.notes_edit.setMaximumHeight(100)
        additional_layout.addRow("Notes:", self.notes_edit)
        
        # Tags
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("work, personal, important (comma separated)")
        additional_layout.addRow("Tags:", self.tags_edit)
        
        layout.addWidget(additional_group)
        
        # Security options group
        security_group = QGroupBox("Security Options")
        security_layout = QVBoxLayout(security_group)
        
        self.favorite_cb = QCheckBox("Mark as favorite")
        security_layout.addWidget(self.favorite_cb)
        
        self.require_reprompt_cb = QCheckBox("Require master password re-prompt")
        security_layout.addWidget(self.require_reprompt_cb)
        
        layout.addWidget(security_group)
    
    def load_password_data(self):
        """Load existing password data into form"""
        if not self.password_data:
            return
        
        self.title_edit.setText(self.password_data.get('title', ''))
        self.username_edit.setText(self.password_data.get('username', ''))
        self.email_edit.setText(self.password_data.get('email', ''))
        self.password_edit.setText(self.password_data.get('password', ''))
        self.website_edit.setText(self.password_data.get('website', ''))
        self.notes_edit.setPlainText(self.password_data.get('notes', ''))
        self.tags_edit.setText(self.password_data.get('tags', ''))
        
        # Set category
        category = self.password_data.get('category', '')
        index = self.category_combo.findText(category)
        if index >= 0:
            self.category_combo.setCurrentIndex(index)
        else:
            self.category_combo.setCurrentText(category)
        
        # Set checkboxes
        self.favorite_cb.setChecked(self.password_data.get('favorite', False))
        self.require_reprompt_cb.setChecked(self.password_data.get('require_reprompt', False))
        
        # Update password strength
        self.update_password_strength()
    
    def update_password_strength(self):
        """Update password strength indicator"""
        password = self.password_edit.text()
        if not password:
            self.password_strength_bar.setValue(0)
            self.password_strength_label.setText("")
            return
        
        score, description, suggestions = CryptoManager.check_password_strength(password)
        self.password_strength_bar.setValue(score)
        
        if score >= 80:
            color = "green"
        elif score >= 60:
            color = "orange"
        else:
            color = "red"
        
        strength_text = f"{description} ({score}/100)"
        if suggestions and score < 80:
            strength_text += f"\nSuggestions: {', '.join(suggestions[:2])}"
        
        self.password_strength_label.setText(strength_text)
        self.password_strength_label.setStyleSheet(f"color: {color}; font-size: 11px;")
    
    def toggle_password_visibility(self):
        """Toggle password field visibility"""
        if self.show_password_btn.isChecked():
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_password_btn.setText("🙈")
        else:
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_password_btn.setText("👁")
    
    def use_generated_password(self, password: str):
        """Use generated password"""
        self.password_edit.setText(password)
        self.tabs.setCurrentIndex(0)  # Switch back to details tab
        QMessageBox.information(self, "Password Set", "Generated password has been set!")
    
    def validate_form(self) -> bool:
        """Validate form data"""
        if not self.title_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Title is required.")
            self.title_edit.setFocus()
            return False
        
        if not self.password_edit.text():
            QMessageBox.warning(self, "Validation Error", "Password is required.")
            self.password_edit.setFocus()
            return False
        
        # Validate email if provided
        email = self.email_edit.text().strip()
        if email:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                QMessageBox.warning(self, "Validation Error", "Invalid email format.")
                self.email_edit.setFocus()
                return False
        
        # Validate website URL if provided
        website = self.website_edit.text().strip()
        if website and not website.startswith(('http://', 'https://')):
            reply = QMessageBox.question(
                self, "Website URL", 
                "Website URL doesn't start with http:// or https://. Add https:// automatically?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.website_edit.setText(f"https://{website}")
        
        return True
    
    def save_password(self):
        """Save password data"""
        if not self.validate_form():
            return
        
        # Create password data dictionary
        password_data = {
            'id': self.password_data.get('id') if self.password_data else None,
            'title': self.title_edit.text().strip(),
            'username': self.username_edit.text().strip(),
            'email': self.email_edit.text().strip(),
            'password': self.password_edit.text(),
            'website': self.website_edit.text().strip(),
            'category': self.category_combo.currentText().strip(),
            'notes': self.notes_edit.toPlainText().strip(),
            'tags': self.tags_edit.text().strip(),
            'favorite': self.favorite_cb.isChecked(),
            'require_reprompt': self.require_reprompt_cb.isChecked(),
            'created_at': self.password_data.get('created_at') if self.password_data else datetime.now().isoformat(),
            'modified_at': datetime.now().isoformat()
        }
        
        self.password_data = password_data
        self.accept()
    
    def get_password_data(self) -> Dict[str, Any]:
        """Get the password data"""
        return self.password_data
