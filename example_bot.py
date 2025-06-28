#!/usr/bin/env python3
"""
Example GoToSocial Bot

This demonstrates how to use the simplified GoToSocial setup to create
a working bot that posts content.
"""

import sys
import time
import random
from datetime import datetime
from gotosocial_bot_helper import GoToSocialBot

# Sample content for the bot to post
SAMPLE_POSTS = [
    "🤖 Beep boop! I'm a GoToSocial bot created with the simplified setup tools!",
    "🌟 The fediverse is amazing! Thanks for following my automated posts.",
    "📡 Broadcasting from the decentralized social web...",
    "🔧 Built with Python and the GoToSocial API. Check out the setup tools!",
    "🌍 Connecting communities across the fediverse, one post at a time.",
    "⚡ Automated posting made simple with GoToSocial!",
    "🚀 Exploring the possibilities of decentralized social media.",
    "🎯 This bot was set up in just a few minutes using the simplified tools!"
]

MOTIVATIONAL_QUOTES = [
    "The best time to plant a tree was 20 years ago. The second best time is now. 🌱",
    "Your limitation—it's only your imagination. 💭",
    "Push yourself, because no one else is going to do it for you. 💪",
    "Great things never come from comfort zones. 🌟",
    "Dream it. Wish it. Do it. ✨",
    "Success doesn't just find you. You have to go out and get it. 🎯",
    "The harder you work for something, the greater you'll feel when you achieve it. 🏆",
    "Don't stop when you're tired. Stop when you're done. 🔥"
]

class ExampleBot:
    def __init__(self, credentials_file: str):
        """Initialize the bot with credentials."""
        try:
            self.bot = GoToSocialBot.from_credentials_file(credentials_file)
            self.account = self.bot.get_account_info()
            print(f"✓ Bot initialized as @{self.account['username']}")
        except Exception as e:
            print(f"❌ Failed to initialize bot: {e}")
            sys.exit(1)
    
    def post_random_content(self):
        """Post a random piece of content."""
        content = random.choice(SAMPLE_POSTS)
        try:
            status = self.bot.post_status(content)
            print(f"✓ Posted: {content[:50]}...")
            print(f"  URL: {status.get('url', 'N/A')}")
            return status
        except Exception as e:
            print(f"❌ Failed to post: {e}")
            return None
    
    def post_motivational_quote(self):
        """Post a motivational quote."""
        quote = random.choice(MOTIVATIONAL_QUOTES)
        content = f"💡 Daily Motivation:\n\n{quote}\n\n#motivation #inspiration #fediverse"
        
        try:
            status = self.bot.post_status(content)
            print(f"✓ Posted motivational quote")
            print(f"  URL: {status.get('url', 'N/A')}")
            return status
        except Exception as e:
            print(f"❌ Failed to post quote: {e}")
            return None
    
    def post_time_announcement(self):
        """Post the current time."""
        now = datetime.now()
        content = f"🕐 Time check: {now.strftime('%Y-%m-%d %H:%M:%S')}\n\nHave a great {now.strftime('%A')}! #timecheck #bot"
        
        try:
            status = self.bot.post_status(content)
            print(f"✓ Posted time announcement")
            print(f"  URL: {status.get('url', 'N/A')}")
            return status
        except Exception as e:
            print(f"❌ Failed to post time: {e}")
            return None
    
    def interact_with_timeline(self):
        """Look at the timeline and interact with posts."""
        try:
            timeline = self.bot.get_timeline("home", limit=5)
            print(f"📖 Found {len(timeline)} posts in timeline")
            
            for post in timeline:
                # Skip our own posts
                if post['account']['id'] == self.account['id']:
                    continue
                
                # Randomly favorite some posts (10% chance)
                if random.random() < 0.1:
                    try:
                        self.bot.favorite_status(post['id'])
                        print(f"⭐ Favorited post by @{post['account']['username']}")
                    except Exception as e:
                        print(f"❌ Failed to favorite: {e}")
                
                # Very rarely boost posts (2% chance)
                if random.random() < 0.02:
                    try:
                        self.bot.boost_status(post['id'])
                        print(f"🔄 Boosted post by @{post['account']['username']}")
                    except Exception as e:
                        print(f"❌ Failed to boost: {e}")
        
        except Exception as e:
            print(f"❌ Failed to interact with timeline: {e}")
    
    def check_notifications(self):
        """Check and respond to notifications."""
        try:
            notifications = self.bot.get_notifications(limit=5)
            print(f"🔔 Found {len(notifications)} notifications")
            
            for notification in notifications:
                if notification['type'] == 'mention':
                    print(f"💬 Mentioned by @{notification['account']['username']}")
                elif notification['type'] == 'follow':
                    print(f"👥 New follower: @{notification['account']['username']}")
                elif notification['type'] == 'favourite':
                    print(f"⭐ Post favorited by @{notification['account']['username']}")
                elif notification['type'] == 'reblog':
                    print(f"🔄 Post boosted by @{notification['account']['username']}")
        
        except Exception as e:
            print(f"❌ Failed to check notifications: {e}")
    
    def run_demo(self):
        """Run a demonstration of bot capabilities."""
        print(f"\n🤖 Running bot demo for @{self.account['username']}")
        print("=" * 50)
        
        # Post some content
        print("\n1. Posting random content...")
        self.post_random_content()
        
        time.sleep(2)
        
        print("\n2. Posting motivational quote...")
        self.post_motivational_quote()
        
        time.sleep(2)
        
        print("\n3. Posting time announcement...")
        self.post_time_announcement()
        
        time.sleep(2)
        
        print("\n4. Checking timeline and interacting...")
        self.interact_with_timeline()
        
        time.sleep(2)
        
        print("\n5. Checking notifications...")
        self.check_notifications()
        
        print("\n✅ Demo complete!")
        print(f"🔗 Visit your profile: {self.account.get('url', 'N/A')}")


def main():
    """Main function to run the example bot."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Example GoToSocial bot")
    parser.add_argument(
        "--credentials", 
        required=True,
        help="Path to credentials JSON file"
    )
    parser.add_argument(
        "--demo", 
        action="store_true",
        help="Run a full demonstration"
    )
    parser.add_argument(
        "--post-type",
        choices=["random", "quote", "time"],
        help="Post a specific type of content"
    )
    
    args = parser.parse_args()
    
    # Initialize bot
    bot = ExampleBot(args.credentials)
    
    if args.demo:
        bot.run_demo()
    elif args.post_type == "random":
        bot.post_random_content()
    elif args.post_type == "quote":
        bot.post_motivational_quote()
    elif args.post_type == "time":
        bot.post_time_announcement()
    else:
        print("🤖 Bot ready! Use --demo or --post-type to do something.")
        print(f"   Account: @{bot.account['username']}")
        print(f"   Instance: {bot.bot.instance_url}")


if __name__ == "__main__":
    main()