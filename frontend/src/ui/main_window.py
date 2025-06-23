"""
Main application window
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QSplitter, QTreeWidget, QTreeWidgetItem, QLineEdit,
                            QPushButton, QLabel, QFrame, QMenuBar, QMenu, 
                            QStatusBar, QMessageBox, QInputDialog, QHeaderView,
                            QTableWidget, QTableWidgetItem, QTextEdit, QCheckBox,
                            QSpinBox, QGroupBox, QFormLayout, QComboBox, QTabWidget,
                            QDialog, QApplication, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QAction, QFont, QIcon, QKeySequence
from typing import Dict, Any, Optional, List
import json
import uuid
import sys
import platform
from ..config.settings import Settings
from ..api.client import APIClient
from ..utils.crypto import CryptoManager
from .login_dialog import LoginDialog
from .password_dialog import PasswordDialog
from .settings_dialog import SettingsDialog

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
        user32 = ctypes.windll.user32
        
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

class VaultSyncThread(QThread):
    """Thread for syncing vault data"""
    finished = pyqtSignal(bool, dict)
    
    def __init__(self, api_client: APIClient, encrypted_data: str = None, salt: str = None):
        super().__init__()
        self.api_client = api_client
        self.encrypted_data = encrypted_data
        self.salt = salt
        self.is_upload = encrypted_data is not None
    
    def run(self):
        try:
            if self.is_upload:
                # Upload vault data
                success, response = self.api_client.update_vault(self.encrypted_data, self.salt)
            else:
                # Download vault data
                success, response = self.api_client.get_vault()
            
            self.finished.emit(success, response)
        except Exception as e:
            self.finished.emit(False, {"error": str(e)})

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.api_client = None
        self.user_data = None
        self.master_password = None
        self.vault_data = {"passwords": [], "notes": [], "categories": []}
        self.is_vault_modified = False
        
        self.setWindowTitle("zPass - Password Manager")
        self.setMinimumSize(1000, 700)
        self.setObjectName("MainWindow")
        
        # Auto-lock timer
        self.auto_lock_timer = QTimer()
        self.auto_lock_timer.setSingleShot(True)
        self.auto_lock_timer.timeout.connect(self.auto_lock)
        
        self.setup_ui()
        self.apply_settings()  # Apply initial settings
        self.restore_window_state()
        self.show_login_dialog()
    
    def setup_ui(self):
        """Setup the main UI"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Setup menu bar
        self.setup_menu_bar()
        
        # Setup toolbar
        self.setup_toolbar()
        
        # Create main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setObjectName("MainSplitter")
        
        # Left panel (categories/search)
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel (password list/details)
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([250, 750])
        
        main_layout.addWidget(splitter)
        
        # Setup status bar
        self.setup_status_bar()
        
        # Initially lock the UI
        self.set_ui_locked(True)
    
    def setup_menu_bar(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        sync_action = QAction("Sync Vault", self)
        sync_action.setShortcut(QKeySequence("Ctrl+S"))
        sync_action.triggered.connect(self.sync_vault)
        file_menu.addAction(sync_action)
        
        file_menu.addSeparator()
        
        logout_action = QAction("Logout", self)
        logout_action.setShortcut(QKeySequence("Ctrl+L"))
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        add_password_action = QAction("Add Password", self)
        add_password_action.setShortcut(QKeySequence("Ctrl+N"))
        add_password_action.triggered.connect(self.add_password)
        edit_menu.addAction(add_password_action)
        
        generate_password_action = QAction("Generate Password", self)
        generate_password_action.setShortcut(QKeySequence("Ctrl+G"))
        generate_password_action.triggered.connect(self.generate_password)
        edit_menu.addAction(generate_password_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        refresh_action = QAction("Refresh", self)
        refresh_action.setShortcut(QKeySequence("F5"))
        refresh_action.triggered.connect(self.refresh_vault)
        view_menu.addAction(refresh_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_toolbar(self):
        """Setup toolbar"""
        toolbar = self.addToolBar("Main")
        toolbar.setObjectName("MainToolBar")
        
        # Add password button
        add_btn = QPushButton("Add Password")
        add_btn.clicked.connect(self.add_password)
        toolbar.addWidget(add_btn)
        
        toolbar.addSeparator()
        
        # Generate password button
        generate_btn = QPushButton("Generate")
        generate_btn.clicked.connect(self.generate_password)
        toolbar.addWidget(generate_btn)
        
        toolbar.addSeparator()
        
        # Sync button
        sync_btn = QPushButton("Sync")
        sync_btn.clicked.connect(self.sync_vault)
        toolbar.addWidget(sync_btn)
        
        # Add stretch
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)
        
        # Lock button
        lock_btn = QPushButton("Lock")
        lock_btn.clicked.connect(self.lock_vault)
        toolbar.addWidget(lock_btn)
    
    def create_left_panel(self) -> QWidget:
        """Create left panel with search and categories"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Search
        search_group = QGroupBox("Search")
        search_layout = QVBoxLayout(search_group)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search passwords...")
        self.search_edit.setObjectName("SearchEdit")
        self.search_edit.textChanged.connect(self.filter_passwords)
        search_layout.addWidget(self.search_edit)
        
        layout.addWidget(search_group)
        
        # Categories
        categories_group = QGroupBox("Categories")
        categories_layout = QVBoxLayout(categories_group)
        
        self.categories_tree = QTreeWidget()
        self.categories_tree.setHeaderHidden(True)
        self.categories_tree.setObjectName("CategoriesTree")
        self.categories_tree.itemClicked.connect(self.on_category_selected)
        categories_layout.addWidget(self.categories_tree)
        
        layout.addWidget(categories_group)
        
        return panel
    
    def create_right_panel(self) -> QWidget:
        """Create right panel with password list and details"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Password list
        list_group = QGroupBox("Passwords")
        list_layout = QVBoxLayout(list_group)
        
        self.password_table = QTableWidget()
        self.password_table.setColumnCount(4)
        self.password_table.setHorizontalHeaderLabels(["Title", "Username", "Website", "Modified"])
        self.password_table.setObjectName("PasswordTable")
        self.password_table.horizontalHeader().setStretchLastSection(True)
        self.password_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.password_table.itemSelectionChanged.connect(self.on_password_selected)
        self.password_table.itemDoubleClicked.connect(self.edit_password)
        
        list_layout.addWidget(self.password_table)
        
        layout.addWidget(list_group)
        
        # Details panel
        details_group = QGroupBox("Details")
        details_layout = QVBoxLayout(details_group)
        
        self.details_tabs = QTabWidget()
        
        # Password details tab
        password_tab = QWidget()
        password_layout = QFormLayout(password_tab)
        
        self.title_display = QLabel()
        self.username_display = QLabel()
        self.password_display = QLabel("••••••••••••")
        self.website_display = QLabel()
        self.notes_display = QTextEdit()
        self.notes_display.setMaximumHeight(100)
        self.notes_display.setReadOnly(True)
        
        password_layout.addRow("Title:", self.title_display)
        password_layout.addRow("Username:", self.username_display)
        password_layout.addRow("Password:", self.password_display)
        password_layout.addRow("Website:", self.website_display)
        password_layout.addRow("Notes:", self.notes_display)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.copy_password_btn = QPushButton("Copy Password")
        self.copy_password_btn.clicked.connect(self.copy_password)
        button_layout.addWidget(self.copy_password_btn)
        
        self.show_password_btn = QPushButton("Show/Hide")
        self.show_password_btn.clicked.connect(self.toggle_password_visibility)
        button_layout.addWidget(self.show_password_btn)
        
        self.edit_password_btn = QPushButton("Edit")
        self.edit_password_btn.clicked.connect(self.edit_password)
        button_layout.addWidget(self.edit_password_btn)
        
        self.delete_password_btn = QPushButton("Delete")
        self.delete_password_btn.clicked.connect(self.delete_password)
        button_layout.addWidget(self.delete_password_btn)
        
        password_layout.addRow(button_layout)
        
        self.details_tabs.addTab(password_tab, "Password Details")
        
        details_layout.addWidget(self.details_tabs)
        
        layout.addWidget(details_group)
        
        return panel
    
    def setup_status_bar(self):
        """Setup status bar"""
        self.status_bar = QStatusBar()
        self.status_bar.setObjectName("MainStatusBar")
        self.setStatusBar(self.status_bar)
        
        # Server info
        self.server_label = QLabel()
        self.server_label.setObjectName("ServerLabel")
        self.status_bar.addPermanentWidget(self.server_label)
        
        # Sync status
        self.sync_label = QLabel()
        self.sync_label.setObjectName("SyncLabel")
        self.status_bar.addPermanentWidget(self.sync_label)
    
    def show_login_dialog(self):
        """Show login dialog"""
        dialog = LoginDialog(self.settings, self)
        dialog.login_successful.connect(self.on_login_successful)
        
        if dialog.exec() != QDialog.DialogCode.Accepted:
            self.close()
    
    def on_login_successful(self, user_data: Dict[str, Any], api_client: APIClient):
        """Handle successful login"""
        self.user_data = user_data
        self.api_client = api_client
        
        # Update status bar
        server_info = self.settings.get_current_server_info()
        self.server_label.setText(f"Server: {server_info['name']}")
        
        # Prompt for master password
        password, ok = QInputDialog.getText(
            self, "Master Password", 
            "Enter your master password to decrypt vault:",
            QLineEdit.EchoMode.Password
        )
        
        if ok and password:
            self.master_password = password
            self.set_ui_locked(False)
            self.refresh_vault()
            self.start_auto_lock_timer()
        else:
            self.logout()
    
    def set_ui_locked(self, locked: bool):
        """Lock/unlock UI"""
        # Enable/disable all UI elements
        self.centralWidget().setEnabled(not locked)
        
        if locked:
            self.setWindowTitle("zPass - Password Manager (Locked)")
        else:
            username = self.user_data.get('username', 'User') if self.user_data else 'User'
            self.setWindowTitle(f"zPass - Password Manager ({username})")
    
    def start_auto_lock_timer(self):
        """Start auto-lock timer"""
        timeout = self.settings.get_auto_lock_timeout() * 60 * 1000  # Convert to milliseconds
        if timeout > 0:
            self.auto_lock_timer.start(timeout)
    
    def auto_lock(self):
        """Auto-lock the vault"""
        self.lock_vault()
    
    def lock_vault(self):
        """Lock the vault"""
        self.master_password = None
        self.vault_data = {"passwords": [], "notes": [], "categories": []}
        self.set_ui_locked(True)
        self.clear_ui()
        
        # Show login dialog again
        self.show_login_dialog()
    
    def logout(self):
        """Logout from the application"""
        if self.api_client:
            self.api_client.logout()
        
        self.api_client = None
        self.user_data = None
        self.master_password = None
        self.vault_data = {"passwords": [], "notes": [], "categories": []}
        self.set_ui_locked(True)
        self.clear_ui()
        
        # Show login dialog
        self.show_login_dialog()
    
    def clear_ui(self):
        """Clear UI elements"""
        self.password_table.setRowCount(0)
        self.categories_tree.clear()
        self.search_edit.clear()
        
        # Clear details
        self.clear_password_details()
    
    def clear_password_details(self):
        """Clear password details panel"""
        self.title_display.clear()
        self.username_display.clear()
        self.password_display.setText("••••••••••••")
        self.website_display.clear()
        self.notes_display.clear()
        
        if hasattr(self, 'current_password'):
            delattr(self, 'current_password')
    
    def refresh_vault(self):
        """Refresh vault data from server"""
        if not self.api_client or not self.master_password:
            return
        
        self.sync_label.setText("Syncing...")
        
        # Download vault data
        self.sync_thread = VaultSyncThread(self.api_client)
        self.sync_thread.finished.connect(self.on_vault_downloaded)
        self.sync_thread.start()
    
    def on_vault_downloaded(self, success: bool, response: Dict[str, Any]):
        """Handle vault download result"""
        self.sync_label.setText("")
        
        if success:
            vault_data = response.get('vault', {})
            encrypted_data = vault_data.get('encrypted_data')
            salt = vault_data.get('salt')
            
            if encrypted_data and salt:
                try:
                    # Decrypt vault data
                    self.vault_data = CryptoManager.decrypt_data(encrypted_data, salt, self.master_password)
                    self.load_vault_data()
                    self.sync_label.setText("✅ Synced")
                except Exception as e:
                    QMessageBox.warning(self, "Decryption Error", f"Failed to decrypt vault: {str(e)}")
            else:
                # Empty vault
                self.vault_data = {"passwords": [], "notes": [], "categories": []}
                self.load_vault_data()
                self.sync_label.setText("✅ Synced (Empty)")
        else:
            error_msg = response.get('error', 'Unknown error')
            QMessageBox.warning(self, "Sync Error", f"Failed to sync vault: {error_msg}")
    
    def load_vault_data(self):
        """Load vault data into UI"""
        # Load categories
        self.load_categories()
        
        # Load passwords
        self.load_passwords()
    
    def load_categories(self):
        """Load categories into tree"""
        self.categories_tree.clear()
        
        # Add default categories
        all_item = QTreeWidgetItem(["All Passwords"])
        all_item.setData(0, Qt.ItemDataRole.UserRole, "all")
        self.categories_tree.addTopLevelItem(all_item)
        
        # Add custom categories
        categories = self.vault_data.get('categories', [])
        for category in categories:
            item = QTreeWidgetItem([category])
            item.setData(0, Qt.ItemDataRole.UserRole, category)
            self.categories_tree.addTopLevelItem(item)
        
        # Select "All Passwords" by default
        self.categories_tree.setCurrentItem(all_item)
    
    def load_passwords(self):
        """Load passwords into table"""
        passwords = self.vault_data.get('passwords', [])
        
        self.password_table.setRowCount(len(passwords))
        
        for i, password_data in enumerate(passwords):
            self.password_table.setItem(i, 0, QTableWidgetItem(password_data.get('title', '')))
            self.password_table.setItem(i, 1, QTableWidgetItem(password_data.get('username', '')))
            self.password_table.setItem(i, 2, QTableWidgetItem(password_data.get('website', '')))
            self.password_table.setItem(i, 3, QTableWidgetItem(password_data.get('modified', '')))
    
    def filter_passwords(self):
        """Filter passwords based on search term"""
        search_term = self.search_edit.text().lower()
        
        for i in range(self.password_table.rowCount()):
            match = False
            for j in range(self.password_table.columnCount()):
                item = self.password_table.item(i, j)
                if item and search_term in item.text().lower():
                    match = True
                    break
            
            self.password_table.setRowHidden(i, not match)
    
    def on_category_selected(self, item: QTreeWidgetItem):
        """Handle category selection"""
        category = item.data(0, Qt.ItemDataRole.UserRole)
        
        if category == "all":
            # Show all passwords
            for i in range(self.password_table.rowCount()):
                self.password_table.setRowHidden(i, False)
        else:
            # Filter by category
            passwords = self.vault_data.get('passwords', [])
            for i, password_data in enumerate(passwords):
                if i < self.password_table.rowCount():
                    match = password_data.get('category') == category
                    self.password_table.setRowHidden(i, not match)
    
    def on_password_selected(self):
        """Handle password selection"""
        current_row = self.password_table.currentRow()
        if current_row >= 0:
            passwords = self.vault_data.get('passwords', [])
            if current_row < len(passwords):
                password_data = passwords[current_row]
                self.display_password_details(password_data)
    
    def display_password_details(self, password_data: Dict[str, Any]):
        """Display password details"""
        self.title_display.setText(password_data.get('title', ''))
        self.username_display.setText(password_data.get('username', ''))
        self.website_display.setText(password_data.get('website', ''))
        self.notes_display.setPlainText(password_data.get('notes', ''))
        
        # Store password for copy/show functions
        self.current_password = password_data.get('password', '')
        self.password_display.setText("••••••••••••")
    
    def copy_password(self):
        """Copy password to clipboard"""
        if hasattr(self, 'current_password'):
            QApplication.clipboard().setText(self.current_password)
            self.status_bar.showMessage("Password copied to clipboard", 2000)
    
    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if hasattr(self, 'current_password'):
            if self.password_display.text() == "••••••••••••":
                self.password_display.setText(self.current_password)
            else:
                self.password_display.setText("••••••••••••")
    
    def add_password(self):
        """Add new password"""
        if not self.master_password:
            return
        
        categories = self.vault_data.get('categories', [])
        dialog = PasswordDialog(categories, parent=self, settings=self.settings)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            password_data = dialog.get_password_data()
            
            # Generate unique ID
            password_data['id'] = str(uuid.uuid4())
            
            # Add to vault data
            if 'passwords' not in self.vault_data:
                self.vault_data['passwords'] = []
            
            self.vault_data['passwords'].append(password_data)
            
            # Add new category if it doesn't exist
            category = password_data.get('category', '').strip()
            if category and category not in categories:
                if 'categories' not in self.vault_data:
                    self.vault_data['categories'] = []
                self.vault_data['categories'].append(category)
                self.load_categories()
            
            # Mark as modified and reload
            self.is_vault_modified = True
            self.load_passwords()
            
            # Auto-sync if enabled
            self.sync_vault()
            
            self.status_bar.showMessage("Password added successfully", 3000)
    
    def edit_password(self):
        """Edit selected password"""
        current_row = self.password_table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "Edit Password", "Please select a password to edit.")
            return
        
        if not self.master_password:
            return
        
        passwords = self.vault_data.get('passwords', [])
        if current_row >= len(passwords):
            return
        
        password_data = passwords[current_row].copy()
        categories = self.vault_data.get('categories', [])
        
        dialog = PasswordDialog(categories, password_data, parent=self, settings=self.settings)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_data = dialog.get_password_data()
            
            # Update in vault data
            passwords[current_row] = updated_data
            
            # Add new category if it doesn't exist
            category = updated_data.get('category', '').strip()
            if category and category not in categories:
                if 'categories' not in self.vault_data:
                    self.vault_data['categories'] = []
                self.vault_data['categories'].append(category)
                self.load_categories()
            
            # Mark as modified and reload
            self.is_vault_modified = True
            self.load_passwords()
            
            # Auto-sync if enabled
            self.sync_vault()
            
            self.status_bar.showMessage("Password updated successfully", 3000)
    
    def delete_password(self):
        """Delete selected password"""
        current_row = self.password_table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "Delete Password", "Please select a password to delete.")
            return
        
        passwords = self.vault_data.get('passwords', [])
        if current_row >= len(passwords):
            return
        
        password_data = passwords[current_row]
        title = password_data.get('title', 'Unknown')
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete the password for '{title}'?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Remove from vault data
            del passwords[current_row]
            
            # Mark as modified and reload
            self.is_vault_modified = True
            self.load_passwords()
            
            # Clear details panel
            self.clear_password_details()
            
            # Auto-sync if enabled
            self.sync_vault()
            
            self.status_bar.showMessage(f"Password '{title}' deleted successfully", 3000)
    
    def generate_password(self):
        """Generate new password"""
        from .password_dialog import PasswordGeneratorWidget
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Password Generator")
        dialog.setModal(True)
        dialog.setFixedSize(450, 400)
        
        layout = QVBoxLayout(dialog)
        
        generator = PasswordGeneratorWidget(self.settings)
        layout.addWidget(generator)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)
        
        button_layout.addStretch()
        
        copy_btn = QPushButton("Copy to Clipboard")
        def copy_password():
            password = generator.password_display.text()
            if password:
                QApplication.clipboard().setText(password)
                self.status_bar.showMessage("Password copied to clipboard", 2000)
        
        copy_btn.clicked.connect(copy_password)
        button_layout.addWidget(copy_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def sync_vault(self):
        """Sync vault to server"""
        if not self.api_client or not self.master_password:
            return
        
        # Encrypt vault data
        try:
            encrypted_data, salt = CryptoManager.encrypt_data(self.vault_data, self.master_password)
            
            self.sync_label.setText("Syncing...")
            
            # Upload vault data
            self.sync_thread = VaultSyncThread(self.api_client, encrypted_data, salt)
            self.sync_thread.finished.connect(self.on_vault_uploaded)
            self.sync_thread.start()
            
        except Exception as e:
            QMessageBox.warning(self, "Encryption Error", f"Failed to encrypt vault: {str(e)}")
    
    def on_vault_uploaded(self, success: bool, response: Dict[str, Any]):
        """Handle vault upload result"""
        self.sync_label.setText("")
        
        if success:
            self.sync_label.setText("✅ Synced")
            self.is_vault_modified = False
        else:
            error_msg = response.get('error', 'Unknown error')
            QMessageBox.warning(self, "Sync Error", f"Failed to sync vault: {error_msg}")
    
    def show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self)
        dialog.settings_changed.connect(self.on_settings_changed)
        dialog.exec()
    
    def on_settings_changed(self):
        """Handle settings changes"""
        # Reload settings that affect the UI
        self.apply_settings()
        QMessageBox.information(self, "Settings", "Settings applied successfully!")
    
    def apply_settings(self):
        """Apply current settings to the UI"""
        # Apply theme
        theme = self.settings.get_theme()
        self.apply_theme(theme)
        
        # Apply font settings
        font_family = self.settings.get_font_family()
        font_size = self.settings.get_font_size()
        if font_family != "System Default":
            font = QFont(font_family, font_size)
            self.setFont(font)
    
    def apply_theme(self, theme: str):
        """Apply theme to the application"""
        is_dark_mode = theme == "Dark"
        
        if is_dark_mode:
            self.setStyleSheet("""
                QMainWindow { background-color: #2b2b2b; color: #ffffff; }
                QWidget { background-color: #2b2b2b; color: #ffffff; }
                QLineEdit { background-color: #3c3c3c; border: 1px solid #555; padding: 5px; }
                QPushButton { 
                    background-color: #0078d4; 
                    color: white; 
                    border: none; 
                    padding: 8px 16px; 
                    border-radius: 4px; 
                }
                QPushButton:hover { background-color: #106ebe; }
                QTableWidget { 
                    background-color: #3c3c3c; 
                    alternate-background-color: #424242;
                    gridline-color: #555;
                }
                QHeaderView::section { 
                    background-color: #505050; 
                    border: 1px solid #555; 
                    padding: 5px;
                }
                QGroupBox { 
                    font-weight: bold; 
                    border: 1px solid #555; 
                    margin: 5px 0px; 
                    padding-top: 10px;
                }
                QGroupBox::title { 
                    subcontrol-origin: margin; 
                    left: 10px; 
                    padding: 0px 5px;
                }
                QMenuBar {
                    background-color: #2b2b2b;
                    color: #ffffff;
                    border-bottom: 1px solid #555;
                }
                QMenuBar::item {
                    background-color: transparent;
                    padding: 5px 8px;
                }
                QMenuBar::item:selected {
                    background-color: #404040;
                }
                QMenu {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555;
                }
                QMenu::item {
                    padding: 5px 20px;
                }
                QMenu::item:selected {
                    background-color: #0078d4;
                }
                QStatusBar {
                    background-color: #2b2b2b;
                    color: #ffffff;
                    border-top: 1px solid #555;
                }
            """)
        elif theme == "Light":
            self.setStyleSheet("")  # Use default light theme
        
        # Windows title bar'ını ayarla
        if platform.system() == "Windows":
            try:
                hwnd = int(self.winId())
                set_window_dark_mode(hwnd, is_dark_mode)
            except:
                pass  # Hata durumunda sessizce devam et
        
        # System and Auto themes would require more complex implementation
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About zPass", 
                         "zPass v1.0.0\\n\\n"
                         "A secure, self-hostable password manager\\n"
                         "Built with PyQt6 and client-side encryption")
    
    def restore_window_state(self):
        """Restore window geometry and state"""
        geometry = self.settings.get_window_geometry()
        if geometry:
            self.restoreGeometry(geometry)
        
        state = self.settings.get_window_state()
        if state:
            self.restoreState(state)
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Save window state
        self.settings.set_window_geometry(self.saveGeometry())
        self.settings.set_window_state(self.saveState())
        
        # Check for unsaved changes
        if self.is_vault_modified:
            reply = QMessageBox.question(
                self, "Unsaved Changes", 
                "You have unsaved changes. Do you want to sync before closing?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.sync_vault()
                # TODO: Wait for sync to complete
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
        
        event.accept()
