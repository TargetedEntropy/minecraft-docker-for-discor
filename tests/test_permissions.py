"""
Tests for permission checking utilities
"""

import pytest
from unittest.mock import Mock
from src.utils.permissions import PermissionChecker


class TestPermissionChecker:
    """Test cases for the PermissionChecker class"""
    
    @pytest.fixture
    def permission_checker(self):
        """Create a PermissionChecker instance for testing"""
        return PermissionChecker()
    
    def test_has_required_role_success(self, permission_checker):
        """Test successful role check"""
        mock_member = Mock()
        mock_role = Mock()
        mock_role.name = "Admin"
        mock_member.roles = [mock_role]
        
        result = permission_checker.has_required_role(mock_member)
        
        assert result is True
    
    def test_has_required_role_failure(self, permission_checker):
        """Test failed role check"""
        mock_member = Mock()
        mock_role = Mock()
        mock_role.name = "User"
        mock_member.roles = [mock_role]
        
        result = permission_checker.has_required_role(mock_member)
        
        assert result is False
    
    def test_is_server_admin(self, permission_checker):
        """Test server admin check"""
        mock_member = Mock()
        mock_member.guild_permissions.administrator = True
        
        result = permission_checker.is_server_admin(mock_member)
        
        assert result is True
