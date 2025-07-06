"""
Docker helper utilities for container management
"""

import docker
import asyncio
from typing import Dict, Optional
import logging
from config.settings import settings

logger = logging.getLogger(__name__)


class DockerHelper:
    """Helper class for Docker operations"""
    
    def __init__(self):
        try:
            self.client = docker.from_env()
            # Test connection
            self.client.ping()
            logger.info("Connected to Docker daemon")
        except Exception as e:
            logger.error(f"Failed to connect to Docker: {e}")
            raise
    
async def create_server(self, server):
        """Create and start a new Minecraft server container"""
        try:
            # Set up port mapping
            ports = {}
            if server.port:
                ports['25565/tcp'] = server.port
            else:
                ports['25565/tcp'] = None
            
            # Set up volume for persistent data
            volume_name = f"minecraft_{server.name}"
            volumes = {volume_name: {'bind': '/data', 'mode': 'rw'}}
            
            # Prepare environment variables
            environment = server.template.environment.copy()
            
            # Add modpack URL if provided
            if server.modpack_url:
                environment['MODPACK'] = server.modpack_url
                # Ensure the server type supports modpacks
                if environment.get('TYPE') in ['VANILLA']:
                    # Convert vanilla to forge for modpack support
                    environment['TYPE'] = 'FORGE'
                    environment['VERSION'] = environment.get('VERSION', '1.20.4')
                    if 'FORGE_VERSION' not in environment:
                        environment['FORGE_VERSION'] = 'RECOMMENDED'
                
                # Enable mod removal for modpack updates
                environment['REMOVE_OLD_MODS'] = 'true'
                environment['REMOVE_OLD_MODS_INCLUDE'] = '*.jar'
                environment['REMOVE_OLD_MODS_EXCLUDE'] = 'essential'
            
            # Create container
            container = self.client.containers.run(
                server.template.image,
                name=f"minecraft_{server.name}",
                environment=environment,
                ports=ports,
                volumes=volumes,
                detach=True,
                restart_policy=server.template.restart_policy
            )
            
            logger.info(f"Created container for server {server.name}: {container.short_id}")
            if server.modpack_url:
                logger.info(f"Server {server.name} configured with modpack: {server.modpack_url}")
            return container
        except Exception as error:
            pass