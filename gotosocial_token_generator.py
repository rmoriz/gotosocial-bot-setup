#!/usr/bin/env python3
"""
GoToSocial Token Generator

A simple script to automate the creation of applications and generation of access tokens
for GoToSocial instances, making it easy to set up bots for the fediverse.

Usage:
    python gotosocial_token_generator.py --instance https://your-instance.com --app-name "My Bot"
"""

import argparse
import json
import requests
import sys
import webbrowser
from urllib.parse import urlencode, parse_qs, urlparse
import time

class GoToSocialTokenGenerator:
    def __init__(self, instance_url, app_name, scopes="read write"):
        self.instance_url = instance_url.rstrip('/')
        self.app_name = app_name
        self.scopes = scopes
        self.client_id = None
        self.client_secret = None
        self.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"  # Out-of-band for manual auth
        
    def create_application(self):
        """Create a new application on the GoToSocial instance."""
        print(f"Creating application '{self.app_name}' on {self.instance_url}...")
        
        url = f"{self.instance_url}/api/v1/apps"
        data = {
            "client_name": self.app_name,
            "redirect_uris": self.redirect_uri,
            "scopes": self.scopes,
            "website": ""  # Optional
        }
        
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            app_data = response.json()
            self.client_id = app_data["client_id"]
            self.client_secret = app_data["client_secret"]
            
            print("✓ Application created successfully!")
            print(f"  Client ID: {self.client_id}")
            print(f"  Client Secret: {self.client_secret[:20]}...")
            
            return app_data
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Failed to create application: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"  Response: {e.response.text}")
            sys.exit(1)
    
    def get_authorization_url(self):
        """Generate the authorization URL for the user to visit."""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": self.scopes
        }
        
        auth_url = f"{self.instance_url}/oauth/authorize?" + urlencode(params)
        return auth_url
    
    def get_access_token(self, authorization_code):
        """Exchange the authorization code for an access token."""
        print("Exchanging authorization code for access token...")
        
        url = f"{self.instance_url}/oauth/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
            "code": authorization_code,
            "scope": self.scopes
        }
        
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            access_token = token_data["access_token"]
            
            print("✓ Access token generated successfully!")
            return token_data
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Failed to get access token: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"  Response: {e.response.text}")
            sys.exit(1)
    
    def verify_token(self, access_token):
        """Verify the access token by making a test API call."""
        print("Verifying access token...")
        
        url = f"{self.instance_url}/api/v1/accounts/verify_credentials"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            account_data = response.json()
            print("✓ Token verification successful!")
            print(f"  Account: @{account_data.get('username', 'unknown')}")
            print(f"  Display Name: {account_data.get('display_name', 'N/A')}")
            
            return account_data
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Token verification failed: {e}")
            return None
    
    def save_credentials(self, app_data, token_data, filename=None):
        """Save the application and token data to a JSON file."""
        if filename is None:
            # Create a safe filename based on instance and app name
            safe_instance = self.instance_url.replace('https://', '').replace('http://', '').replace('/', '_')
            safe_app_name = "".join(c for c in self.app_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"gotosocial_credentials_{safe_instance}_{safe_app_name.replace(' ', '_')}.json"
        
        credentials = {
            "instance_url": self.instance_url,
            "app_name": self.app_name,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "access_token": token_data["access_token"],
            "token_type": token_data.get("token_type", "Bearer"),
            "scope": token_data.get("scope", self.scopes),
            "created_at": token_data.get("created_at"),
            "app_data": app_data,
            "token_data": token_data
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(credentials, f, indent=2)
            print(f"✓ Credentials saved to: {filename}")
            return filename
        except Exception as e:
            print(f"✗ Failed to save credentials: {e}")
            return None
    
    def generate_token_interactive(self):
        """Run the complete token generation process interactively."""
        print(f"\n🤖 GoToSocial Token Generator")
        print(f"Instance: {self.instance_url}")
        print(f"App Name: {self.app_name}")
        print(f"Scopes: {self.scopes}")
        print("-" * 50)
        
        # Step 1: Create application
        app_data = self.create_application()
        
        # Step 2: Get authorization URL
        auth_url = self.get_authorization_url()
        print(f"\n📋 Please visit this URL to authorize the application:")
        print(f"   {auth_url}")
        
        # Try to open the URL automatically
        try:
            print("\n🌐 Attempting to open the URL in your default browser...")
            webbrowser.open(auth_url)
            time.sleep(2)
        except Exception:
            print("   (Could not open browser automatically)")
        
        # Step 3: Get authorization code from user
        print(f"\n🔑 After authorizing, you'll receive an authorization code.")
        auth_code = input("   Please enter the authorization code: ").strip()
        
        if not auth_code:
            print("✗ No authorization code provided. Exiting.")
            sys.exit(1)
        
        # Step 4: Exchange code for token
        token_data = self.get_access_token(auth_code)
        
        # Step 5: Verify token
        account_data = self.verify_token(token_data["access_token"])
        
        # Step 6: Save credentials
        credentials_file = self.save_credentials(app_data, token_data)
        
        # Step 7: Display results
        print(f"\n🎉 SUCCESS! Your GoToSocial bot is ready!")
        print(f"   Access Token: {token_data['access_token'][:20]}...")
        print(f"   Credentials File: {credentials_file}")
        print(f"\n💡 Usage example:")
        print(f"   export GOTOSOCIAL_TOKEN='{token_data['access_token']}'")
        print(f"   export GOTOSOCIAL_INSTANCE='{self.instance_url}'")
        
        return {
            "access_token": token_data["access_token"],
            "instance_url": self.instance_url,
            "credentials_file": credentials_file,
            "app_data": app_data,
            "token_data": token_data,
            "account_data": account_data
        }


def main():
    parser = argparse.ArgumentParser(
        description="Generate access tokens for GoToSocial instances",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python gotosocial_token_generator.py --instance https://social.example.com --app-name "My Weather Bot"
  python gotosocial_token_generator.py --instance https://gts.myserver.org --app-name "News Bot" --scopes "read write:statuses"
        """
    )
    
    parser.add_argument(
        "--instance", 
        required=True,
        help="GoToSocial instance URL (e.g., https://social.example.com)"
    )
    
    parser.add_argument(
        "--app-name",
        required=True,
        help="Name for your application/bot"
    )
    
    parser.add_argument(
        "--scopes",
        default="read write",
        help="OAuth scopes (default: 'read write')"
    )
    
    parser.add_argument(
        "--output",
        help="Output file for credentials (default: auto-generated)"
    )
    
    args = parser.parse_args()
    
    # Validate instance URL
    if not args.instance.startswith(('http://', 'https://')):
        print("✗ Instance URL must start with http:// or https://")
        sys.exit(1)
    
    try:
        generator = GoToSocialTokenGenerator(args.instance, args.app_name, args.scopes)
        result = generator.generate_token_interactive()
        
        if args.output:
            generator.save_credentials(
                result["app_data"], 
                result["token_data"], 
                args.output
            )
        
    except KeyboardInterrupt:
        print("\n\n✗ Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()