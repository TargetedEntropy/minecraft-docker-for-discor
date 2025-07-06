"""
Administrative commands cog
"""

import discord
from discord.ext import commands
import logging
from src.utils.permissions import PermissionChecker

logger = logging.getLogger(__name__)


class AdminCommands(commands.Cog):
    """Administrative commands for bot management"""
    
    def __init__(self, bot):
        self.bot = bot
        self.permission_checker = PermissionChecker()
    
    @commands.command(name='info')
    async def info(self, ctx):
        """Get bot information and statistics"""
        if not self.permission_checker.has_required_role(ctx.author):
            await ctx.send("❌ You don't have permission to use this command.")
            return
        
        embed = discord.Embed(title="Bot Information", color=0x0099ff)
        embed.add_field(name="Bot Name", value=self.bot.user.name, inline=True)
        embed.add_field(name="Bot ID", value=self.bot.user.id, inline=True)
        embed.add_field(name="Guilds", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Users", value=len(set(self.bot.get_all_members())), inline=True)
        embed.add_field(name="Commands", value=len(self.bot.commands), inline=True)
        embed.add_field(name="Latency", value=f"{self.bot.latency * 1000:.2f}ms", inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='reload_cog')
    @commands.is_owner()
    async def reload_cog(self, ctx, cog_name: str):
        """Reload a specific cog"""
        try:
            await self.bot.reload_extension(f"src.cogs.{cog_name}")
            await ctx.send(f"✅ Reloaded cog: {cog_name}")
        except Exception as e:
            await ctx.send(f"❌ Error reloading cog: {str(e)}")
    
    @commands.command(name='list_cogs')
    async def list_cogs(self, ctx):
        """List all loaded cogs"""
        if not self.permission_checker.has_required_role(ctx.author):
            await ctx.send("❌ You don't have permission to use this command.")
            return
        
        cogs = list(self.bot.cogs.keys())
        embed = discord.Embed(title="Loaded Cogs", color=0x00ff00)
        embed.description = "\n".join(f"• {cog}" for cog in cogs)
        await ctx.send(embed=embed)


async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(AdminCommands(bot))
