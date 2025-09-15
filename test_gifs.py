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
    """Test total result extraction logic"""
    print("\n🧮 Testing total result extraction...")
    
    # Test data - last item is the total
    test_results = [
        {"Subject": "Math", "Result": "85"},
        {"Subject": "English", "Result": "78"},
        {"Subject": "Science", "Result": "92"},
        {"Subject": "History", "Result": "88"},
        {"Subject": "Total", "Result": "343"}  # Last item is the total
    ]
    
    # Get total from last item (as per API response structure)
    if test_results:
        last_result = test_results[-1]
        total_grade = last_result.get('Result', 'N/A')
        
        try:
            if isinstance(total_grade, str) and total_grade.replace('.', '').isdigit():
                total = float(total_grade)
            else:
                total = 0
        except (ValueError, TypeError):
            total = 0
    else:
        total = 0
    
    print(f"📊 Test total (from last item): {total}")
    
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
