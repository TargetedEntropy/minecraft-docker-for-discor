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
    async def create_server(self, ctx, server_name: str, template_name: str, port: int = None):
        """Create a new Minecraft server from template"""
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
        
        try:
            template = ServerTemplate.from_dict(template_name, self.templates[template_name])
            
            # Create server instance
            server = MinecraftServer(
                name=server_name,
                template=template,
                port=port,
                created_by=str(ctx.author)
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
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error creating server {server_name}: {e}")
            await ctx.send(f"❌ Error creating server: {str(e)}")
    
    @commands.command(name='list_servers')
    async def list_servers(self, ctx):
        """List all active servers"""
        if not self.permission_checker.has_required_role(ctx.author):
            await ctx.send("❌ You don't have permission to use this command.")
            return
        
        if not self.active_servers:
            await ctx.send("No active servers found.")
            return
        
        embed = discord.Embed(title="Active Minecraft Servers", color=0x0099ff)
        
        for server_name, info in self.active_servers.items():
            try:
                status = await self.docker_helper.get_container_status(info['container_id'])
                self.active_servers[server_name]['status'] = status
                
                embed.add_field(
                    name=server_name,
                    value=f"**Status:** {status}\n"
                          f"**Template:** {info['template_name']}\n"
                          f"**Port:** {info.get('port', 'Auto')}\n"
                          f"**Created by:** {info['created_by']}",
                    inline=False
                )
            except Exception as e:
                embed.add_field(
                    name=server_name,
                    value=f"**Status:** Error ({str(e)})",
                    inline=False
                )
        
        self.save_active_servers()
        await ctx.send(embed=embed)
    
    @commands.command(name='start_server')
    async def start_server(self, ctx, server_name: str):
        """Start a stopped server"""
        if not self.permission_checker.has_required_role(ctx.author):
            await ctx.send("❌ You don't have permission to use this command.")
            return
        
        if server_name not in self.active_servers:
            await ctx.send(f"❌ Server '{server_name}' not found.")
            return
        
        try:
            await self.docker_helper.start_container(self.active_servers[server_name]['container_id'])
            self.active_servers[server_name]['status'] = 'running'
            self.save_active_servers()
            
            await ctx.send(f"✅ Server '{server_name}' started successfully.")
        except Exception as e:
            logger.error(f"Error starting server {server_name}: {e}")
            await ctx.send(f"❌ Error starting server: {str(e)}")
    
    @commands.command(name='stop_server')
    async def stop_server(self, ctx, server_name: str):
        """Stop a running server"""
        if not self.permission_checker.has_required_role(ctx.author):
            await ctx.send("❌ You don't have permission to use this command.")
            return
        
        if server_name not in self.active_servers:
            await ctx.send(f"❌ Server '{server_name}' not found.")
            return
        
        try:
            await self.docker_helper.stop_container(self.active_servers[server_name]['container_id'])
            self.active_servers[server_name]['status'] = 'stopped'
            self.save_active_servers()
            
            await ctx.send(f"✅ Server '{server_name}' stopped successfully.")
        except Exception as e:
            logger.error(f"Error stopping server {server_name}: {e}")
            await ctx.send(f"❌ Error stopping server: {str(e)}")
    
    @commands.command(name='restart_server')
    async def restart_server(self, ctx, server_name: str):
        """Restart a server"""
        if not self.permission_checker.has_required_role(ctx.author):
            await ctx.send("❌ You don't have permission to use this command.")
            return
        
        if server_name not in self.active_servers:
            await ctx.send(f"❌ Server '{server_name}' not found.")
            return
        
        try:
            await self.docker_helper.restart_container(self.active_servers[server_name]['container_id'])
            self.active_servers[server_name]['status'] = 'running'
            self.save_active_servers()
            
            await ctx.send(f"✅ Server '{server_name}' restarted successfully.")
        except Exception as e:
            logger.error(f"Error restarting server {server_name}: {e}")
            await ctx.send(f"❌ Error restarting server: {str(e)}")
    
    @commands.command(name='remove_server')
    async def remove_server(self, ctx, server_name: str):
        """Remove a server (stops and deletes container)"""
        if not self.permission_checker.has_required_role(ctx.author):
            await ctx.send("❌ You don't have permission to use this command.")
            return
        
        if server_name not in self.active_servers:
            await ctx.send(f"❌ Server '{server_name}' not found.")
            return
        
        try:
            await self.docker_helper.remove_container(self.active_servers[server_name]['container_id'])
            del self.active_servers[server_name]
            self.save_active_servers()
            
            await ctx.send(f"✅ Server '{server_name}' removed successfully.")
        except Exception as e:
            logger.error(f"Error removing server {server_name}: {e}")
            await ctx.send(f"❌ Error removing server: {str(e)}")
    
    @commands.command(name='server_logs')
    async def server_logs(self, ctx, server_name: str, lines: int = 50):
        """Get server logs"""
        if not self.permission_checker.has_required_role(ctx.author):
            await ctx.send("❌ You don't have permission to use this command.")
            return
        
        if server_name not in self.active_servers:
            await ctx.send(f"❌ Server '{server_name}' not found.")
            return
        
        if lines > 100:
            await ctx.send("❌ Maximum 100 lines allowed.")
            return
        
        try:
            logs = await self.docker_helper.get_container_logs(
                self.active_servers[server_name]['container_id'], 
                lines
            )
            
            # Split logs into chunks if too long for Discord
            if len(logs) > 1900:
                chunks = [logs[i:i+1900] for i in range(0, len(logs), 1900)]
                for i, chunk in enumerate(chunks):
                    await ctx.send(f"```\n{chunk}\n```")
                    if i < len(chunks) - 1:
                        await asyncio.sleep(1)
            else:
                await ctx.send(f"```\n{logs}\n```")
                
        except Exception as e:
            logger.error(f"Error getting logs for {server_name}: {e}")
            await ctx.send(f"❌ Error getting logs: {str(e)}")
    
    @commands.command(name='server_status')
    async def server_status(self, ctx, server_name: str):
        """Get detailed server status"""
        if not self.permission_checker.has_required_role(ctx.author):
            await ctx.send("❌ You don't have permission to use this command.")
            return
        
        if server_name not in self.active_servers:
            await ctx.send(f"❌ Server '{server_name}' not found.")
            return
        
        try:
            status_info = await self.docker_helper.get_detailed_status(
                self.active_servers[server_name]['container_id']
            )
            
            embed = discord.Embed(title=f"Server Status: {server_name}", color=0x0099ff)
            embed.add_field(name="Container Status", value=status_info['status'], inline=True)
            embed.add_field(name="Template", value=self.active_servers[server_name]['template_name'], inline=True)
            embed.add_field(name="Port", value=self.active_servers[server_name].get('port', 'Auto'), inline=True)
            embed.add_field(name="Created By", value=self.active_servers[server_name]['created_by'], inline=True)
            embed.add_field(name="Container ID", value=status_info['short_id'], inline=True)
            
            if 'memory_usage' in status_info:
                embed.add_field(
                    name="Memory Usage", 
                    value=f"{status_info['memory_usage']:.1f}MB / {status_info['memory_limit']:.1f}MB", 
                    inline=True
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error getting status for {server_name}: {e}")
            await ctx.send(f"❌ Error getting status: {str(e)}")


async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(MinecraftServerManager(bot))
