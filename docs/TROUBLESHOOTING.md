# Troubleshooting Guide

Common issues and solutions for the Discord Minecraft Server Manager bot.

## Bot Issues

### Bot Doesn't Respond to Commands

**Symptoms:**
- Bot is online but doesn't respond to `!` commands
- No error messages in console

**Possible Causes & Solutions:**

1. **Missing Permissions**
   - Ensure bot has "Send Messages" permission in the channel
   - Check "Read Message History" permission
   - Verify "Use Slash Commands" if using slash commands

2. **Incorrect Role Configuration**
   - Check your role name in Discord matches `ALLOWED_ROLES` in `.env`
   - Role names are case-sensitive
   - User must have at least one of the configured roles

3. **Message Content Intent Missing**
   - Go to Discord Developer Portal > Your App > Bot
   - Enable "Message Content Intent" under "Privileged Gateway Intents"
   - Restart the bot

**Solution:**
```bash
# Check bot permissions
!bot_info

# Verify role configuration
echo $ALLOWED_ROLES
```

### Bot Crashes on Startup

**Symptoms:**
- Bot exits immediately with error
- Connection errors in logs

**Common Errors & Solutions:**

1. **Invalid Discord Token**
   ```
   discord.errors.LoginFailure: Improper token has been passed
   ```
   - Verify `DISCORD_TOKEN` in `.env` file
   - Generate new token if necessary

2. **Docker Connection Failed**
   ```
   docker.errors.DockerException: Error while fetching server API version
   ```
   - Ensure Docker daemon is running: `docker ps`
   - Check Docker socket permissions
   - Add user to docker group: `sudo usermod -aG docker $USER`

3. **Missing Dependencies**
   ```
   ModuleNotFoundError: No module named 'docker'
   ```
   - Install requirements: `pip install -r requirements.txt`
   - Activate virtual environment

## Docker Issues

### Permission Denied Errors

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied: '/var/run/docker.sock'
```

**Solutions:**

1. **Add User to Docker Group**
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   # Restart terminal or reboot
   ```

2. **Fix Docker Socket Permissions**
   ```bash
   sudo chmod 666 /var/run/docker.sock
   ```

3. **Use Docker with Sudo (not recommended)**
   ```bash
   sudo python main.py
   ```

### Container Creation Fails

**Symptoms:**
- Server creation command fails
- Error messages about image pulling or container creation

**Common Solutions:**

1. **Image Not Found**
   ```bash
   # Pull image manually
   docker pull itzg/minecraft-server:latest
   ```

2. **Port Already in Use**
   ```bash
   # Check port usage
   netstat -tlnp | grep :25565
   # Or use different port
   !create_server myserver vanilla 25566
   ```

3. **Insufficient Resources**
   ```bash
   # Check available memory
   free -h
   # Check disk space
   df -h
   ```

### Container Won't Start

**Symptoms:**
- Container created but shows "exited" status
- Server appears stopped immediately after creation

**Debugging Steps:**

1. **Check Container Logs**
   ```bash
   docker logs minecraft_servername
   ```

2. **Common Issues:**
   - EULA not accepted (should be automatic)
   - Invalid Minecraft version
   - Insufficient memory
   - Port conflicts

3. **Manual Container Inspection**
   ```bash
   docker inspect minecraft_servername
   ```

## Server Management Issues

### Server Shows Wrong Status

**Symptoms:**
- `!list_servers` shows incorrect status
- Server appears running but is actually stopped

**Solutions:**

1. **Refresh Server Status**
   ```
   !server_status servername
   ```

2. **Check Docker Directly**
   ```bash
   docker ps -a | grep minecraft_
   ```

3. **Restart Bot**
   - Sometimes the bot's internal state gets out of sync
   - Restart the bot to refresh all statuses

### Cannot Connect to Server

**Symptoms:**
- Server shows "running" but can't connect from Minecraft
- Connection timeout errors

**Debugging Steps:**

1. **Check Server Logs**
   ```
   !server_logs servername 100
   ```

2. **Verify Port Mapping**
   ```bash
   docker port minecraft_servername
   ```

3. **Check Firewall**
   ```bash
   # Ubuntu/Debian
   sudo ufw status
   sudo ufw allow 25565

   # CentOS/RHEL
   sudo firewall-cmd --list-all
   sudo firewall-cmd --add-port=25565/tcp --permanent
   ```

4. **Test Network Connectivity**
   ```bash
   telnet your_server_ip 25565
   ```

### Server Won't Stop/Start

**Symptoms:**
- Commands hang or timeout
- Server stuck in transitional state

**Solutions:**

1. **Force Stop Container**
   ```bash
   docker kill minecraft_servername
   ```

2. **Remove Stuck Container**
   ```bash
   docker rm -f minecraft_servername
   ```

3. **Recreate Server**
   ```
   !remove_server servername
   !create_server servername template_name port
   ```

## Template Issues

### Template Not Found

**Symptoms:**
```
❌ Template 'template_name' not found
```

**Solutions:**

1. **Check Available Templates**
   ```
   !list_templates
   ```

2. **Verify Template File**
   ```bash
   cat config/templates.json
   ```

3. **Fix JSON Syntax**
   ```bash
   # Validate JSON
   python -m json.tool config/templates.json
   ```

### Server Creation Fails with Template

**Symptoms:**
- Template exists but server creation fails
- Docker errors during container creation

**Common Issues:**

1. **Invalid Docker Image**
   - Check if image exists: `docker pull image_name`
   - Verify image tag is correct

2. **Invalid Environment Variables**
   - Check template environment section
   - Ensure required variables are set

3. **Invalid Memory Format**
   - Use format like "2G", "512M"
   - Check memory limits on your system

## Network Issues

### Port Conflicts

**Symptoms:**
```
Error: Port 25565 is already in use
```

**Solutions:**

1. **Find Process Using Port**
   ```bash
   lsof -i :25565
   netstat -tlnp | grep :25565
   ```

2. **Use Different Port**
   ```
   !create_server myserver vanilla 25566
   ```

3. **Stop Conflicting Service**
   ```bash
   # If another Minecraft server
   docker stop conflicting_container
   ```

### Cannot Access Server Externally

**Symptoms:**
- Server works locally but not from internet
- Friends can't connect

**Solutions:**

1. **Port Forwarding**
   - Configure router to forward port 25565 to your server
   - Use your external IP address

2. **Firewall Configuration**
   ```bash
   # Allow through firewall
   sudo ufw allow 25565
   ```

3. **Check ISP Restrictions**
   - Some ISPs block certain ports
   - Try different port numbers

## Performance Issues

### High Memory Usage

**Symptoms:**
- System running out of memory
- Servers crashing with OOM errors

**Solutions:**

1. **Monitor Memory Usage**
   ```bash
   docker stats
   free -h
   ```

2. **Adjust Server Memory**
   - Edit template memory settings
   - Reduce number of concurrent servers

3. **Add Swap Space**
   ```bash
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

### Slow Server Performance

**Symptoms:**
- High server lag
- Long response times

**Solutions:**

1. **Check Resource Usage**
   ```
   !server_status servername
   ```

2. **Optimize Server Settings**
   - Reduce view distance
   - Limit player count
   - Disable unnecessary plugins

3. **Hardware Upgrades**
   - More RAM
   - Faster CPU
   - SSD storage

## Logging and Debugging

### Enable Debug Logging

**Add to `.env`:**
```env
LOG_LEVEL=DEBUG
```

### Check Bot Logs

```bash
tail -f logs/bot.log
```

### Check Docker Logs

```bash
# Bot container logs
docker-compose logs -f minecraft-bot

# Specific server logs
docker logs minecraft_servername
```

### Manual Testing

```bash
# Test Docker connection
docker ps

# Test bot commands manually
python -c "
from src.utils.docker_helper import DockerHelper
helper = DockerHelper()
print('Docker connection successful')
"
```

## Getting Help

### Information to Gather

When seeking help, provide:

1. **Error Messages**
   - Full error text from logs
   - Commands that triggered the error

2. **System Information**
   ```bash
   # OS version
   cat /etc/os-release
   
   # Python version
   python --version
   
   # Docker version
   docker --version
   
   # Bot configuration (redact tokens)
   cat .env | grep -v TOKEN
   ```

3. **Bot Status**
   ```
   !bot_info
   !list_servers
   ```

### Common Debug Commands

```bash
# Check all running containers
docker ps

# Check bot process
ps aux | grep python

# Check network connectivity
ping discord.com

# Check disk space
df -h

# Check memory usage
free -h
```

### Log Analysis

```bash
# Search for errors in logs
grep -i error logs/bot.log

# Check recent activity
tail -100 logs/bot.log

# Monitor real-time logs
tail -f logs/bot.log
```
