#!/bin/bash

# Automated pytest setup for WSL/Linux
# This script handles the "externally-managed-environment" error

set -e  # Exit on error

echo "🚀 Setting up pytest for Horizon Sync..."
echo ""

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📍 Working directory: $SCRIPT_DIR"
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✓ $PYTHON_VERSION found"
echo ""

# Remove old venv if exists
if [ -d "venv_wsl" ]; then
    echo "🗑️  Removing old virtual environment..."
    rm -rf venv_wsl
    echo ""
fi

# Create new virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv_wsl
echo "✓ Virtual environment created"
echo ""

# Use the venv's pip to avoid externally-managed-environment error
VENV_PIP="./venv_wsl/bin/pip"
VENV_PYTEST="./venv_wsl/bin/pytest"

# Upgrade pip
echo "📦 Upgrading pip..."
$VENV_PIP install --upgrade pip --quiet
echo "✓ pip upgraded"
echo ""

# Install dependencies
echo "📚 Installing dependencies..."
if [ -f "requirements.txt" ]; then
    $VENV_PIP install -r requirements.txt --quiet
    echo "✓ Dependencies from requirements.txt installed"
else
    echo "⚠️  requirements.txt not found, installing minimal packages..."
    $VENV_PIP install fastapi uvicorn sqlalchemy asyncpg pytest pytest-asyncio pytest-cov httpx --quiet
    echo "✓ Essential packages installed"
fi
echo ""

# Verify pytest
echo "✓ Verifying pytest..."
$VENV_PYTEST --version
echo ""

# Success message
echo "✅ Setup complete!"
echo ""
echo "📌 To run tests:"
echo ""
echo "1. Quick test:"
echo "   ./venv_wsl/bin/pytest tests/services/test_auth_service.py -v"
echo ""
echo "2. All tests:"
echo "   ./venv_wsl/bin/pytest tests/ -v"
echo ""
echo "3. With coverage:"
echo "   ./venv_wsl/bin/pytest tests/ --cov=services --cov-report=html"
echo ""
echo "📌 Or activate the venv first:"
echo "   source venv_wsl/bin/activate"
echo "   pytest tests/ -v"
echo ""
