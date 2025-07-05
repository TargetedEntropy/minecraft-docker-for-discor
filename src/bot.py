"""
Main bot class and initialization
"""

import discord
from discord.ext import commands
import logging
from pathlib import Path
import sys

from config.settings import settings

logger = logging.getLogger(__name__)


class MinecraftBot(commands.Bot):
    """Main Discord bot class"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.guild_messages = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=commands.DefaultHelpCommand(no_category="Commands")
        )
        
    async def setup_hook(self):
        """Load cogs and perform setup tasks"""
        logger.info("Setting up bot...")
        
        # Load cogs
        cogs_to_load = [
            "cogs.minecraft_manager",
            "cogs.admin"
        ]
        
        for cog in cogs_to_load:
            try:
                await self.load_extension(f"src.{cog}")
                logger.info(f"Loaded cog: {cog}")
            except Exception as e:
                logger.error(f"Failed to load cog {cog}: {e}")
        
        logger.info("Bot setup completed")
    
    async def on_ready(self):
        """Event handler for when the bot is ready"""
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')
        
        # Set bot status
        activity = discord.Game(name="Managing Minecraft Servers")
        await self.change_presence(activity=activity)
    
    async def on_command_error(self, ctx, error):
        """Global error handler for commands"""
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: `{error.param}`")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"❌ Invalid argument: {str(error)}")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ I don't have the required permissions to execute this command.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"❌ Command is on cooldown. Try again in {error.retry_after:.2f} seconds.")
        else:
            await ctx.send(f"❌ An error occurred: {str(error)}")
            logger.error(f"Command error in {ctx.command}: {error}", exc_info=True)
    
    async def on_guild_join(self, guild):
        """Event handler for when the bot joins a guild"""
        logger.info(f"Joined guild: {guild.name} (ID: {guild.id})")
    
    async def on_guild_remove(self, guild):
        """Event handler for when the bot leaves a guild"""
        logger.info(f"Left guild: {guild.name} (ID: {guild.id})")
