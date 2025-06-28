#!/bin/bash
# Setup script for GoToSocial bot tools with virtual environment

set -e

echo "🤖 GoToSocial Bot Setup with Virtual Environment"
echo "==============================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "   Please install Python 3.7 or later and try again."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "🐍 Found Python $PYTHON_VERSION"

# Create virtual environment
VENV_DIR="gotosocial_bot_env"

if [ -d "$VENV_DIR" ]; then
    echo "📁 Virtual environment already exists at $VENV_DIR"
    read -p "   Remove and recreate? (y/N): " RECREATE
    if [[ $RECREATE =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing existing virtual environment..."
        rm -rf "$VENV_DIR"
    else
        echo "✅ Using existing virtual environment"
    fi
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run tests
echo "🧪 Running tests..."
python test_setup.py

if [ $? -eq 0 ]; then
    echo
    echo "🎉 Setup complete! Your GoToSocial bot tools are ready."
    echo
    echo "📋 To use the tools:"
    echo "   1. Activate the virtual environment:"
    echo "      source $VENV_DIR/bin/activate"
    echo
    echo "   2. Run the interactive setup:"
    echo "      python gotosocial_token_generator.py --instance https://your-instance.com --app-name \"My Bot\""
    echo
    echo "   3. Or use the automated setup:"
    echo "      python gotosocial_simple.py --instance https://your-instance.com --app-name \"My Bot\" --username your_user --password your_pass --output bot.json"
    echo
    echo "   4. Test your bot:"
    echo "      python example_bot.py --credentials bot.json --demo"
    echo
    echo "   5. When done, deactivate:"
    echo "      deactivate"
    echo
    echo "📖 See README.md for detailed usage instructions."
else
    echo "❌ Setup failed during testing. Please check the errors above."
    exit 1
fi