#!/bin/bash

# Fix for TLS/Certificate errors in WSL Python venv
# This script handles the "Could not find a suitable TLS CA certificate bundle" error

set -e

echo "🔧 Fixing TLS Certificate Issues in WSL..."
echo ""

# Step 1: Install system certificates
echo "📦 Step 1/5: Installing system certificates..."
sudo apt-get update -qq && sudo apt-get install -y ca-certificates > /dev/null 2>&1
echo "✓ System certificates installed"
echo ""

# Step 2: Navigate to project directory
PROJECT_DIR="/mnt/d/Code/CRM/horizon-sync-be"
echo "📍 Step 2/5: Navigating to project..."
cd "$PROJECT_DIR"
echo "✓ In directory: $PROJECT_DIR"
echo ""

# Step 3: Remove corrupted venv
echo "🗑️  Step 3/5: Removing corrupted virtual environment..."
if [ -d "venv_wsl" ]; then
    rm -rf venv_wsl
    echo "✓ Old venv removed"
else
    echo "✓ No old venv to remove"
fi
echo ""

# Step 4: Create fresh venv
echo "📦 Step 4/5: Creating fresh virtual environment..."
python3 -m venv venv_wsl
echo "✓ New venv created"
echo ""

# Step 5: Install dependencies
echo "📚 Step 5/5: Installing dependencies..."
./venv_wsl/bin/pip install --upgrade pip setuptools --no-cache-dir > /dev/null 2>&1
echo "✓ pip upgraded"

if [ -f "requirements.txt" ]; then
    ./venv_wsl/bin/pip install -r requirements.txt --no-cache-dir > /dev/null 2>&1
    echo "✓ Dependencies installed from requirements.txt"
else
    echo "⚠️  requirements.txt not found"
    ./venv_wsl/bin/pip install fastapi uvicorn sqlalchemy asyncpg pytest pytest-asyncio pytest-cov httpx --no-cache-dir > /dev/null 2>&1
    echo "✓ Essential packages installed"
fi
echo ""

# Verify pytest works
echo "✓ Verifying pytest installation..."
PYTEST_VERSION=$( ./venv_wsl/bin/pytest --version 2>&1 | head -1)
echo "✓ $PYTEST_VERSION"
echo ""

# Success!
echo "✅ TLS Certificate Issues Fixed!"
echo ""
echo "🚀 You can now run tests:"
echo ""
echo "   Option 1 (with full path):"
echo "   ./venv_wsl/bin/pytest tests/ -v"
echo ""
echo "   Option 2 (activate venv first):"
echo "   source venv_wsl/bin/activate"
echo "   pytest tests/ -v"
echo ""
echo "📌 Test a single service:"
echo "   ./venv_wsl/bin/pytest tests/services/test_auth_service.py -v"
echo ""
