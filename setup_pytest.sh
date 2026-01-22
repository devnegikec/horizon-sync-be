#!/bin/bash

# Setup script for pytest in WSL/Linux environment

echo "🔧 Setting up pytest environment..."

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📍 Working directory: $SCRIPT_DIR"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.12 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✓ Python 3 found: $PYTHON_VERSION"

# Remove old venv if it exists
if [ -d "venv_wsl" ]; then
    echo "🗑️  Removing old virtual environment..."
    rm -rf venv_wsl
fi

# Create new virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv_wsl --upgrade-deps

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source venv_wsl/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install dependencies from requirements.txt
if [ -f "requirements.txt" ]; then
    echo "📚 Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    echo "⚠️  requirements.txt not found. Installing essential packages..."
    pip install fastapi uvicorn sqlalchemy asyncpg pytest pytest-asyncio pytest-cov httpx
fi

# Verify pytest installation
if pytest --version &> /dev/null; then
    echo ""
    echo "✅ Setup complete!"
    echo ""
    echo "📌 To use pytest:"
    echo ""
    echo "1. Activate the virtual environment:"
    echo "   source venv_wsl/bin/activate"
    echo ""
    echo "2. Run tests:"
    echo "   pytest tests/ -v"
    echo ""
    echo "3. Run specific service tests:"
    echo "   pytest tests/services/test_auth_service.py -v"
    echo ""
    echo "4. Run with coverage:"
    echo "   pytest tests/ --cov=services --cov-report=html"
    echo ""
else
    echo "❌ pytest installation failed. Please check your Python installation."
    exit 1
fi
