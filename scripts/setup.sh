#!/bin/bash

# Discord Minecraft Server Manager Bot Setup Script
# This script automates the initial setup process

set -e

echo "=== Discord Minecraft Server Manager Bot Setup ==="
echo

# Check if Python 3.11+ is installed
check_python() {
    echo "Checking Python version..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        echo "Python $PYTHON_VERSION found"
        
        # Check if version is 3.11 or higher
        if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 11) else 1)'; then
            echo "✅ Python version is compatible"
        else
            echo "❌ Python 3.11+ is required, found $PYTHON_VERSION"
            exit 1
        fi
    else
        echo "❌ Python 3 not found. Please install Python 3.11+"
        exit 1
    fi
}

# Check if Docker is installed and running
check_docker() {
    echo "Checking Docker installation..."
    if command -v docker &> /dev/null; then
        echo "✅ Docker found"
        if docker ps &> /dev/null; then
            echo "✅ Docker daemon is running"
        else
            echo "❌ Docker daemon is not running. Please start Docker."
            exit 1
        fi
    else
        echo "❌ Docker not found. Please install Docker."
        exit 1
    fi
}

# Create virtual environment
setup_venv() {
    echo "Setting up Python virtual environment..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo "✅ Virtual environment created"
    else
        echo "✅ Virtual environment already exists"
    fi
}

# Install dependencies
install_dependencies() {
    echo "Installing Python dependencies..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
}

# Create directories
create_directories() {
    echo "Creating necessary directories..."
    mkdir -p data logs config
    touch logs/.gitkeep data/.gitkeep
    echo "✅ Directories created"
}

# Setup environment file
setup_env() {
    echo "Setting up environment configuration..."
    if [ ! -f ".env" ]; then
        cp .env.example .env
        echo "✅ Environment file created from template"
        echo
        echo "⚠️  IMPORTANT: Please edit .env file with your Discord bot token"
        echo "   You can get a token from: https://discord.com/developers/applications"
        echo
    else
        echo "✅ Environment file already exists"
    fi
}

# Check Docker permissions
check_docker_permissions() {
    echo "Checking Docker permissions..."
    if docker ps &> /dev/null; then
        echo "✅ Docker permissions are correct"
    else
        echo "⚠️  Docker permission issue detected"
        echo "   You may need to add your user to the docker group:"
        echo "   sudo usermod -aG docker $USER"
        echo "   Then restart your terminal or reboot"
    fi
}

# Main setup function
main() {
    echo "Starting setup process..."
    echo
    
    check_python
    echo
    
    check_docker
    echo
    
    setup_venv
    echo
    
    install_dependencies
    echo
    
    create_directories
    echo
    
    setup_env
    echo
    
    check_docker_permissions
    echo
    
    echo "=== Setup Complete! ==="
    echo
    echo "Next steps:"
    echo "1. Edit .env file with your Discord bot token"
    echo "2. Configure your Discord bot permissions"
    echo "3. Run the bot:"
    echo "   source venv/bin/activate"
    echo "   python main.py"
    echo
    echo "Or use Docker:"
    echo "   docker-compose up -d"
    echo
    echo "For more information, see docs/SETUP.md"
}

# Run main function
main
