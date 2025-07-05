"""
Minecraft server model
"""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class MinecraftServer:
    """Model representing a Minecraft server instance"""
    
    name: str
    template: 'ServerTemplate'
    port: Optional[int] = None
    created_by: str = ""
    created_at: str = ""
    status: str = "created"
    container_id: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert server to dictionary representation"""
        return {
            'name': self.name,
            'template_name': self.template.name if hasattr(self.template, 'name') else 'unknown',
            'port': self.port,
            'created_by': self.created_by,
            'created_at': self.created_at,
            'status': self.status,
            'container_id': self.container_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], template: 'ServerTemplate') -> 'MinecraftServer':
        """Create server instance from dictionary"""
        return cls(
            name=data['name'],
            template=template,
            port=data.get('port'),
            created_by=data.get('created_by', ''),
            created_at=data.get('created_at', ''),
            status=data.get('status', 'created'),
            container_id=data.get('container_id', '')
        )
