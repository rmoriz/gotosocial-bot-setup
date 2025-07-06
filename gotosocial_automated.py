#!/usr/bin/env python3
"""
Automated GoToSocial Token Generator

This script automates the OAuth flow by programmatically handling the authorization
without requiring manual browser interaction. It uses provided credentials to
automatically authorize the application.
"""

import argparse
import json
import requests
import sys
from urllib.parse import urlencode, parse_qs, urlparse
import re

class AutomatedGoToSocialAuth:
    def __init__(self, instance_url, app_name, scopes="read write"):
        self.instance_url = instance_url.rstrip('/')
        self.app_name = app_name
        self.scopes = scopes
        self.client_id = None
        self.client_secret = None
        self.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
        self.session = requests.Session()
        
    def create_application(self):
        """Create a new application on the GoToSocial instance."""
        print(f"Creating application '{self.app_name}' on {self.instance_url}...")
        
        url = f"{self.instance_url}/api/v1/apps"
        data = {
            "client_name": self.app_name,
            "redirect_uris": self.redirect_uri,
            "scopes": self.scopes,
            "website": ""
        }
        
        try:
            response = self.session.post(url, data=data)
            response.raise_for_status()
            
            app_data = response.json()
            self.client_id = app_data["client_id"]
            self.client_secret = app_data["client_secret"]
            
            print("✓ Application created successfully!")
            return app_data
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Failed to create application: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"  Response: {e.response.text}")
            sys.exit(1)
    
    def automated_authorize(self, username, password):
        """
        Automatically handle the OAuth authorization flow by simulating
        the browser interaction programmatically.
        """
        print("Starting automated authorization...")
        
        # Step 1: Get the authorization page
        auth_url = self.get_authorization_url()
        print(f"Getting authorization page: {auth_url}")
        
        try:
            # Get the authorization page
            response = self.session.get(auth_url)
            response.raise_for_status()
            
            # Check if we're already logged in or need to login
            if "Sign in" in response.text or "login" in response.text.lower():
                print("Need to log in first...")
                auth_code = self._handle_login_and_authorize(response, username, password)
            else:
                print("Already logged in, proceeding with authorization...")
                auth_code = self._extract_or_authorize(response)
            
            return auth_code
            
        except Exception as e:
            print(f"✗ Automated authorization failed: {e}")
            return None
    
    def _handle_login_and_authorize(self, auth_response, username, password):
        """Handle login and then authorization."""
        
        # Look for login form
        login_url = f"{self.instance_url}/auth/sign_in"
        
        print(f"Attempting to log in at: {login_url}")
        
        # Get login page
        login_response = self.session.get(login_url)
        login_response.raise_for_status()
        
        # Extract CSRF token or other form data
        csrf_token = self._extract_csrf_token(login_response.text)
        
        # Prepare login data
        login_data = {
            "username": username,
            "password": password
        }
        
        if csrf_token:
            login_data["authenticity_token"] = csrf_token
        
        # Submit login
        login_submit_response = self.session.post(login_url, data=login_data, allow_redirects=True)
        
        if login_submit_response.status_code == 200 and "Sign in" not in login_submit_response.text:
            print("✓ Login successful!")
            
            # Now try the authorization again
            auth_url = self.get_authorization_url()
            auth_response = self.session.get(auth_url)
            auth_response.raise_for_status()
            
            return self._extract_or_authorize(auth_response)
        else:
            print("✗ Login failed!")
            print(f"Response status: {login_submit_response.status_code}")
            return None
    
    def _extract_csrf_token(self, html_content):
        """Extract CSRF token from HTML."""
        # Look for CSRF token in various forms
        patterns = [
            r'name="authenticity_token"[^>]*value="([^"]*)"',
            r'name="csrf_token"[^>]*value="([^"]*)"',
            r'name="_token"[^>]*value="([^"]*)"',
            r'<meta name="csrf-token" content="([^"]*)"'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html_content)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_or_authorize(self, auth_response):
        """Extract authorization code or submit authorization form."""
        
        # Check if there's already an authorization code in the response
        if "authorization_code" in auth_response.text or "code=" in auth_response.text:
            # Try to extract the code directly
            code_match = re.search(r'code=([^&\s"]+)', auth_response.text)
            if code_match:
                return code_match.group(1)
        
        # Look for authorization form to submit
        if "authorize" in auth_response.text.lower() or "allow" in auth_response.text.lower():
            print("Found authorization form, submitting...")
            
            # Extract form data
            csrf_token = self._extract_csrf_token(auth_response.text)
            
            # Submit authorization
            auth_data = {
                "client_id": self.client_id,
                "redirect_uri": self.redirect_uri,
                "response_type": "code",
                "scope": self.scopes
            }
            
            if csrf_token:
                auth_data["authenticity_token"] = csrf_token
            
            # Submit the authorization
            auth_submit_url = f"{self.instance_url}/oauth/authorize"
            auth_submit_response = self.session.post(auth_submit_url, data=auth_data, allow_redirects=False)
            
            # Check for redirect with code
            if auth_submit_response.status_code in [302, 303]:
                location = auth_submit_response.headers.get('Location', '')
                if 'code=' in location:
                    parsed = urlparse(location)
                    query_params = parse_qs(parsed.query)
                    if 'code' in query_params:
                        return query_params['code'][0]
            
            # Check response text for code
            if 'code=' in auth_submit_response.text:
                code_match = re.search(r'code=([^&\s"]+)', auth_submit_response.text)
                if code_match:
                    return code_match.group(1)
        
        print("✗ Could not extract authorization code")
        return None
    
    def get_authorization_url(self):
        """Generate the authorization URL."""
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
            response = self.session.post(url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
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
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            
            account_data = response.json()
            print("✓ Token verification successful!")
            print(f"  Account: @{account_data.get('username', 'unknown')}")
            print(f"  Display Name: {account_data.get('display_name', 'N/A')}")
            
            return account_data
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Token verification failed: {e}")
            return None
    
    def save_credentials(self, app_data, token_data, account_data, filename):
        """Save the credentials to a JSON file."""
        credentials = {
            "instance_url": self.instance_url,
            "app_name": self.app_name,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "access_token": token_data["access_token"],
            "token_type": token_data.get("token_type", "Bearer"),
            "scope": token_data.get("scope", self.scopes),
            "created_at": token_data.get("created_at"),
            "account": account_data,
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

def automated_setup(instance_url, app_name, username, password, output_file=None):
    """
    Automated setup function for getting a GoToSocial token without browser interaction.
    """
    
    auth = AutomatedGoToSocialAuth(instance_url, app_name)
    
    # Step 1: Create application
    app_data = auth.create_application()
    
    # Step 2: Automated authorization
    auth_code = auth.automated_authorize(username, password)
    
    if not auth_code:
        print("✗ Failed to get authorization code")
        sys.exit(1)
    
    print(f"✓ Got authorization code: {auth_code[:10]}...")
    
    # Step 3: Get access token
    token_data = auth.get_access_token(auth_code)
    
    # Step 4: Verify token
    account_data = auth.verify_token(token_data["access_token"])
    
    # Step 5: Save credentials
    if output_file:
        auth.save_credentials(app_data, token_data, account_data, output_file)
    
    result = {
        "instance_url": instance_url,
        "app_name": app_name,
        "access_token": token_data["access_token"],
        "client_id": auth.client_id,
        "client_secret": auth.client_secret,
        "account": account_data,
        "app_data": app_data,
        "token_data": token_data
    }
    
    print(f"\n🎉 SUCCESS! Your access token: {token_data['access_token']}")
    print(f"Account: @{account_data['username']}")
    
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated GoToSocial token generator")
    parser.add_argument("--instance", required=True, help="GoToSocial instance URL")
    parser.add_argument("--app-name", required=True, help="Application name")
    parser.add_argument("--username", required=True, help="Your username/email")
    parser.add_argument("--password", required=True, help="Your password")
    parser.add_argument("--output", help="Output file for credentials")
    parser.add_argument("--scopes", default="read write", help="OAuth scopes")
    
    args = parser.parse_args()
    
    try:
        result = automated_setup(
            args.instance,
            args.app_name,
            args.username,
            args.password,
            args.output
        )
        
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)