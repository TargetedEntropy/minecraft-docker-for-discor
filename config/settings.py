"""
Application settings and configuration management
"""

import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings class"""
    
    # Bot Configuration
    DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "")
    ALLOWED_ROLES: List[str] = os.getenv("ALLOWED_ROLES", "Admin,Moderator,ServerManager").split(",")
    
    # Docker Configuration
    DOCKER_HOST: str = os.getenv("DOCKER_HOST", "unix:///var/run/docker.sock")
    
    # File Paths
    TEMPLATES_FILE: str = os.getenv("TEMPLATES_FILE", "config/templates.json")
    SERVERS_FILE: str = os.getenv("SERVERS_FILE", "data/active_servers.json")
    
    # Server Defaults
    DEFAULT_MEMORY: str = os.getenv("DEFAULT_MEMORY", "2G")
    DEFAULT_PORT_RANGE_START: int = int(os.getenv("DEFAULT_PORT_RANGE_START", "25565"))
    DEFAULT_PORT_RANGE_END: int = int(os.getenv("DEFAULT_PORT_RANGE_END", "25600"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/bot.log")
    
    # Ensure directories exist
    @staticmethod
    def ensure_directories():
        """Create necessary directories if they don't exist"""
        directories = ["data", "logs", "config"]
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)

# Global settings instance
settings = Settings()
settings.ensure_directories()
