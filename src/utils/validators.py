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
        pattern = r'^[a-zA-Z0-9_-]+'
        
        return bool(re.match(pattern, name))
    
    @staticmethod
    def validate_port(port: int) -> bool:
        """Validate port number"""
        return 1024 <= port <= 65535
    
    @staticmethod
    def validate_memory(memory: str) -> bool:
        """Validate memory format (e.g., '2G', '512M')"""
        pattern = r'^\d+[GMgm]'
        
        return bool(re.match(pattern, memory))
    
    @staticmethod
    def validate_minecraft_version(version: str) -> bool:
        """Validate Minecraft version format"""
        pattern = r'^\d+\.\d+(\.\d+)?'
        
        return bool(re.match(pattern, version))
