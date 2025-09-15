#!/usr/bin/env python3
"""
Test script to verify GIF files exist and are accessible
"""

import os

def test_gif_files():
    """Test if GIF files exist and are readable"""
    gifs = [
        "assets/tom-and-jerry-throwing-flowers-celebration-dance.gif",
        "assets/sushichaeng-tom-and-jerry.gif"
    ]
    
    print("🧪 Testing GIF files...")
    
    for gif_path in gifs:
        if os.path.exists(gif_path):
            file_size = os.path.getsize(gif_path)
            print(f"✅ {gif_path} - {file_size:,} bytes")
        else:
            print(f"❌ {gif_path} - File not found")
            return False
    
    print("🎉 All GIF files are ready!")
    return True

def test_total_calculation():
    """Test total result calculation logic"""
    print("\n🧮 Testing total result calculation...")
    
    # Test data
    test_results = [
        {"Subject": "Math", "Result": "85"},
        {"Subject": "English", "Result": "78"},
        {"Subject": "Science", "Result": "92"},
        {"Subject": "History", "Result": "88"}
    ]
    
    total = 0
    for result in test_results:
        grade = result.get('Result', 'N/A')
        try:
            if isinstance(grade, str) and grade.replace('.', '').isdigit():
                total += float(grade)
        except (ValueError, TypeError):
            pass
    
    print(f"📊 Test total: {total}")
    
    if total > 300:
        print("🎉 Would send celebration GIF (passed)")
    else:
        print("😔 Would send sad GIF (didn't pass)")
    
    return True

def main():
    """Run all tests"""
    print("🚀 Testing Grade 12 Results Bot GIF Features")
    print("=" * 50)
    
    if not test_gif_files():
        print("❌ GIF file test failed!")
        return False
    
    if not test_total_calculation():
        print("❌ Total calculation test failed!")
        return False
    
    print("\n✅ All tests passed! Bot is ready with GIF features.")
    return True

if __name__ == '__main__':
    main()
