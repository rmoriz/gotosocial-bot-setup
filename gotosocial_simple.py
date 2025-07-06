#!/usr/bin/env python3
"""
Simple GoToSocial Token Generator

A streamlined version for automated token generation when you already have
user credentials or want to use password-based authentication.
"""

import requests
import json
import sys
from typing import Dict, Optional

class SimpleGoToSocialAuth:
    def __init__(self, instance_url: str):
        self.instance_url = instance_url.rstrip('/')
        self.session = requests.Session()
    
    def create_app_and_get_token(self, 
                                app_name: str, 
                                username: str, 
                                password: str,
                                scopes: str = "read write") -> Dict:
        """
        Create an app and get an access token in one go using username/password.
        This is useful for bot accounts where you control the credentials.
        """
        
        # Step 1: Create application
        print(f"Creating application '{app_name}'...")
        app_data = self._create_application(app_name, scopes)
        
        # Step 2: Get token using password grant (if supported)
        print("Getting access token...")
        token_data = self._get_token_password_grant(
            app_data["client_id"],
            app_data["client_secret"],
            username,
            password,
            scopes
        )
        
        # Step 3: Verify token
        print("Verifying token...")
        account_data = self._verify_token(token_data["access_token"])
        
        result = {
            "instance_url": self.instance_url,
            "app_name": app_name,
            "access_token": token_data["access_token"],
            "client_id": app_data["client_id"],
            "client_secret": app_data["client_secret"],
            "account": account_data,
            "app_data": app_data,
            "token_data": token_data
        }
        
        print("✓ Success! Token generated and verified.")
        return result
    
    def _create_application(self, app_name: str, scopes: str) -> Dict:
        """Create a new application."""
        url = f"{self.instance_url}/api/v1/apps"
        data = {
            "client_name": app_name,
            "redirect_uris": "urn:ietf:wg:oauth:2.0:oob",
            "scopes": scopes
        }
        
        response = self.session.post(url, data=data)
        response.raise_for_status()
        return response.json()
    
    def _get_token_password_grant(self, 
                                 client_id: str, 
                                 client_secret: str,
                                 username: str, 
                                 password: str, 
                                 scopes: str) -> Dict:
        """Get access token using password grant."""
        url = f"{self.instance_url}/oauth/token"
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "password",
            "username": username,
            "password": password,
            "scope": scopes,
            "redirect_uri": "urn:ietf:wg:oauth:2.0:oob"
        }
        
        response = self.session.post(url, data=data)
        response.raise_for_status()
        return response.json()
    
    def _verify_token(self, access_token: str) -> Dict:
        """Verify the access token."""
        url = f"{self.instance_url}/api/v1/accounts/verify_credentials"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        response = self.session.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    
    def save_credentials(self, credentials: Dict, filename: str) -> None:
        """Save credentials to a JSON file."""
        with open(filename, 'w') as f:
            json.dump(credentials, f, indent=2)
        print(f"✓ Credentials saved to: {filename}")


def quick_setup(instance_url: str, 
               app_name: str, 
               username: str, 
               password: str,
               output_file: Optional[str] = None) -> Dict:
    """
    Quick setup function for getting a GoToSocial token.
    
    Args:
        instance_url: Your GoToSocial instance URL
        app_name: Name for your bot application
        username: Your account username
        password: Your account password
        output_file: Optional file to save credentials
    
    Returns:
        Dictionary with access token and other credentials
    """
    
    auth = SimpleGoToSocialAuth(instance_url)
    credentials = auth.create_app_and_get_token(app_name, username, password)
    
    if output_file:
        auth.save_credentials(credentials, output_file)
    
    return credentials


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple GoToSocial token generator")
    parser.add_argument("--instance", required=True, help="GoToSocial instance URL")
    parser.add_argument("--app-name", required=True, help="Application name")
    parser.add_argument("--username", required=True, help="Your username")
    parser.add_argument("--password", required=True, help="Your password")
    parser.add_argument("--output", help="Output file for credentials")
    parser.add_argument("--scopes", default="read write", help="OAuth scopes")
    
    args = parser.parse_args()
    
    try:
        credentials = quick_setup(
            args.instance,
            args.app_name,
            args.username,
            args.password,
            args.output
        )
        
        print(f"\n🎉 Your access token: {credentials['access_token']}")
        print(f"Account: @{credentials['account']['username']}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)