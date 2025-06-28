#!/bin/bash
# Quick setup script for GoToSocial bots

set -e

echo "🤖 GoToSocial Bot Quick Setup"
echo "=============================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if virtual environment exists
VENV_DIR="gotosocial_bot_env"
if [ ! -d "$VENV_DIR" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Get user input
read -p "🌐 GoToSocial instance URL (e.g., https://social.example.com): " INSTANCE_URL
read -p "🏷️  Bot application name: " APP_NAME
read -p "👤 Bot username: " USERNAME
read -s -p "🔒 Bot password: " PASSWORD
echo

# Validate inputs
if [[ -z "$INSTANCE_URL" || -z "$APP_NAME" || -z "$USERNAME" || -z "$PASSWORD" ]]; then
    echo "❌ All fields are required."
    exit 1
fi

# Generate safe filename
SAFE_INSTANCE=$(echo "$INSTANCE_URL" | sed 's|https\?://||' | sed 's|/|_|g')
SAFE_APP_NAME=$(echo "$APP_NAME" | sed 's/[^a-zA-Z0-9_-]/_/g')
CREDS_FILE="gotosocial_${SAFE_INSTANCE}_${SAFE_APP_NAME}.json"

echo "🔧 Setting up bot..."

# Run the simple token generator
python gotosocial_simple.py \
    --instance "$INSTANCE_URL" \
    --app-name "$APP_NAME" \
    --username "$USERNAME" \
    --password "$PASSWORD" \
    --output "$CREDS_FILE"

if [[ $? -eq 0 ]]; then
    echo
    echo "🎉 Success! Your bot is ready!"
    echo "📁 Credentials saved to: $CREDS_FILE"
    echo
    echo "💡 Quick test (remember to activate venv first):"
    echo "source $VENV_DIR/bin/activate"
    echo "python -c \"from gotosocial_bot_helper import GoToSocialBot; bot = GoToSocialBot.from_credentials_file('$CREDS_FILE'); print('✓ Bot ready:', bot.get_account_info()['username'])\""
    echo
    echo "🤖 Run example bot:"
    echo "python example_bot.py --credentials '$CREDS_FILE' --demo"
    echo
    echo "📖 See README.md for more examples and usage instructions."
    echo "💡 Don't forget to 'deactivate' when done!"
else
    echo "❌ Setup failed. Please check your credentials and try again."
    exit 1
fi