# API Documentation

Technical documentation for the Discord Minecraft Server Manager bot.

## Architecture Overview

The bot follows a modular architecture with the following components:

- **Bot Core** (`src/bot.py`): Main bot class and event handlers
- **Cogs** (`src/cogs/`): Modular command groups
- **Models** (`src/models/`): Data models for servers and templates
- **Utils** (`src/utils/`): Helper utilities for Docker, permissions, and validation
- **Config** (`config/`): Configuration management

## Core Classes

### `MinecraftBot`

Main bot class that handles Discord events and cog loading.

```python
class MinecraftBot(commands.Bot):
    def __init__(self):
        # Bot initialization with intents and prefix
    
    async def setup_hook(self):
        # Load cogs and perform setup
    
    async def on_ready(self):
        # Handle bot ready event
```

### `MinecraftServerManager`

Primary cog for server management commands.

```python
class MinecraftServerManager(commands.Cog):
    def __init__(self, bot):
        # Initialize Docker helper, permissions, etc.
    
    async def create_server(self, ctx, server_name, template_name, port=None):
        # Create new Minecraft server
```

## Data Models

### `MinecraftServer`

Represents a Minecraft server instance.

```python
@dataclass
class MinecraftServer:
    name: str
    template: ServerTemplate
    port: Optional[int] = None
    created_by: str = ""
    created_at: str = ""
    status: str = "created"
    container_id: str = ""
```

### `ServerTemplate`

Represents a server template configuration.

```python
@dataclass
class ServerTemplate:
    name: str
    description: str
    image: str
    environment: Dict[str, str]
    ports: Dict[str, Optional[int]]
    volumes: Dict[str, Any]
    restart_policy: Dict[str, str]
```

## Utility Classes

### `DockerHelper`

Manages Docker container operations.

**Methods:**
- `create_server(server)`: Create and start a new container
- `start_container(container_id)`: Start a stopped container
- `stop_container(container_id)`: Stop a running container
- `restart_container(container_id)`: Restart a container
- `remove_container(container_id)`: Remove a container
- `get_container_status(container_id)`: Get container status
- `get_container_logs(container_id, lines)`: Get container logs
- `get_detailed_status(container_id)`: Get detailed status with metrics

### `PermissionChecker`

Handles user permission validation.

**Methods:**
- `has_required_role(member)`: Check if user has required role
- `is_server_admin(member)`: Check if user is server admin
- `can_manage_server(member, server_info)`: Check server-specific permissions

### `ServerValidator`

Validates user inputs.

**Methods:**
- `validate_server_name(name)`: Validate server name format
- `validate_port(port)`: Validate port number
- `validate_memory(memory)`: Validate memory format
- `validate_minecraft_version(version)`: Validate version format

## Configuration

### Environment Variables

Configuration is managed through environment variables:

```python
class Settings:
    DISCORD_TOKEN: str
    ALLOWED_ROLES: List[str]
    DOCKER_HOST: str
    TEMPLATES_FILE: str
    SERVERS_FILE: str
    DEFAULT_MEMORY: str
    LOG_LEVEL: str
```

### Template Format

Server templates are defined in JSON format:

```json
{
  "template_name": {
    "name": "Display Name",
    "description": "Template description",
    "image": "docker/image:tag",
    "environment": {
      "ENV_VAR": "value"
    },
    "ports": {
      "25565/tcp": null
    },
    "volumes": {},
    "restart_policy": {
      "Name": "unless-stopped"
    }
  }
}
```

## Docker Integration

### Container Naming

Containers are named using the pattern: `minecraft_{server_name}`

### Volume Management

Each server gets a dedicated Docker volume: `minecraft_{server_name}`

### Network Configuration

Servers use bridge networking with port mapping to host ports.

### Resource Limits

Memory limits are set via environment variables in templates.

## Error Handling

### Docker Errors

Common Docker errors and their handling:

- `docker.errors.NotFound`: Container doesn't exist
- `docker.errors.APIError`: Docker daemon error
- `ConnectionError`: Docker daemon unreachable

### Discord Errors

Discord-related error handling:

- `commands.CommandNotFound`: Ignored
- `commands.MissingRequiredArgument`: User-friendly error message
- `commands.BadArgument`: Input validation error
- `commands.MissingPermissions`: Permission denied

## Logging

### Log Levels

- `INFO`: General bot operations
- `WARNING`: Non-critical issues
- `ERROR`: Critical errors requiring attention
- `DEBUG`: Detailed debugging information

### Log Format

```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

## Security Considerations

### Permission System

- Role-based access control
- Server creator privileges
- Admin override capabilities

### Input Validation

- Server name sanitization
- Port range validation
- Memory format validation

### Docker Security

- Non-root container execution
- Volume isolation
- Network segmentation

## Extension Points

### Adding New Commands

1. Create command method in appropriate cog
2. Add permission checks
3. Implement validation
4. Add error handling
5. Update documentation

### Custom Templates

1. Define template in `templates.json`
2. Set appropriate environment variables
3. Configure resource limits
4. Test deployment

### New Cogs

1. Create cog file in `src/cogs/`
2. Implement cog class with `setup` function
3. Add cog loading to bot setup
4. Document new commands

## Performance Considerations

### Resource Monitoring

- Container memory usage tracking
- CPU usage monitoring (if needed)
- Disk space management

### Optimization

- Async operations for Docker calls
- Efficient data serialization
- Log rotation

## Testing

### Unit Tests

Test coverage includes:
- Model serialization/deserialization
- Permission checking logic
- Input validation
- Docker helper methods

### Integration Tests

- Full command execution
- Docker container lifecycle
- Error handling scenarios
