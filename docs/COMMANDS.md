# Commands Reference

Complete reference for all Discord Minecraft Server Manager bot commands.

## Prerequisites

All commands require users to have one of the configured roles (Admin, Moderator, ServerManager by default).

## Server Management Commands

### `!list_templates`
Lists all available server templates.

**Usage:** `!list_templates`

**Example:**
```
!list_templates
```

**Output:** Displays an embed with all available templates, their types, memory allocations, and descriptions.

---

### `!create_server`
Creates a new Minecraft server from a template.

**Usage:** `!create_server <server_name> <template_name> [port]`

**Parameters:**
- `server_name`: Unique name for the server (letters, numbers, underscores, hyphens only)
- `template_name`: Name of the template to use
- `port`: Optional port number (1024-65535)

**Examples:**
```
!create_server myserver vanilla
!create_server modded_server forge 25566
!create_server survival_world vanilla 25567
```

---

### `!list_servers`
Lists all active servers with their status.

**Usage:** `!list_servers`

**Example:**
```
!list_servers
```

**Output:** Displays an embed showing all servers, their status, template, port, and creator.

---

### `!start_server`
Starts a stopped server.

**Usage:** `!start_server <server_name>`

**Parameters:**
- `server_name`: Name of the server to start

**Example:**
```
!start_server myserver
```

---

### `!stop_server`
Stops a running server.

**Usage:** `!stop_server <server_name>`

**Parameters:**
- `server_name`: Name of the server to stop

**Example:**
```
!stop_server myserver
```

---

### `!restart_server`
Restarts a server (stops and starts it).

**Usage:** `!restart_server <server_name>`

**Parameters:**
- `server_name`: Name of the server to restart

**Example:**
```
!restart_server myserver
```

---

### `!remove_server`
Permanently removes a server (stops and deletes the container).

**Usage:** `!remove_server <server_name>`

**Parameters:**
- `server_name`: Name of the server to remove

**Example:**
```
!remove_server myserver
```

**Warning:** This action is irreversible and will delete the server container (but not the world data).

---

### `!server_logs`
Retrieves recent logs from a server.

**Usage:** `!server_logs <server_name> [lines]`

**Parameters:**
- `server_name`: Name of the server
- `lines`: Number of log lines to retrieve (default: 50, max: 100)

**Examples:**
```
!server_logs myserver
!server_logs myserver 100
```

---

### `!server_status`
Shows detailed status information for a server.

**Usage:** `!server_status <server_name>`

**Parameters:**
- `server_name`: Name of the server

**Example:**
```
!server_status myserver
```

**Output:** Displays an embed with container status, memory usage, template info, and more.

## Administrative Commands

### `!bot_info`
Shows bot information and statistics.

**Usage:** `!bot_info`

**Example:**
```
!bot_info
```

**Output:** Displays bot name, ID, guild count, user count, and latency.

---

### `!list_cogs`
Lists all loaded bot modules (cogs).

**Usage:** `!list_cogs`

**Example:**
```
!list_cogs
```

---

### `!reload_cog`
Reloads a specific bot module (owner only).

**Usage:** `!reload_cog <cog_name>`

**Parameters:**
- `cog_name`: Name of the cog to reload

**Example:**
```
!reload_cog minecraft_manager
```

**Note:** This command is restricted to the bot owner.

## Command Examples

### Creating and Managing a Server
```
# List available templates
!list_templates

# Create a new server
!create_server survival vanilla 25565

# Check server status
!server_status survival

# View server logs
!server_logs survival 50

# Restart the server
!restart_server survival

# Stop the server
!stop_server survival

# Remove the server
!remove_server survival
```

### Batch Operations
```
# Create multiple servers
!create_server lobby vanilla 25565
!create_server creative vanilla 25566
!create_server modded forge 25567

# List all servers
!list_servers

# Check individual statuses
!server_status lobby
!server_status creative
!server_status modded
```

## Error Messages

Common error messages and their meanings:

- `❌ You don't have permission to use this command.` - User lacks required role
- `❌ Server 'name' not found.` - Server doesn't exist in the database
- `❌ Template 'name' not found.` - Invalid template name
- `❌ Server 'name' already exists.` - Server name is already in use
- `❌ Invalid server name.` - Server name contains invalid characters
- `❌ Invalid port number.` - Port is outside valid range (1024-65535)
- `❌ Maximum 100 lines allowed.` - Too many log lines requested

## Tips and Best Practices

1. **Naming Convention**: Use descriptive server names like `survival-world` or `creative-build`
2. **Port Management**: Keep track of used ports to avoid conflicts
3. **Resource Monitoring**: Regularly check server status and memory usage
4. **Log Checking**: Use server logs to troubleshoot issues
5. **Template Usage**: Use appropriate templates for different server types
6. **Cleanup**: Remove unused servers to free up resources
