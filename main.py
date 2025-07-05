import discord
from discord.ext import commands
import docker
import json
import os
import asyncio
from typing import Dict, Optional, List
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
ALLOWED_ROLES = os.getenv('ALLOWED_ROLES', 'Admin,Moderator,ServerManager').split(',')  # Configure these role names
TEMPLATES_FILE = 'server_templates.json'
SERVERS_FILE = 'active_servers.json'

class MinecraftServerManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.docker_client = docker.from_env()
        self.templates = self.load_templates()
        self.active_servers = self.load_active_servers()
        
    def load_templates(self) -> Dict:
        """Load server templates from JSON file"""
        try:
            with open(TEMPLATES_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Create default templates if file doesn't exist
            default_templates = {
                "vanilla": {
                    "image": "itzg/minecraft-server:latest",
                    "environment": {
                        "EULA": "TRUE",
                        "TYPE": "VANILLA",
                        "MEMORY": "2G"
                    },
                    "ports": {"25565/tcp": None},
                    "volumes": {}
                },
                "forge": {
                    "image": "itzg/minecraft-server:latest",
                    "environment": {
                        "EULA": "TRUE",
                        "TYPE": "FORGE",
                        "MEMORY": "4G"
                    },
                    "ports": {"25565/tcp": None},
                    "volumes": {}
                },
                "modded": {
                    "image": "itzg/minecraft-server:latest",
                    "environment": {
                        "EULA": "TRUE",
                        "TYPE": "FORGE",
                        "MEMORY": "6G",
                        "MODPACK": ""
                    },
                    "ports": {"25565/tcp": None},
                    "volumes": {}
                }
            }
            self.save_templates(default_templates)
            return default_templates
    
    def save_templates(self, templates: Dict):
        """Save templates to JSON file"""
        with open(TEMPLATES_FILE, 'w') as f:
            json.dump(templates, f, indent=2)
    
    def load_active_servers(self) -> Dict:
        """Load active servers from JSON file"""
        try:
            with open(SERVERS_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_active_servers(self):
        """Save active servers to JSON file"""
        with open(SERVERS_FILE, 'w') as f:
            json.dump(self.active_servers, f, indent=2)
    
    def has_required_role(self, member: discord.Member) -> bool:
        """Check if member has required role"""
        user_roles = [role.name for role in member.roles]
        return any(role in ALLOWED_ROLES for role in user_roles)
    
    @commands.command(name='list_templates')
    async def list_templates(self, ctx):
        """List available server templates"""
        if not self.has_required_role(ctx.author):
            await ctx.send("❌ You don't have permission to use this command.")
            return
        
        embed = discord.Embed(title="Available Server Templates", color=0x00ff00)
        for name, template in self.templates.items():
            embed.add_field(
                name=name.capitalize(),
                value=f"Image: {template['image']}\nMemory: {template['environment'].get('MEMORY', 'N/A')}",
                inline=False
            )
        await ctx.send(embed=embed)
    
    @commands.command(name='create_server')
    async def create_server(self, ctx, server_name: str, template_name: str, port: int = None):
        """Create a new Minecraft server from template"""
        if not self.has_required_role(ctx.author):
            await ctx.send("❌ You don't have permission to use this command.")
            return
        
        if template_name not in self.templates:
            await ctx.send(f"❌ Template '{template_name}' not found. Use `!list_templates` to see available templates.")
            return
        
        if server_name in self.active_servers:
            await ctx.send(f"❌ Server '{server_name}' already exists.")
            return
        
        try:
            template = self.templates[template_name].copy()
            
            # Set up port mapping
            if port:
                template['ports'] = {f"25565/tcp": port}
            
            # Set up volume for persistent data
            volume_name = f"minecraft_{server_name}"
            template['volumes'] = {volume_name: {'bind': '/data', 'mode': 'rw'}}
            
            # Create and start container
            container = self.docker_client.containers.run(
                template['image'],
                name=f"minecraft_{server_name}",
                environment=template['environment'],
                ports=template['ports'],
                volumes=template['volumes'],
                detach=True,
                restart_policy={"Name": "unless-stopped"}
            )
            
            # Store server info
            self.active_servers[server_name] = {
                'container_id': container.id,
                'template': template_name,
                'port': port,
                'created_by': str(ctx.author),
                'status': 'running'
            }
            self.save_active_servers()
            
            embed = discord.Embed(title="✅ Server Created", color=0x00ff00)
            embed.add_field(name="Server Name", value=server_name, inline=True)
            embed.add_field(name="Template", value=template_name, inline=True)
            embed.add_field(name="Port", value=port or "Auto-assigned", inline=True)
            embed.add_field(name="Container ID", value=container.short_id, inline=True)
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error creating server: {str(e)}")
    
    @commands.command(name='list_servers')
    async def list_servers(self, ctx):
        """List all active servers"""
        if not self.has_required_role(ctx.author):
            await ctx.send("❌ You don't have permission to use this command.")
            return
        
        if not self.active_servers:
            await ctx.send("No active servers found.")
            return
        
        embed = discord.Embed(title="Active Minecraft Servers", color=0x0099ff)
        
        for server_name, info in self.active_servers.items():
            try:
                container = self.docker_client.containers.get(info['container_id'])
                status = container.status
                
                # Update status in our records
                self.active_servers[server_name]['status'] = status
                
                embed.add_field(
                    name=server_name,
                    value=f"Status: {status}\nTemplate: {info['template']}\nPort: {info.get('port', 'Auto')}\nCreated by: {info['created_by']}",
                    inline=False
                )
            except docker.errors.NotFound:
                embed.add_field(
                    name=server_name,
                    value="Status: Container not found (may have been removed)",
                    inline=False
                )
        
        self.save_active_servers()
        await ctx.send(embed=embed)
    
    @commands.command(name='start_server')
    async def start_server(self, ctx, server_name: str):
        """Start a stopped server"""
        if not self.has_required_role(ctx.author):
            await ctx.send("❌ You don't have permission to use this command.")
            return
        
        if server_name not in self.active_servers:
            await ctx.send(f"❌ Server '{server_name}' not found.")
            return
        
        try:
            container = self.docker_client.containers.get(self.active_servers[server_name]['container_id'])
            container.start()
            
            self.active_servers[server_name]['status'] = 'running'
            self.save_active_servers()
            
            await ctx.send(f"✅ Server '{server_name}' started successfully.")
        except Exception as e:
            await ctx.send(f"❌ Error starting server: {str(e)}")
    
    @commands.command(name='stop_server')
    async def stop_server(self, ctx, server_name: str):
        """Stop a running server"""
        if not self.has_required_role(ctx.author):
            await ctx.send("❌ You don't have permission to use this command.")
            return
        
        if server_name not in self.active_servers:
            await ctx.send(f"❌ Server '{server_name}' not found.")
            return
        
        try:
            container = self.docker_client.containers.get(self.active_servers[server_name]['container_id'])
            container.stop()
            
            self.active_servers[server_name]['status'] = 'stopped'
            self.save_active_servers()
            
            await ctx.send(f"✅ Server '{server_name}' stopped successfully.")
        except Exception as e:
            await ctx.send(f"❌ Error stopping server: {str(e)}")
    
    @commands.command(name='restart_server')
    async def restart_server(self, ctx, server_name: str):
        """Restart a server"""
        if not self.has_required_role(ctx.author):
            await ctx.send("❌ You don't have permission to use this command.")
            return
        
        if server_name not in self.active_servers:
            await ctx.send(f"❌ Server '{server_name}' not found.")
            return
        
        try:
            container = self.docker_client.containers.get(self.active_servers[server_name]['container_id'])
            container.restart()
            
            self.active_servers[server_name]['status'] = 'running'
            self.save_active_servers()
            
            await ctx.send(f"✅ Server '{server_name}' restarted successfully.")
        except Exception as e:
            await ctx.send(f"❌ Error restarting server: {str(e)}")
    
    @commands.command(name='remove_server')
    async def remove_server(self, ctx, server_name: str):
        """Remove a server (stops and deletes container)"""
        if not self.has_required_role(ctx.author):
            await ctx.send("❌ You don't have permission to use this command.")
            return
        
        if server_name not in self.active_servers:
            await ctx.send(f"❌ Server '{server_name}' not found.")
            return
        
        try:
            container = self.docker_client.containers.get(self.active_servers[server_name]['container_id'])
            container.stop()
            container.remove()
            
            del self.active_servers[server_name]
            self.save_active_servers()
            
            await ctx.send(f"✅ Server '{server_name}' removed successfully.")
        except Exception as e:
            await ctx.send(f"❌ Error removing server: {str(e)}")
    
    @commands.command(name='server_logs')
    async def server_logs(self, ctx, server_name: str, lines: int = 50):
        """Get server logs"""
        if not self.has_required_role(ctx.author):
            await ctx.send("❌ You don't have permission to use this command.")
            return
        
        if server_name not in self.active_servers:
            await ctx.send(f"❌ Server '{server_name}' not found.")
            return
        
        try:
            container = self.docker_client.containers.get(self.active_servers[server_name]['container_id'])
            logs = container.logs(tail=lines).decode('utf-8')
            
            # Split logs into chunks if too long for Discord
            if len(logs) > 1900:  # Discord message limit is 2000 chars
                chunks = [logs[i:i+1900] for i in range(0, len(logs), 1900)]
                for i, chunk in enumerate(chunks):
                    await ctx.send(f"```\n{chunk}\n```")
                    if i < len(chunks) - 1:
                        await asyncio.sleep(1)  # Avoid rate limiting
            else:
                await ctx.send(f"```\n{logs}\n```")
                
        except Exception as e:
            await ctx.send(f"❌ Error getting logs: {str(e)}")
    
    @commands.command(name='server_status')
    async def server_status(self, ctx, server_name: str):
        """Get detailed server status"""
        if not self.has_required_role(ctx.author):
            await ctx.send("❌ You don't have permission to use this command.")
            return
        
        if server_name not in self.active_servers:
            await ctx.send(f"❌ Server '{server_name}' not found.")
            return
        
        try:
            container = self.docker_client.containers.get(self.active_servers[server_name]['container_id'])
            stats = container.stats(stream=False)
            
            embed = discord.Embed(title=f"Server Status: {server_name}", color=0x0099ff)
            embed.add_field(name="Container Status", value=container.status, inline=True)
            embed.add_field(name="Template", value=self.active_servers[server_name]['template'], inline=True)
            embed.add_field(name="Port", value=self.active_servers[server_name].get('port', 'Auto'), inline=True)
            embed.add_field(name="Created By", value=self.active_servers[server_name]['created_by'], inline=True)
            embed.add_field(name="Container ID", value=container.short_id, inline=True)
            
            # Add resource usage if container is running
            if container.status == 'running':
                memory_usage = stats['memory_stats']['usage'] / 1024 / 1024  # MB
                memory_limit = stats['memory_stats']['limit'] / 1024 / 1024  # MB
                embed.add_field(name="Memory Usage", value=f"{memory_usage:.1f}MB / {memory_limit:.1f}MB", inline=True)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error getting status: {str(e)}")

class MinecraftBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        
    async def on_ready(self):
        logger.info(f'{self.user} has connected to Discord!')
        await self.add_cog(MinecraftServerManager(self))
        
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: {error.param}")
        else:
            await ctx.send(f"❌ An error occurred: {str(error)}")
            logger.error(f"Command error: {error}")

def main():
    if not DISCORD_TOKEN:
        print("Please set the DISCORD_TOKEN environment variable")
        return
    
    bot = MinecraftBot()
    bot.run(DISCORD_TOKEN)

if __name__ == "__main__":
    main()