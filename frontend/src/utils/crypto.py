"""
Cryptographic utilities for zPass
"""

import os
import json
import base64
import hashlib
from typing import Dict, Any, Optional, Tuple
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

class CryptoManager:
    """Manages encryption and decryption of vault data"""
    
    # AES-256 key length
    KEY_LENGTH = 32
    # IV length for AES
    IV_LENGTH = 16
    # Salt length for PBKDF2
    SALT_LENGTH = 32
    # PBKDF2 iterations
    PBKDF2_ITERATIONS = 100000
    
    @staticmethod
    def generate_salt() -> bytes:
        """Generate a random salt"""
        return get_random_bytes(CryptoManager.SALT_LENGTH)
    
    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        """Derive encryption key from password using PBKDF2"""
        return PBKDF2(
            password.encode('utf-8'),
            salt,
            dkLen=CryptoManager.KEY_LENGTH,
            count=CryptoManager.PBKDF2_ITERATIONS
        )
    
    @staticmethod
    def encrypt_data(data: Dict[str, Any], password: str) -> Tuple[str, str]:
        """
        Encrypt vault data with master password
        Returns: (encrypted_data_base64, salt_base64)
        """
        try:
            # Convert data to JSON string
            json_data = json.dumps(data, ensure_ascii=False)
            
            # Generate salt and derive key
            salt = CryptoManager.generate_salt()
            key = CryptoManager.derive_key(password, salt)
            
            # Generate IV
            iv = get_random_bytes(CryptoManager.IV_LENGTH)
            
            # Create cipher and encrypt
            cipher = AES.new(key, AES.MODE_CBC, iv)
            padded_data = pad(json_data.encode('utf-8'), AES.block_size)
            encrypted_data = cipher.encrypt(padded_data)
            
            # Combine IV + encrypted data
            combined_data = iv + encrypted_data
            
            # Return base64 encoded strings
            encrypted_b64 = base64.b64encode(combined_data).decode('utf-8')
            salt_b64 = base64.b64encode(salt).decode('utf-8')
            
            return encrypted_b64, salt_b64
            
        except Exception as e:
            raise ValueError(f"Encryption failed: {str(e)}")
    
    @staticmethod
    def decrypt_data(encrypted_data_b64: str, salt_b64: str, password: str) -> Dict[str, Any]:
        """
        Decrypt vault data with master password
        Returns: decrypted data as dictionary
        """
        try:
            # Decode base64
            encrypted_data = base64.b64decode(encrypted_data_b64.encode('utf-8'))
            salt = base64.b64decode(salt_b64.encode('utf-8'))
            
            # Derive key
            key = CryptoManager.derive_key(password, salt)
            
            # Extract IV and encrypted data
            iv = encrypted_data[:CryptoManager.IV_LENGTH]
            ciphertext = encrypted_data[CryptoManager.IV_LENGTH:]
            
            # Create cipher and decrypt
            cipher = AES.new(key, AES.MODE_CBC, iv)
            padded_data = cipher.decrypt(ciphertext)
            
            # Remove padding
            json_data = unpad(padded_data, AES.block_size).decode('utf-8')
            
            # Parse JSON
            return json.loads(json_data)
            
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
    
    @staticmethod
    def verify_password(encrypted_data_b64: str, salt_b64: str, password: str) -> bool:
        """
        Verify if password can decrypt the data
        Returns: True if password is correct
        """
        try:
            CryptoManager.decrypt_data(encrypted_data_b64, salt_b64, password)
            return True
        except:
            return False
    
    @staticmethod
    def generate_password(length: int = 16, use_symbols: bool = True, 
                         use_numbers: bool = True, use_uppercase: bool = True, 
                         use_lowercase: bool = True) -> str:
        """Generate a secure random password"""
        import string
        import secrets
        
        chars = ""
        if use_lowercase:
            chars += string.ascii_lowercase
        if use_uppercase:
            chars += string.ascii_uppercase
        if use_numbers:
            chars += string.digits
        if use_symbols:
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        if not chars:
            chars = string.ascii_letters + string.digits
        
        return ''.join(secrets.choice(chars) for _ in range(length))
    
    @staticmethod
    def check_password_strength(password: str) -> Tuple[int, str, list]:
        """
        Check password strength
        Returns: (score 0-100, description, suggestions)
        """
        score = 0
        suggestions = []
        
        # Length check
        if len(password) >= 12:
            score += 25
        elif len(password) >= 8:
            score += 15
        else:
            suggestions.append("Use at least 8 characters")
        
        # Character variety checks
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_symbol = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        variety_score = sum([has_lower, has_upper, has_digit, has_symbol])
        score += variety_score * 15
        
        if not has_lower:
            suggestions.append("Add lowercase letters")
        if not has_upper:
            suggestions.append("Add uppercase letters")
        if not has_digit:
            suggestions.append("Add numbers")
        if not has_symbol:
            suggestions.append("Add special characters")
        
        # Common patterns check
        common_patterns = ['123456', 'password', 'qwerty', 'abc', '000']
        for pattern in common_patterns:
            if pattern.lower() in password.lower():
                score -= 10
                suggestions.append(f"Avoid common patterns like '{pattern}'")
        
        # Repetition check
        if len(set(password)) < len(password) * 0.6:
            score -= 10
            suggestions.append("Avoid too much repetition")
        
        score = max(0, min(100, score))
        
        if score >= 80:
            description = "Very Strong"
        elif score >= 60:
            description = "Strong"
        elif score >= 40:
            description = "Moderate"
        elif score >= 20:
            description = "Weak"
        else:
            description = "Very Weak"
        
        return score, description, suggestions
