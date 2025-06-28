#!/usr/bin/env python3
"""
GoToSocial Bot Helper

A utility class to make it easy to work with GoToSocial/Mastodon APIs
after you have an access token.
"""

import requests
import json
import mimetypes
from typing import Dict, List, Optional, Union
from pathlib import Path

class GoToSocialBot:
    def __init__(self, instance_url: str, access_token: str):
        self.instance_url = instance_url.rstrip('/')
        self.access_token = access_token
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {access_token}",
            "User-Agent": "GoToSocial-Bot-Helper/1.0"
        })
    
    @classmethod
    def from_credentials_file(cls, credentials_file: str):
        """Create a bot instance from a saved credentials file."""
        with open(credentials_file, 'r') as f:
            creds = json.load(f)
        return cls(creds["instance_url"], creds["access_token"])
    
    def post_status(self, 
                   content: str,
                   visibility: str = "public",
                   sensitive: bool = False,
                   spoiler_text: str = "",
                   in_reply_to_id: Optional[str] = None,
                   media_ids: Optional[List[str]] = None) -> Dict:
        """
        Post a new status (toot).
        
        Args:
            content: The text content of the status
            visibility: "public", "unlisted", "private", or "direct"
            sensitive: Mark as sensitive content
            spoiler_text: Content warning text
            in_reply_to_id: ID of status to reply to
            media_ids: List of media attachment IDs
        
        Returns:
            The created status object
        """
        url = f"{self.instance_url}/api/v1/statuses"
        data = {
            "status": content,
            "visibility": visibility,
            "sensitive": sensitive
        }
        
        if spoiler_text:
            data["spoiler_text"] = spoiler_text
        if in_reply_to_id:
            data["in_reply_to_id"] = in_reply_to_id
        if media_ids:
            data["media_ids"] = media_ids
        
        response = self.session.post(url, data=data)
        response.raise_for_status()
        return response.json()
    
    def upload_media(self, file_path: Union[str, Path], description: str = "") -> Dict:
        """
        Upload a media file.
        
        Args:
            file_path: Path to the media file
            description: Alt text description for accessibility
        
        Returns:
            Media attachment object with ID
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        url = f"{self.instance_url}/api/v1/media"
        
        # Determine MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if not mime_type:
            mime_type = "application/octet-stream"
        
        files = {
            "file": (file_path.name, open(file_path, "rb"), mime_type)
        }
        data = {}
        if description:
            data["description"] = description
        
        try:
            response = self.session.post(url, files=files, data=data)
            response.raise_for_status()
            return response.json()
        finally:
            files["file"][1].close()
    
    def get_account_info(self) -> Dict:
        """Get information about the authenticated account."""
        url = f"{self.instance_url}/api/v1/accounts/verify_credentials"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_timeline(self, timeline_type: str = "home", limit: int = 20) -> List[Dict]:
        """
        Get timeline posts.
        
        Args:
            timeline_type: "home", "local", "public", or "tag/hashtag"
            limit: Number of posts to retrieve (max 40)
        
        Returns:
            List of status objects
        """
        url = f"{self.instance_url}/api/v1/timelines/{timeline_type}"
        params = {"limit": min(limit, 40)}
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def follow_account(self, account_id: str) -> Dict:
        """Follow an account by ID."""
        url = f"{self.instance_url}/api/v1/accounts/{account_id}/follow"
        response = self.session.post(url)
        response.raise_for_status()
        return response.json()
    
    def search_accounts(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for accounts."""
        url = f"{self.instance_url}/api/v2/search"
        params = {
            "q": query,
            "type": "accounts",
            "limit": limit
        }
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json().get("accounts", [])
    
    def favorite_status(self, status_id: str) -> Dict:
        """Favorite (like) a status."""
        url = f"{self.instance_url}/api/v1/statuses/{status_id}/favourite"
        response = self.session.post(url)
        response.raise_for_status()
        return response.json()
    
    def boost_status(self, status_id: str) -> Dict:
        """Boost (reblog) a status."""
        url = f"{self.instance_url}/api/v1/statuses/{status_id}/reblog"
        response = self.session.post(url)
        response.raise_for_status()
        return response.json()
    
    def delete_status(self, status_id: str) -> Dict:
        """Delete a status."""
        url = f"{self.instance_url}/api/v1/statuses/{status_id}"
        response = self.session.delete(url)
        response.raise_for_status()
        return response.json()
    
    def get_notifications(self, limit: int = 15) -> List[Dict]:
        """Get notifications."""
        url = f"{self.instance_url}/api/v1/notifications"
        params = {"limit": min(limit, 30)}
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()


# Example usage functions
def simple_bot_example():
    """Example of how to use the bot helper."""
    
    # Load credentials from file
    bot = GoToSocialBot.from_credentials_file("my_bot_credentials.json")
    
    # Or create directly with token
    # bot = GoToSocialBot("https://social.example.com", "your_access_token_here")
    
    # Get account info
    account = bot.get_account_info()
    print(f"Logged in as: @{account['username']}")
    
    # Post a simple status
    status = bot.post_status("Hello from my GoToSocial bot! 🤖")
    print(f"Posted status: {status['url']}")
    
    # Post with media
    # media = bot.upload_media("image.jpg", "A beautiful sunset")
    # status = bot.post_status("Check out this sunset!", media_ids=[media["id"]])
    
    # Get home timeline
    timeline = bot.get_timeline("home", limit=5)
    print(f"Found {len(timeline)} posts in home timeline")


if __name__ == "__main__":
    # Run the example
    simple_bot_example()