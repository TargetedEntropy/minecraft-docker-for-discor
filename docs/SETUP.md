# Setup Guide

This guide will walk you through setting up the Discord Minecraft Server Manager bot.

## Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose
- Discord bot token
- Basic knowledge of Discord and Minecraft servers

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/minecraft-discord-bot.git
cd minecraft-discord-bot
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your settings
nano .env
```

Required environment variables:
- `DISCORD_TOKEN`: Your Discord bot token
- `ALLOWED_ROLES`: Comma-separated list of roles that can use the bot

### 4. Discord Bot Setup

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the "Bot" section and create a bot
4. Copy the bot token and add it to your `.env` file
5. Under "Privileged Gateway Intents", enable:
   - Message Content Intent
   - Server Members Intent (if needed)

### 5. Bot Permissions

When inviting the bot to your server, ensure it has these permissions:
- Send Messages
- Read Message History
- Use Slash Commands
- Embed Links
- Attach Files

### 6. Docker Setup

Ensure Docker is installed and running:

```bash
# Test Docker installation
docker --version
docker-compose --version

# Test Docker daemon
docker ps
```

### 7. Run the Bot

#### Option A: Direct Python Execution
```bash
python main.py
```

#### Option B: Docker Compose
```bash
docker-compose up -d
```

## Configuration

### Server Templates

Edit `config/templates.json` to customize server templates:

```json
{
  "custom_template": {
    "name": "Custom Server",
    "description": "My custom Minecraft server",
    "image": "itzg/minecraft-server:latest",
    "environment": {
      "EULA": "TRUE",
      "TYPE": "FORGE",
      "VERSION": "1.20.1",
      "MEMORY": "4G"
    }
  }
}
```

### Role Configuration

Configure allowed roles in your `.env` file:

```env
ALLOWED_ROLES=Admin,Moderator,ServerManager,VIP
```

## Troubleshooting

### Common Issues

1. **Bot doesn't respond**: Check bot permissions and token
2. **Docker permission denied**: Ensure user is in docker group
3. **Port conflicts**: Use different ports or check for conflicts

### Logs

Check logs for debugging:

```bash
# View bot logs
tail -f logs/bot.log

# View Docker logs
docker-compose logs -f minecraft-bot
```

## Security Considerations

- Keep your Discord token secure
- Use strong passwords for any databases
- Regularly update dependencies
- Monitor bot permissions
- Use Docker security best practices

## Next Steps

- Read the [Commands Reference](COMMANDS.md)
- Check out the [API Documentation](API.md)
- Join our support Discord (if available)
