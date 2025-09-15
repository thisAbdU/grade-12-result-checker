#!/usr/bin/env python3
"""
Simple test to verify the bot can start without errors
"""

import os
import sys

def test_imports():
    """Test if all imports work"""
    try:
        import telegram_bot
        print("✅ Import successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_bot_creation():
    """Test if bot can be created"""
    try:
        import telegram_bot
        # Use a dummy token for testing
        bot = telegram_bot.Grade12ResultBot("dummy_token")
        print("✅ Bot creation successful")
        return True
    except Exception as e:
        print(f"❌ Bot creation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Grade 12 Results Bot...")
    
    if not test_imports():
        sys.exit(1)
    
    if not test_bot_creation():
        sys.exit(1)
    
    print("🎉 All tests passed!")

if __name__ == '__main__':
    main()
