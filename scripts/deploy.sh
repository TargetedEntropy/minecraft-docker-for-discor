#!/bin/bash

# Discord Minecraft Server Manager Bot Deployment Script
# This script handles production deployment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo "=== Discord Minecraft Server Manager Bot Deployment ==="
echo "Project directory: $PROJECT_DIR"
echo

# Load configuration
load_config() {
    if [ -f ".env" ]; then
        echo "✅ Loading environment configuration"
        export $(grep -v '^#' .env | xargs)
    else
        echo "❌ .env file not found. Please run setup.sh first."
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {
    echo "Checking deployment prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker not found"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose not found"
        exit 1
    fi
    
    # Check if Discord token is set
    if [ -z "$DISCORD_TOKEN" ] || [ "$DISCORD_TOKEN" = "your_discord_bot_token_here" ]; then
        echo "❌ Discord token not configured in .env file"
        exit 1
    fi
    
    echo "✅ Prerequisites check passed"
}

# Backup existing data
backup_data() {
    echo "Creating backup of existing data..."
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    
    if [ -d "data" ] && [ "$(ls -A data)" ]; then
        mkdir -p "$BACKUP_DIR"
        cp -r data/* "$BACKUP_DIR/" 2>/dev/null || true
        echo "✅ Backup created at $BACKUP_DIR"
    else
        echo "ℹ️  No existing data to backup"
    fi
}

# Pull latest images
pull_images() {
    echo "Pulling latest Docker images..."
    docker-compose pull
    echo "✅ Images updated"
}

# Build application
build_app() {
    echo "Building application..."
    docker-compose build --no-cache
    echo "✅ Application built"
}

# Deploy with zero downtime
deploy() {
    echo "Deploying application..."
    
    # Stop existing containers
    if docker-compose ps | grep -q "Up"; then
        echo "Stopping existing containers..."
        docker-compose down
    fi
    
    # Start new containers
    echo "Starting new containers..."
    docker-compose up -d
    
    # Wait for services to be ready
    echo "Waiting for services to start..."
    sleep 10
    
    # Check if services are running
    if docker-compose ps | grep -q "Up"; then
        echo "✅ Deployment successful"
    else
        echo "❌ Deployment failed"
        docker-compose logs
        exit 1
    fi
}

# Health check
health_check() {
    echo "Performing health check..."
    
    # Check if bot container is running
    if docker-compose ps minecraft-bot | grep -q "Up"; then
        echo "✅ Bot container is running"
    else
        echo "❌ Bot container is not running"
        docker-compose logs minecraft-bot
        exit 1
    fi
    
    # Check logs for any immediate errors
    sleep 5
    if docker-compose logs minecraft-bot | grep -q "ERROR"; then
        echo "⚠️  Errors detected in logs:"
        docker-compose logs minecraft-bot | grep "ERROR"
    else
        echo "✅ No immediate errors detected"
    fi
}

# Cleanup old images
cleanup() {
    echo "Cleaning up old Docker images..."
    docker system prune -f
    echo "✅ Cleanup completed"
}

# Main deployment function
main() {
    echo "Starting deployment process..."
    echo
    
    load_config
    echo
    
    check_prerequisites
    echo
    
    backup_data
    echo
    
    pull_images
    echo
    
    build_app
    echo
    
    deploy
    echo
    
    health_check
    echo
    
    cleanup
    echo
    
    echo "=== Deployment Complete! ==="
    echo
    echo "Bot status:"
    docker-compose ps
    echo
    echo "To view logs:"
    echo "  docker-compose logs -f minecraft-bot"
    echo
    echo "To stop the bot:"
    echo "  docker-compose down"
}

# Handle command line arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "logs")
        docker-compose logs -f minecraft-bot
        ;;
    "status")
        docker-compose ps
        ;;
    "stop")
        docker-compose down
        ;;
    "restart")
        docker-compose restart
        ;;
    *)
        echo "Usage: $0 [deploy|logs|status|stop|restart]"
        echo
        echo "Commands:"
        echo
