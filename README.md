# GoToSocial Bot Setup - Simplified

## 🤖 AI Disclosure

This project was created with the assistance of **Rovo Dev**, an AI agent powered by Claude 3.5 Sonnet, as part of the Atlassian Rovo platform. The initial prompt was:

> "gotosociall is a mastodon compatible fediverse server available from https://github.com/superseriousbusiness/gotosocial . As a developer who wants to launch a couple of fediverse bots, I need to create an appliation, do some nasty curl to finally get an ACCECSS_TOKEN that can be used with mastodon clients. Can you simplify this solution?"

The AI agent analyzed the problem of complex GoToSocial bot setup processes and created this comprehensive toolkit to automate and simplify the workflow. All code has been tested and follows Python best practices.

---

This repository provides simple Python tools to streamline the process of creating applications and getting access tokens for GoToSocial instances, making it much easier to set up fediverse bots.

## The Problem

Setting up a bot for GoToSocial typically involves:
1. Manual curl commands to create an application
2. Navigating OAuth flows in browsers
3. More curl commands to exchange codes for tokens
4. Manually managing credentials

This is tedious and error-prone, especially when setting up multiple bots.

## The Solution

Three Python scripts that automate the entire process, with proper virtual environment support.

### Quick Start

```bash
# Option 1: Automated setup with virtual environment (recommended)
./setup_venv.sh

# Option 2: Quick bot setup (creates venv automatically)
./setup_bot.sh

# Option 3: Manual setup
python3 -m venv gotosocial_bot_env
source gotosocial_bot_env/bin/activate
pip install -r requirements.txt

# Then use the tools:
python gotosocial_token_generator.py --instance https://your-instance.com --app-name "My Bot"
# or
python gotosocial_simple.py --instance https://your-instance.com --app-name "My Bot" --username your_username --password your_password --output bot_credentials.json
```

## Scripts Overview

### 1. `gotosocial_token_generator.py` - Interactive Setup

**Best for:** First-time setup, when you want to see each step

Features:
- Creates application automatically
- Opens authorization URL in your browser
- Guides you through the OAuth flow
- Verifies the token works
- Saves credentials to a JSON file

```bash
# Activate virtual environment first
source gotosocial_bot_env/bin/activate

python gotosocial_token_generator.py \
  --instance https://social.example.com \
  --app-name "Weather Bot" \
  --scopes "read write:statuses"
```

### 2. `gotosocial_simple.py` - Automated Setup

**Best for:** Automated deployments, when you control the account credentials

Features:
- One-command setup using username/password
- No browser interaction needed
- Perfect for CI/CD and automated deployments

```bash
# Activate virtual environment first
source gotosocial_bot_env/bin/activate

python gotosocial_simple.py \
  --instance https://social.example.com \
  --app-name "News Bot" \
  --username mybot \
  --password mypassword \
  --output news_bot_creds.json
```

### 3. `gotosocial_bot_helper.py` - Bot Operations

**Best for:** Actually using your bot after setup

Features:
- Simple API for common bot operations
- Post statuses, upload media, follow accounts
- Load credentials from saved files
- Mastodon API compatible

```python
from gotosocial_bot_helper import GoToSocialBot

# Load your saved credentials
bot = GoToSocialBot.from_credentials_file("bot_credentials.json")

# Post a status
bot.post_status("Hello fediverse! 🤖")

# Upload and post with media
media = bot.upload_media("photo.jpg", "A cool photo")
bot.post_status("Check this out!", media_ids=[media["id"]])
```

## Virtual Environment Setup

### Why Use Virtual Environments?

Virtual environments isolate your Python dependencies, preventing conflicts with other projects and system packages.

### Setup Commands

```bash
# Create virtual environment
python3 -m venv gotosocial_bot_env

# Activate it (Linux/Mac)
source gotosocial_bot_env/bin/activate

# Activate it (Windows)
gotosocial_bot_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# When done working
deactivate
```

### Automated Setup

Use the provided setup scripts for easier management:

```bash
# Full setup with testing
./setup_venv.sh

# Quick bot setup
./setup_bot.sh
```

## Complete Example: Setting Up a Weather Bot

```bash
# 1. Setup virtual environment
./setup_venv.sh

# 2. Activate environment
source gotosocial_bot_env/bin/activate

# 3. Generate credentials
python gotosocial_simple.py \
  --instance https://social.myserver.org \
  --app-name "Weather Bot" \
  --username weatherbot \
  --password supersecret123 \
  --output weather_bot.json

# 4. Create your bot script
cat > weather_bot.py << 'EOF'
#!/usr/bin/env python3
from gotosocial_bot_helper import GoToSocialBot
import requests

# Load credentials
bot = GoToSocialBot.from_credentials_file("weather_bot.json")

# Get weather data (example)
weather_data = requests.get("https://api.weather.gov/...").json()
weather_text = f"Today's weather: {weather_data['temperature']}°F, {weather_data['conditions']}"

# Post the weather
status = bot.post_status(weather_text)
print(f"Posted weather update: {status['url']}")
EOF

# 5. Run your bot
python weather_bot.py

# 6. When done
deactivate
```

## Environment Variables

You can also use environment variables instead of credential files:

```bash
# Activate virtual environment
source gotosocial_bot_env/bin/activate

export GOTOSOCIAL_INSTANCE="https://social.example.com"
export GOTOSOCIAL_TOKEN="your_access_token_here"

python -c "
from gotosocial_bot_helper import GoToSocialBot
import os
bot = GoToSocialBot(os.environ['GOTOSOCIAL_INSTANCE'], os.environ['GOTOSOCIAL_TOKEN'])
bot.post_status('Hello from environment variables!')
"
```

## Credential File Format

The generated credential files contain everything you need:

```json
{
  "instance_url": "https://social.example.com",
  "app_name": "My Bot",
  "access_token": "your_access_token_here",
  "client_id": "client_id_here",
  "client_secret": "client_secret_here",
  "account": {
    "username": "mybot",
    "display_name": "My Bot"
  }
}
```

## Available Scopes

Common OAuth scopes you might need:

- `read` - Read access to your account
- `write` - Write access (post, follow, etc.)
- `write:statuses` - Only post statuses
- `write:follows` - Only follow/unfollow
- `write:media` - Only upload media
- `push` - Push notifications

Example: `--scopes "read write:statuses write:media"`

## Bot Helper API Reference

### Basic Operations

```python
# Always activate virtual environment first
# source gotosocial_bot_env/bin/activate

from gotosocial_bot_helper import GoToSocialBot

bot = GoToSocialBot.from_credentials_file("creds.json")

# Account info
account = bot.get_account_info()

# Post status
status = bot.post_status("Hello world!")
status = bot.post_status("Private message", visibility="private")
status = bot.post_status("Content warning", spoiler_text="Spoiler alert!")

# Media upload
media = bot.upload_media("image.jpg", "Alt text description")
bot.post_status("Photo post!", media_ids=[media["id"]])

# Timeline
posts = bot.get_timeline("home", limit=10)
posts = bot.get_timeline("local", limit=20)
posts = bot.get_timeline("public", limit=5)

# Interactions
bot.favorite_status("status_id_here")
bot.boost_status("status_id_here")
bot.follow_account("account_id_here")

# Search
accounts = bot.search_accounts("@username@instance.com")

# Notifications
notifications = bot.get_notifications(limit=10)
```

## Testing Your Setup

```bash
# Activate virtual environment
source gotosocial_bot_env/bin/activate

# Run the test suite
python test_setup.py

# Test your credentials
python -c "
from gotosocial_bot_helper import GoToSocialBot
bot = GoToSocialBot.from_credentials_file('your_creds.json')
print('Account:', bot.get_account_info()['username'])
print('Test post:', bot.post_status('Test from Python!')['url'])
"

# Run the example bot
python example_bot.py --credentials your_creds.json --demo
```

## Error Handling

All scripts include proper error handling:

```python
try:
    bot = GoToSocialBot.from_credentials_file("creds.json")
    bot.post_status("Hello!")
except FileNotFoundError:
    print("Credentials file not found!")
except requests.exceptions.HTTPError as e:
    print(f"API error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Troubleshooting

### Common Issues

1. **"Application creation failed"**
   - Check your instance URL (include https://)
   - Verify the instance is running and accessible
   - Some instances may have application creation disabled

2. **"Token verification failed"**
   - Check your username/password are correct
   - Verify your account has the necessary permissions
   - Some instances may not support password grants

3. **"Permission denied"**
   - Check your OAuth scopes
   - Verify your account has the required permissions
   - Some operations may require admin approval

4. **"Module not found"**
   - Make sure you activated the virtual environment: `source gotosocial_bot_env/bin/activate`
   - Install dependencies: `pip install -r requirements.txt`

### Virtual Environment Issues

```bash
# If virtual environment is corrupted, recreate it
rm -rf gotosocial_bot_env
python3 -m venv gotosocial_bot_env
source gotosocial_bot_env/bin/activate
pip install -r requirements.txt
```

## Project Structure

```
gotosocial-bot-tools/
├── gotosocial_token_generator.py  # Interactive token generation
├── gotosocial_simple.py           # Automated token generation
├── gotosocial_bot_helper.py       # Bot operations library
├── example_bot.py                 # Example bot implementation
├── test_setup.py                  # Test suite
├── setup_venv.sh                  # Virtual environment setup
├── setup_bot.sh                   # Quick bot setup
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Security Notes

- Keep your credential files secure and never commit them to version control
- Use environment variables in production
- Consider using dedicated bot accounts rather than your personal account
- Regularly rotate your access tokens if possible
- Always use virtual environments to isolate dependencies

## Dependencies

- `requests>=2.25.0` - HTTP library for API calls
- Python 3.7+ with venv support

```bash
# Install in virtual environment
source gotosocial_bot_env/bin/activate
pip install -r requirements.txt
```

## License

This code is provided as-is for educational and practical use. Feel free to modify and distribute as needed.

---

**Happy botting! 🤖**

Remember to always activate your virtual environment before working with the tools:
```bash
source gotosocial_bot_env/bin/activate
```