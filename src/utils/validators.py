"""
Input validation utilities
"""

import re
from typing import Optional


class ServerValidator:
    """Helper class for validating server-related inputs"""
    
    @staticmethod
    def validate_server_name(name: str) -> bool:
        """Validate server name format"""
        if not name or len(name) < 1 or len(name) > 32:
            return False
        
        # Allow letters, numbers, underscores, and hyphens
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, name))
    
    @staticmethod
    def validate_port(port: int) -> bool:
        """Validate port number"""
        return 1024 <= port <= 65535
    
    @staticmethod
    def validate_memory(memory: str) -> bool:
        """Validate memory format (e.g., '2G', '512M')"""
        pattern = r'^\d+[GMgm]$'
        return bool(re.match(pattern, memory))
    
    @staticmethod
    def validate_minecraft_version(version: str) -> bool:
        """Validate Minecraft version format"""
        pattern = r'^\d+\.\d+(\.\d+)?$'
        return bool(re.match(pattern, version))
    
    @staticmethod
    def validate_modpack_url(url: str) -> bool:
        """Validate modpack URL format"""
        if not url:
            return False
        
        # Check if URL is valid format
        import urllib.parse
        try:
            result = urllib.parse.urlparse(url)
            if not all([result.scheme, result.netloc]):
                return False
        except Exception:
            return False
        
        # Check if URL ends with .zip
        if not url.lower().endswith('.zip'):
            return False
        
        # Check if URL is accessible (basic validation)
        valid_schemes = ['http', 'https']
        if result.scheme not in valid_schemes:
            return False
        
        return True