"""
Tests for Docker helper utilities
"""

import pytest
from unittest.mock import Mock, patch
from src.utils.docker_helper import DockerHelper
from src.models.server import MinecraftServer
from src.models.template import ServerTemplate


class TestDockerHelper:
    """Test cases for the DockerHelper class"""
    
    @pytest.fixture
    def docker_helper(self):
        """Create a DockerHelper instance for testing"""
        with patch('docker.from_env') as mock_docker:
            mock_client = Mock()
            mock_docker.return_value = mock_client
            helper = DockerHelper()
            helper.client = mock_client
            return helper
    
    @pytest.fixture
    def sample_template(self):
        """Create a sample template for testing"""
        return ServerTemplate(
            name="test_template",
            description="Test template",
            image="test/image",
            environment={"EULA": "TRUE"},
            ports={"25565/tcp": None},
            volumes={},
            restart_policy={"Name": "unless-stopped"}
        )
    
    @pytest.fixture
    def sample_server(self, sample_template):
        """Create a sample server for testing"""
        return MinecraftServer(
            name="test_server",
            template=sample_template,
            port=25565,
            created_by="test_user"
        )
    
    @pytest.mark.asyncio
    async def test_create_server(self, docker_helper, sample_server):
        """Test server creation"""
        mock_container = Mock()
        mock_container.short_id = "abc123"
        docker_helper.client.containers.run.return_value = mock_container
        
        result = await docker_helper.create_server(sample_server)
        
        assert result == mock_container
        docker_helper.client.containers.run.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_container_status(self, docker_helper):
        """Test getting container status"""
        mock_container = Mock()
        mock_container.status = "running"
        docker_helper.client.containers.get.return_value = mock_container
        
        status = await docker_helper.get_container_status("test_id")
        
        assert status == "running"
