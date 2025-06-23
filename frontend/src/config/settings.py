"""
Application settings and configuration management
"""

import os
import json
from typing import Dict, Any, Optional
from PyQt6.QtCore import QSettings

class Settings:
    """Application settings manager"""
    
    # Default server endpoints
    DEFAULT_SERVERS = {
        "official": {
            "name": "Official zPass Server",
            "url": "https://api.zpass.app",
            "description": "Official zPass cloud server"
        }
    }
    
    def __init__(self):
        self.qsettings = QSettings()
        self._servers = self._load_servers()
        self._current_server = self._get_current_server()
    
    def _load_servers(self) -> Dict[str, Dict[str, str]]:
        """Load server configurations"""
        # Start with default servers
        servers = self.DEFAULT_SERVERS.copy()
        
        # Load custom servers from settings
        custom_servers = self.qsettings.value("custom_servers", {})
        if isinstance(custom_servers, dict):
            servers.update(custom_servers)
        
        return servers
    
    def _get_current_server(self) -> str:
        """Get currently selected server"""
        return self.qsettings.value("current_server", "localhost")
    
    def get_servers(self) -> Dict[str, Dict[str, str]]:
        """Get all available servers"""
        # Always include localhost for development
        servers = self._servers.copy()
        servers["localhost"] = {
            "name": "Local Development",
            "url": "http://127.0.0.1:5000",
            "description": "Local development server"
        }
        return servers
    
    def get_current_server_url(self) -> str:
        """Get current server URL"""
        servers = self.get_servers()
        if self._current_server in servers:
            return servers[self._current_server]["url"]
        return "http://127.0.0.1:5000"  # Fallback to localhost
    
    def get_current_server_info(self) -> Dict[str, str]:
        """Get current server information"""
        servers = self.get_servers()
        if self._current_server in servers:
            return servers[self._current_server]
        return {
            "name": "Local Development",
            "url": "http://127.0.0.1:5000",
            "description": "Local development server"
        }
    
    def set_current_server(self, server_id: str) -> bool:
        """Set current server"""
        servers = self.get_servers()
        if server_id in servers:
            self._current_server = server_id
            self.qsettings.setValue("current_server", server_id)
            return True
        return False
    
    def add_custom_server(self, server_id: str, name: str, url: str, description: str = "") -> bool:
        """Add a custom server"""
        try:
            # Validate URL format
            if not url.startswith(('http://', 'https://')):
                return False
            
            custom_servers = self.qsettings.value("custom_servers", {})
            if not isinstance(custom_servers, dict):
                custom_servers = {}
            
            custom_servers[server_id] = {
                "name": name,
                "url": url.rstrip('/'),  # Remove trailing slash
                "description": description
            }
            
            self.qsettings.setValue("custom_servers", custom_servers)
            self._servers = self._load_servers()
            return True
        except Exception:
            return False
    
    def remove_custom_server(self, server_id: str) -> bool:
        """Remove a custom server"""
        try:
            custom_servers = self.qsettings.value("custom_servers", {})
            if isinstance(custom_servers, dict) and server_id in custom_servers:
                del custom_servers[server_id]
                self.qsettings.setValue("custom_servers", custom_servers)
                self._servers = self._load_servers()
                
                # If current server was removed, switch to localhost
                if self._current_server == server_id:
                    self.set_current_server("localhost")
                
                return True
            return False
        except Exception:
            return False
    
    def get_remember_credentials(self) -> bool:
        """Get remember credentials setting"""
        return self.qsettings.value("remember_credentials", False, bool)
    
    def set_remember_credentials(self, remember: bool):
        """Set remember credentials setting"""
        self.qsettings.setValue("remember_credentials", remember)
    
    def get_theme(self) -> str:
        """Get current theme"""
        return self.qsettings.value("theme", "light")
    
    def set_theme(self, theme: str):
        """Set current theme"""
        self.qsettings.setValue("theme", theme)
    
    def get_auto_lock_timeout(self) -> int:
        """Get auto lock timeout in minutes"""
        return self.qsettings.value("auto_lock_timeout", 15, int)
    
    def set_auto_lock_timeout(self, timeout: int):
        """Set auto lock timeout in minutes"""
        self.qsettings.setValue("auto_lock_timeout", timeout)
    
    def get_window_geometry(self) -> Optional[bytes]:
        """Get saved window geometry"""
        return self.qsettings.value("window_geometry")
    
    def set_window_geometry(self, geometry: bytes):
        """Set window geometry"""
        self.qsettings.setValue("window_geometry", geometry)
    
    def get_window_state(self) -> Optional[bytes]:
        """Get saved window state"""
        return self.qsettings.value("window_state")
    
    def set_window_state(self, state: bytes):
        """Set window state"""
        self.qsettings.setValue("window_state", state)
    
    # Appearance Settings
    def get_font_family(self) -> str:
        """Get font family"""
        return self.qsettings.value("font_family", "System Default")
    
    def set_font_family(self, font_family: str):
        """Set font family"""
        self.qsettings.setValue("font_family", font_family)
    
    def get_font_size(self) -> int:
        """Get font size"""
        return self.qsettings.value("font_size", 10, int)
    
    def set_font_size(self, font_size: int):
        """Set font size"""
        self.qsettings.setValue("font_size", font_size)
    
    def get_remember_window_state(self) -> bool:
        """Get remember window state setting"""
        return self.qsettings.value("remember_window_state", True, bool)
    
    def set_remember_window_state(self, remember: bool):
        """Set remember window state setting"""
        self.qsettings.setValue("remember_window_state", remember)
    
    def get_minimize_to_tray(self) -> bool:
        """Get minimize to tray setting"""
        return self.qsettings.value("minimize_to_tray", False, bool)
    
    def set_minimize_to_tray(self, minimize: bool):
        """Set minimize to tray setting"""
        self.qsettings.setValue("minimize_to_tray", minimize)
    
    def get_start_minimized(self) -> bool:
        """Get start minimized setting"""
        return self.qsettings.value("start_minimized", False, bool)
    
    def set_start_minimized(self, start_minimized: bool):
        """Set start minimized setting"""
        self.qsettings.setValue("start_minimized", start_minimized)
    
    # Security Settings
    def get_auto_lock_enabled(self) -> bool:
        """Get auto lock enabled setting"""
        return self.qsettings.value("auto_lock_enabled", True, bool)
    
    def set_auto_lock_enabled(self, enabled: bool):
        """Set auto lock enabled setting"""
        self.qsettings.setValue("auto_lock_enabled", enabled)
    
    def get_lock_on_minimize(self) -> bool:
        """Get lock on minimize setting"""
        return self.qsettings.value("lock_on_minimize", False, bool)
    
    def set_lock_on_minimize(self, lock: bool):
        """Set lock on minimize setting"""
        self.qsettings.setValue("lock_on_minimize", lock)
    
    def get_lock_on_focus_lost(self) -> bool:
        """Get lock on focus lost setting"""
        return self.qsettings.value("lock_on_focus_lost", False, bool)
    
    def set_lock_on_focus_lost(self, lock: bool):
        """Set lock on focus lost setting"""
        self.qsettings.setValue("lock_on_focus_lost", lock)
    
    # Password Generation Settings
    def get_default_password_length(self) -> int:
        """Get default password length"""
        return self.qsettings.value("default_password_length", 16, int)
    
    def set_default_password_length(self, length: int):
        """Set default password length"""
        self.qsettings.setValue("default_password_length", length)
    
    def get_include_uppercase(self) -> bool:
        """Get include uppercase setting"""
        return self.qsettings.value("include_uppercase", True, bool)
    
    def set_include_uppercase(self, include: bool):
        """Set include uppercase setting"""
        self.qsettings.setValue("include_uppercase", include)
    
    def get_include_lowercase(self) -> bool:
        """Get include lowercase setting"""
        return self.qsettings.value("include_lowercase", True, bool)
    
    def set_include_lowercase(self, include: bool):
        """Set include lowercase setting"""
        self.qsettings.setValue("include_lowercase", include)
    
    def get_include_numbers(self) -> bool:
        """Get include numbers setting"""
        return self.qsettings.value("include_numbers", True, bool)
    
    def set_include_numbers(self, include: bool):
        """Set include numbers setting"""
        self.qsettings.setValue("include_numbers", include)
    
    def get_include_symbols(self) -> bool:
        """Get include symbols setting"""
        return self.qsettings.value("include_symbols", True, bool)
    
    def set_include_symbols(self, include: bool):
        """Set include symbols setting"""
        self.qsettings.setValue("include_symbols", include)
    
    # Clipboard Settings
    def get_clear_clipboard(self) -> bool:
        """Get clear clipboard setting"""
        return self.qsettings.value("clear_clipboard", True, bool)
    
    def set_clear_clipboard(self, clear: bool):
        """Set clear clipboard setting"""
        self.qsettings.setValue("clear_clipboard", clear)
    
    def get_clipboard_timeout(self) -> int:
        """Get clipboard timeout in seconds"""
        return self.qsettings.value("clipboard_timeout", 30, int)
    
    def set_clipboard_timeout(self, timeout: int):
        """Set clipboard timeout in seconds"""
        self.qsettings.setValue("clipboard_timeout", timeout)
    
    # Sync Settings
    def get_server_type(self) -> str:
        """Get server type"""
        current_server = self.get_current_server_info()
        if current_server["url"] == "http://127.0.0.1:5000":
            return "Local (Localhost)"
        elif "zpass.app" in current_server["url"]:
            return "Official Server"
        else:
            return "Custom Server"
    
    def set_server_type(self, server_type: str):
        """Set server type"""
        if server_type == "Official Server":
            self.set_current_server("official")
        elif server_type == "Local (Localhost)":
            self.set_current_server("localhost")
        # For custom server, keep current selection
    
    def get_custom_server_url(self) -> str:
        """Get custom server URL"""
        current_info = self.get_current_server_info()
        if self.get_server_type() == "Custom Server":
            return current_info["url"]
        return ""
    
    def set_custom_server_url(self, url: str):
        """Set custom server URL"""
        if url.strip():
            self.add_custom_server("custom", "Custom Server", url.strip())
            self.set_current_server("custom")
    
    def get_auto_sync_enabled(self) -> bool:
        """Get auto sync enabled setting"""
        return self.qsettings.value("auto_sync_enabled", True, bool)
    
    def set_auto_sync_enabled(self, enabled: bool):
        """Set auto sync enabled setting"""
        self.qsettings.setValue("auto_sync_enabled", enabled)
    
    def get_sync_interval(self) -> int:
        """Get sync interval in minutes"""
        return self.qsettings.value("sync_interval", 5, int)
    
    def set_sync_interval(self, interval: int):
        """Set sync interval in minutes"""
        self.qsettings.setValue("sync_interval", interval)
    
    def get_sync_on_startup(self) -> bool:
        """Get sync on startup setting"""
        return self.qsettings.value("sync_on_startup", True, bool)
    
    def set_sync_on_startup(self, sync: bool):
        """Set sync on startup setting"""
        self.qsettings.setValue("sync_on_startup", sync)
    
    def get_sync_on_changes(self) -> bool:
        """Get sync on changes setting"""
        return self.qsettings.value("sync_on_changes", True, bool)
    
    def set_sync_on_changes(self, sync: bool):
        """Set sync on changes setting"""
        self.qsettings.setValue("sync_on_changes", sync)
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.qsettings.clear()
        self._servers = self._load_servers()
        self._current_server = self._get_current_server()
