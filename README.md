# Discord Minecraft Server Manager 🎮

A powerful Discord bot for managing Minecraft servers using Docker containers with template support and role-based permissions.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Discord.py](https://img.shields.io/badge/Discord.py-2.3+-blue.svg)](https://discordpy.readthedocs.io/)
[![Docker](https://img.shields.io/badge/Docker-Required-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Features ✨

- 🐳 **Docker Integration**: Seamlessly manage Minecraft servers in Docker containers
- 📋 **Template System**: Pre-configured templates for different server types (Vanilla, Forge, Modded)
- 🔐 **Role-Based Permissions**: Secure command access with Discord role restrictions
- 📊 **Server Monitoring**: Real-time status, logs, and resource monitoring
- 💾 **Persistent Data**: Automatic volume management for world saves
- 🔧 **Easy Configuration**: Environment-based configuration with `.env` support
- 🚀 **Production Ready**: Docker Compose deployment with health checks

## Quick Start 🚀

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Discord Bot Token

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/minecraft-discord-bot.git
   cd minecraft-discord-bot
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Discord token and settings
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the bot**
   ```bash
   python main.py
   ```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f minecraft-bot
```

## Configuration ⚙️

### Environment Variables

Create a `.env` file in the root directory:

```env
# Required
DISCORD_TOKEN=your_discord_bot_token

# Optional
ALLOWED_ROLES=Admin,Moderator,ServerManager
DEFAULT_MEMORY=2G
```

### Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application and bot
3. Copy the bot token to your `.env` file
4. Invite the bot to your server with appropriate permissions

## Commands 🎯

| Command | Description | Usage |
|---------|-------------|-------|
| `!list_templates` | Show available server templates | `!list_templates` |
| `!create_server` | Create a new server | `!create_server myserver vanilla 25565` |
| `!list_servers` | List all active servers | `!list_servers` |
| `!start_server` | Start a stopped server | `!start_server myserver` |
| `!stop_server` | Stop a running server | `!stop_server myserver` |
| `!restart_server` | Restart a server | `!restart_server myserver` |
| `!remove_server` | Remove a server | `!remove_server myserver` |
| `!server_logs` | Get server logs | `!server_logs myserver 50` |
| `!server_status` | Get detailed server status | `!server_status myserver` |

## Server Templates 📋

Built-in templates include:
- **Vanilla**: Standard Minecraft server
- **Forge**: Modded server with Forge
- **Modded**: Custom modpack support

Templates are fully customizable in `config/templates.json`.

## Documentation 📚

- [Setup Guide](docs/SETUP.md)
- [Command Reference](docs/COMMANDS.md)
- [API Documentation](docs/API.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## Contributing 🤝

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support 💬

- 🐛 [Report Issues](https://github.com/yourusername/minecraft-discord-bot/issues)
- 💡 [Request Features](https://github.com/yourusername/minecraft-discord-bot/issues/new?template=feature_request.md)
- 📖 [Documentation](docs/)

## Acknowledgments 🙏

- [discord.py](https://github.com/Rapptz/discord.py) - Discord API wrapper
- [itzg/minecraft-server](https://github.com/itzg/docker-minecraft-server) - Docker Minecraft server image
- [Docker](https://www.docker.com/) - Containerization platform
