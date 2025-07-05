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
            
            # Create container
            container = self.client.containers.run(
                server.template.image,
                name=f"minecraft_{server.name}",
                environment=server.template.environment,
                ports=ports,
                volumes=volumes,
                detach=True,
                restart_policy=server.template.restart_policy
            )
            
            logger.info(f"Created container for server {server.name}: {container.short_id}")
            return container
            
        except Exception as e:
            logger.error(f"Error creating server container: {e}")
            raise
    
    async def start_container(self, container_id: str):
        """Start a stopped container"""
        try:
            container = self.client.containers.get(container_id)
            container.start()
            logger.info(f"Started container {container.short_id}")
        except Exception as e:
            logger.error(f"Error starting container {container_id}: {e}")
            raise
    
    async def stop_container(self, container_id: str):
        """Stop a running container"""
        try:
            container = self.client.containers.get(container_id)
            container.stop()
            logger.info(f"Stopped container {container.short_id}")
        except Exception as e:
            logger.error(f"Error stopping container {container_id}: {e}")
            raise
    
    async def restart_container(self, container_id: str):
        """Restart a container"""
        try:
            container = self.client.containers.get(container_id)
            container.restart()
            logger.info(f"Restarted container {container.short_id}")
        except Exception as e:
            logger.error(f"Error restarting container {container_id}: {e}")
            raise
    
    async def remove_container(self, container_id: str):
        """Stop and remove a container"""
        try:
            container = self.client.containers.get(container_id)
            container.stop()
            container.remove()
            logger.info(f"Removed container {container.short_id}")
        except Exception as e:
            logger.error(f"Error removing container {container_id}: {e}")
            raise
    
    async def get_container_status(self, container_id: str) -> str:
        """Get the status of a container"""
        try:
            container = self.client.containers.get(container_id)
            return container.status
        except docker.errors.NotFound:
            return "not_found"
        except Exception as e:
            logger.error(f"Error getting container status {container_id}: {e}")
            return "error"
    
    async def get_container_logs(self, container_id: str, lines: int = 50) -> str:
        """Get logs from a container"""
        try:
            container = self.client.containers.get(container_id)
            logs = container.logs(tail=lines).decode('utf-8')
            return logs
        except Exception as e:
            logger.error(f"Error getting container logs {container_id}: {e}")
            raise
    
    async def get_detailed_status(self, container_id: str) -> Dict:
        """Get detailed status information for a container"""
        try:
            container = self.client.containers.get(container_id)
            
            result = {
                'status': container.status,
                'short_id': container.short_id
            }
            
            # Get resource usage if container is running
            if container.status == 'running':
                try:
                    stats = container.stats(stream=False)
                    memory_usage = stats['memory_stats']['usage'] / 1024 / 1024  # MB
                    memory_limit = stats['memory_stats']['limit'] / 1024 / 1024  # MB
                    result.update({
                        'memory_usage': memory_usage,
                        'memory_limit': memory_limit
                    })
                except Exception as e:
                    logger.warning(f"Could not get stats for container {container_id}: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting detailed status for {container_id}: {e}")
            raise
