"""
Tests for the main bot functionality
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from src.bot import MinecraftBot


class TestMinecraftBot:
    """Test cases for the MinecraftBot class"""
    
    @pytest.fixture
    def bot(self):
        """Create a bot instance for testing"""
        return MinecraftBot()
    
    def test_bot_initialization(self, bot):
        """Test bot initialization"""
        assert bot.command_prefix == '!'
        assert bot.intents.message_content is True
        assert bot.intents.guilds is True
    
    @pytest.mark.asyncio
    async def test_on_ready(self, bot):
        """Test on_ready event handler"""
        bot.user = Mock()
        bot.user.name = "TestBot"
        bot.guilds = [Mock(), Mock()]
        bot.change_presence = Mock()
        
        await bot.on_ready()
        
        # Verify that change_presence was called
        bot.change_presence.assert_called_once()
