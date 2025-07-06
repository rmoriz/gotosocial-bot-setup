#!/usr/bin/env python3
"""
Test script to verify the GoToSocial setup tools work correctly.
"""

import sys
import json
import tempfile
import os
from unittest.mock import Mock, patch
import requests

def test_imports():
    """Test that all modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        import gotosocial_token_generator
        print("  ✓ gotosocial_token_generator")
    except ImportError as e:
        print(f"  ❌ gotosocial_token_generator: {e}")
        return False
    
    
    try:
        from gotosocial_bot_helper import GoToSocialBot
        print("  ✓ gotosocial_bot_helper")
    except ImportError as e:
        print(f"  ❌ gotosocial_bot_helper: {e}")
        return False
    
    return True

def test_credential_file_handling():
    """Test credential file creation and loading."""
    print("\n🧪 Testing credential file handling...")
    
    from gotosocial_bot_helper import GoToSocialBot
    
    # Create a test credentials file
    test_creds = {
        "instance_url": "https://test.example.com",
        "access_token": "test_token_123",
        "app_name": "Test Bot",
        "client_id": "test_client_id",
        "client_secret": "test_client_secret"
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_creds, f)
        temp_file = f.name
    
    try:
        # Test loading credentials
        bot = GoToSocialBot.from_credentials_file(temp_file)
        
        if bot.instance_url == "https://test.example.com":
            print("  ✓ Credential file loading")
        else:
            print("  ❌ Credential file loading - wrong instance URL")
            return False
        
        if bot.access_token == "test_token_123":
            print("  ✓ Access token loading")
        else:
            print("  ❌ Access token loading - wrong token")
            return False
        
    except Exception as e:
        print(f"  ❌ Credential file handling: {e}")
        return False
    finally:
        os.unlink(temp_file)
    
    return True

def test_api_request_formatting():
    """Test that API requests are formatted correctly."""
    print("\n🧪 Testing API request formatting...")
    
    from gotosocial_bot_helper import GoToSocialBot
    
    bot = GoToSocialBot("https://test.example.com", "test_token")
    
    # Check headers are set correctly
    expected_auth = "Bearer test_token"
    if bot.session.headers.get("Authorization") == expected_auth:
        print("  ✓ Authorization header")
    else:
        print(f"  ❌ Authorization header: {bot.session.headers.get('Authorization')}")
        return False
    
    # Check instance URL is cleaned
    if bot.instance_url == "https://test.example.com":
        print("  ✓ Instance URL cleaning")
    else:
        print(f"  ❌ Instance URL cleaning: {bot.instance_url}")
        return False
    
    return True

def test_mock_api_calls():
    """Test API calls with mocked responses."""
    print("\n🧪 Testing API calls (mocked)...")
    
    from gotosocial_bot_helper import GoToSocialBot
    
    bot = GoToSocialBot("https://test.example.com", "test_token")
    
    # Mock a successful status post
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "id": "12345",
        "content": "Test post",
        "url": "https://test.example.com/@testbot/12345"
    }
    
    with patch.object(bot.session, 'post', return_value=mock_response):
        try:
            result = bot.post_status("Test post")
            if result["id"] == "12345":
                print("  ✓ Status posting (mocked)")
            else:
                print("  ❌ Status posting - wrong response")
                return False
        except Exception as e:
            print(f"  ❌ Status posting: {e}")
            return False
    
    # Mock account verification
    mock_response.json.return_value = {
        "username": "testbot",
        "display_name": "Test Bot"
    }
    
    with patch.object(bot.session, 'get', return_value=mock_response):
        try:
            result = bot.get_account_info()
            if result["username"] == "testbot":
                print("  ✓ Account info (mocked)")
            else:
                print("  ❌ Account info - wrong response")
                return False
        except Exception as e:
            print(f"  ❌ Account info: {e}")
            return False
    
    return True

def test_error_handling():
    """Test error handling in various scenarios."""
    print("\n🧪 Testing error handling...")
    
    from gotosocial_bot_helper import GoToSocialBot
    
    # Test with non-existent credentials file
    try:
        bot = GoToSocialBot.from_credentials_file("nonexistent.json")
        print("  ❌ Should have raised FileNotFoundError")
        return False
    except FileNotFoundError:
        print("  ✓ FileNotFoundError for missing credentials")
    except Exception as e:
        print(f"  ❌ Wrong exception type: {e}")
        return False
    
    # Test with invalid JSON
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("invalid json content")
        temp_file = f.name
    
    try:
        bot = GoToSocialBot.from_credentials_file(temp_file)
        print("  ❌ Should have raised JSON decode error")
        return False
    except json.JSONDecodeError:
        print("  ✓ JSONDecodeError for invalid JSON")
    except Exception as e:
        print(f"  ❌ Wrong exception type: {e}")
        return False
    finally:
        os.unlink(temp_file)
    
    return True

def main():
    """Run all tests."""
    print("🧪 GoToSocial Setup Tools - Test Suite")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_credential_file_handling,
        test_api_request_formatting,
        test_mock_api_calls,
        test_error_handling
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print(f"  ❌ {test.__name__} failed")
    
    print(f"\n📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! The setup tools are working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())