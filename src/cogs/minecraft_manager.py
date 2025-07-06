"""
Minecraft server management cog
"""

import discord
from discord.ext import commands
import docker
import json
import asyncio
from typing import Dict, Optional
import logging
from pathlib import Path

from src.utils.docker_helper import DockerHelper
from src.utils.permissions import PermissionChecker
from src.utils.validators import ServerValidator
from src.models.server import MinecraftServer
from src.models.template import ServerTemplate
from config.settings import settings

logger = logging.getLogger(__name__)


class MinecraftServerManager(commands.Cog):
    """Cog for managing Minecraft servers"""
    
    def __init__(self, bot):
        self.bot = bot
        self.docker_helper = DockerHelper()
        self.permission_checker = PermissionChecker()
        self.validator = ServerValidator()
        self.templates = self.load_templates()
        self.active_servers = self.load_active_servers()
        
    def load_templates(self) -> Dict:
        """Load server templates from JSON file"""
        try:
            with open(settings.TEMPLATES_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Templates file not found: {settings.TEMPLATES_FILE}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing templates file: {e}")
            return {}
    
    def load_active_servers(self) -> Dict:
        """Load active servers from JSON file"""
        try:
            with open(settings.SERVERS_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing servers file: {e}")
            return {}
    
    def save_active_servers(self):
        """Save active servers to JSON file"""
        try:
            Path(settings.SERVERS_FILE).parent.mkdir(parents=True, exist_ok=True)
            with open(settings.SERVERS_FILE, 'w') as f:
                json.dump(self.active_servers, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving servers file: {e}")
    
    @commands.command(name='list_templates')
    async def list_templates(self, ctx):
        """List available server templates"""
        if not self.permission_checker.has_required_role(ctx.author):
            await ctx.send("❌ You don't have permission to use this command.")
            return
        
        if not self.templates:
            await ctx.send("❌ No templates available.")
            return
        
        embed = discord.Embed(title="Available Server Templates", color=0x00ff00)
        
        for name, template in self.templates.items():
            template_obj = ServerTemplate.from_dict(name, template)
            embed.add_field(
                name=template_obj.name,
                value=f"**Type:** {template_obj.environment.get('TYPE', 'Unknown')}\n"
                      f"**Memory:** {template_obj.environment.get('MEMORY', 'N/A')}\n"
                      f"**Description:** {template_obj.description}",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
@commands.command(name='create_server')
    async def create_server(self, ctx, server_name: str, template_name: str, port: int = None, modpack_url: str = None):
        """Create a new Minecraft server from template with optional modpack URL"""
        if not self.permission_checker.has_required_role(ctx.author):
            await ctx.send("❌ You don't have permission to use this command.")
            return
        
        # Validate inputs
        if not self.validator.validate_server_name(server_name):
            await ctx.send("❌ Invalid server name. Use only letters, numbers, and underscores.")
            return
        
        if template_name not in self.templates:
            await ctx.send(f"❌ Template '{template_name}' not found. Use `!list_templates` to see available templates.")
            return
        
        if server_name in self.active_servers:
            await ctx.send(f"❌ Server '{server_name}' already exists.")
            return
        
        if port and not self.validator.validate_port(port):
            await ctx.send("❌ Invalid port number. Port must be between 1024 and 65535.")
            return
        
        # Validate modpack URL if provided
        if modpack_url and not self.validator.validate_modpack_url(modpack_url):
            await ctx.send("❌ Invalid modpack URL. Must be a direct link to a .zip file.")
            return
        
        try:
            template = ServerTemplate.from_dict(template_name, self.templates[template_name])
            
            # Create server instance with modpack URL
            server = MinecraftServer(
                name=server_name,
                template=template,
                port=port,
                created_by=str(ctx.author),
                modpack_url=modpack_url
            )
            
            # Create container using Docker helper
            container = await self.docker_helper.create_server(server)
            
            # Store server info
            self.active_servers[server_name] = server.to_dict()
            self.active_servers[server_name]['container_id'] = container.id
            self.save_active_servers()
            
            embed = discord.Embed(title="✅ Server Created", color=0x00ff00)
            embed.add_field(name="Server Name", value=server_name, inline=True)
            embed.add_field(name="Template", value=template_name, inline=True)
            embed.add_field(name="Port", value=port or "Auto-assigned", inline=True)
            embed.add_field(name="Container ID", value=container.short_id, inline=True)
            if modpack_url:
                embed.add_field(name="Modpack", value="Custom ZIP", inline=True)
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error creating server {server_name}: {e}")
            await ctx.send(f"❌ Error creating server: {str(e)}")
async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(MinecraftServerManager(bot))
