"""
API Client for communicating with zPass backend
"""

import requests
import json
from typing import Dict, Any, Optional, Tuple
from requests.exceptions import RequestException, ConnectionError, Timeout

class APIClient:
    """zPass API Client"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:5000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.access_token = None
    
    def set_base_url(self, url: str):
        """Set the base URL for API requests"""
        self.base_url = url.rstrip('/')
    
    def set_access_token(self, token: str):
        """Set the access token for authenticated requests"""
        self.access_token = token
        self.session.headers.update({
            'Authorization': f'Bearer {token}'
        })
    
    def clear_access_token(self):
        """Clear the access token"""
        self.access_token = None
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                     timeout: int = 30) -> Tuple[bool, Dict[str, Any]]:
        """Make HTTP request to the API"""
        url = f"{self.base_url}/api/{endpoint.lstrip('/')}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, timeout=timeout)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, timeout=timeout)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, timeout=timeout)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, timeout=timeout)
            else:
                return False, {"error": "Unsupported HTTP method"}
            
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = {"error": "Invalid JSON response"}
            
            success = response.status_code < 400
            return success, response_data
            
        except ConnectionError:
            return False, {"error": "Connection failed. Please check your internet connection and server URL."}
        except Timeout:
            return False, {"error": "Request timed out. Please try again."}
        except RequestException as e:
            return False, {"error": f"Request failed: {str(e)}"}
        except Exception as e:
            return False, {"error": f"Unexpected error: {str(e)}"}
    
    def test_connection(self) -> Tuple[bool, Dict[str, Any]]:
        """Test connection to the server"""
        return self._make_request('GET', 'test')
    
    def register(self, username: str, email: str, password: str) -> Tuple[bool, Dict[str, Any]]:
        """Register a new user"""
        data = {
            "username": username,
            "email": email,
            "password": password
        }
        return self._make_request('POST', 'auth/register', data)
    
    def login(self, username: str, password: str) -> Tuple[bool, Dict[str, Any]]:
        """Login user"""
        data = {
            "username": username,
            "password": password
        }
        success, response = self._make_request('POST', 'auth/login', data)
        
        if success and 'access_token' in response:
            # Automatically set the access token
            self.set_access_token(response['access_token'])
        
        return success, response
    
    def verify_token(self) -> Tuple[bool, Dict[str, Any]]:
        """Verify current access token"""
        if not self.access_token:
            return False, {"error": "No access token available"}
        
        return self._make_request('GET', 'auth/verify')
    
    def get_vault(self) -> Tuple[bool, Dict[str, Any]]:
        """Get user's vault data"""
        if not self.access_token:
            return False, {"error": "Authentication required"}
        
        return self._make_request('GET', 'vault')
    
    def update_vault(self, encrypted_data: str, salt: str) -> Tuple[bool, Dict[str, Any]]:
        """Update user's vault data"""
        if not self.access_token:
            return False, {"error": "Authentication required"}
        
        data = {
            "encrypted_data": encrypted_data,
            "salt": salt
        }
        return self._make_request('PUT', 'vault', data)
    
    def logout(self):
        """Logout (clear local session)"""
        self.clear_access_token()
