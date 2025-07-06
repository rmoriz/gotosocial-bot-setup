#!/usr/bin/env python3
"""
GoToSocial Interactive Token Generator

Uses the authorization code flow which is supported by GoToSocial.
This requires manual authorization through the browser.
"""

import requests
import json
import sys
import urllib.parse
from typing import Dict, Optional

class GoToSocialInteractiveAuth:
    def __init__(self, instance_url: str):
        self.instance_url = instance_url.rstrip('/')
        self.session = requests.Session()
    
    def create_app_and_get_token(self, 
                                app_name: str, 
                                scopes: str = "read write") -> Dict:
        """
        Create an app and get an access token using the authorization code flow.
        This requires manual user authorization through the browser.
        """
        
        # Step 1: Create application
        print(f"Creating application '{app_name}'...")
        app_data = self._create_application(app_name, scopes)
        
        # Step 2: Generate authorization URL
        print("Generating authorization URL...")
        auth_url = self._get_authorization_url(app_data["client_id"], scopes)
        
        print(f"\nPlease open this URL in your browser and authorize the application:")
        print(f"{auth_url}")
        print(f"\nAfter authorization, you'll get an authorization code.")
        
        # Step 3: Get authorization code from user
        auth_code = input("Please enter the authorization code: ").strip()
        
        # Step 4: Exchange code for token
        print("Exchanging authorization code for access token...")
        token_data = self._get_token_authorization_code(
            app_data["client_id"],
            app_data["client_secret"],
            auth_code
        )
        
        # Step 5: Verify token
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
        
        print("Success! Token generated and verified.")
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
    
    def _get_authorization_url(self, client_id: str, scopes: str) -> str:
        """Generate authorization URL for manual authorization."""
        params = {
            "client_id": client_id,
            "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
            "response_type": "code",
            "scope": scopes
        }
        
        query_string = urllib.parse.urlencode(params)
        return f"{self.instance_url}/oauth/authorize?{query_string}"
    
    def _get_token_authorization_code(self, 
                                    client_id: str, 
                                    client_secret: str,
                                    auth_code: str) -> Dict:
        """Get access token using authorization code grant."""
        url = f"{self.instance_url}/oauth/token"
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "authorization_code",
            "code": auth_code,
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
        print(f"Credentials saved to: {filename}")


def quick_setup(instance_url: str, 
               app_name: str, 
               output_file: Optional[str] = None) -> Dict:
    """
    Quick setup function for getting a GoToSocial token using authorization code flow.
    
    Args:
        instance_url: Your GoToSocial instance URL
        app_name: Name for your bot application
        output_file: Optional file to save credentials
    
    Returns:
        Dictionary with access token and other credentials
    """
    
    auth = GoToSocialInteractiveAuth(instance_url)
    credentials = auth.create_app_and_get_token(app_name)
    
    if output_file:
        auth.save_credentials(credentials, output_file)
    
    return credentials


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="GoToSocial interactive token generator")
    parser.add_argument("--instance", required=True, help="GoToSocial instance URL")
    parser.add_argument("--app-name", required=True, help="Application name")
    parser.add_argument("--output", help="Output file for credentials")
    parser.add_argument("--scopes", default="read write", help="OAuth scopes")
    
    args = parser.parse_args()
    
    try:
        auth = GoToSocialInteractiveAuth(args.instance)
        credentials = auth.create_app_and_get_token(args.app_name, args.scopes)
        
        if args.output:
            auth.save_credentials(credentials, args.output)
        
        print(f"\nYour access token: {credentials['access_token']}")
        print(f"Account: @{credentials['account']['username']}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)