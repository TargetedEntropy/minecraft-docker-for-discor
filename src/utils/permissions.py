"""
Permission checking utilities
"""

import discord
from typing import List
from config.settings import settings


class PermissionChecker:
    """Helper class for checking user permissions"""
    
    def __init__(self):
        self.allowed_roles = settings.ALLOWED_ROLES
    
    def has_required_role(self, member: discord.Member) -> bool:
        """Check if member has any of the required roles"""
        if not isinstance(member, discord.Member):
            return False
        
        user_roles = [role.name for role in member.roles]
        return any(role in self.allowed_roles for role in user_roles)
    
    def is_server_admin(self, member: discord.Member) -> bool:
        """Check if member is a server administrator"""
        if not isinstance(member, discord.Member):
            return False
        
        return member.guild_permissions.administrator
    
    def can_manage_server(self, member: discord.Member, server_info: dict) -> bool:
        """Check if member can manage a specific server"""
        # Server creators can always manage their servers
        if server_info.get('created_by') == str(member):
            return True
        
        # Users with required roles can manage any server
        return self.has_required_role(member)
