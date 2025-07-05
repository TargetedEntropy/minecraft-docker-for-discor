"""
Server template model
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class ServerTemplate:
    """Model representing a server template"""
    
    name: str
    description: str
    image: str
    environment: Dict[str, str]
    ports: Dict[str, Optional[int]]
    volumes: Dict[str, Any]
    restart_policy: Dict[str, str]
    
    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> 'ServerTemplate':
        """Create template instance from dictionary"""
        return cls(
            name=data.get('name', name),
            description=data.get('description', ''),
            image=data['image'],
            environment=data.get('environment', {}),
            ports=data.get('ports', {}),
            volumes=data.get('volumes', {}),
            restart_policy=data.get('restart_policy', {'Name': 'unless-stopped'})
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary representation"""
        return {
            'name': self.name,
            'description': self.description,
            'image': self.image,
            'environment': self.environment,
            'ports': self.ports,
            'volumes': self.volumes,
            'restart_policy': self.restart_policy
        }
