#!/usr/bin/env python3
"""
Comprehensive test for export functionality
"""

import requests
import json
import os
import time

API_BASE = "http://localhost:8000"

def test_service_health():
    """Test if services are running"""
    try:
        # Test API health
        response = requests.get(f"{API_BASE}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API service is running")
            return True
        else:
            print(f"❌ API service not responding: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API service not accessible: {e}")
        return False

def login():
    """Login and get token"""
    try:
        response = requests.post(f"{API_BASE}/api/v1/auth/login", data={
            "username": "test@example.com",
            "password": "test123"
        }, timeout=10)
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("✅ Login successful")
            return token
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_export_preview(token):
    """Test export preview"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE}/api/v1/export/insights/preview", headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Export preview successful")
            print(f"   📊 Generated {len(data.get('insights', []))} insights")
            print(f"   🎯 Generated {len(data.get('recommendations', []))} recommendations")
            print(f"   📈 Analyzed {len(data.get('channel_performance', {}))} channels")
            return True
        else:
            print(f"❌ Export preview failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
    except Exception as e:
        print(f"❌ Export preview error: {e}")
        return False

def test_export_formats(token):
    """Test different export formats"""
    headers = {"Authorization": f"Bearer {token}"}
    formats = ["json", "csv", "txt"]
    results = {}
    
    for fmt in formats:
        try:
            print(f"   Testing {fmt.upper()} export...")
            response = requests.get(f"{API_BASE}/api/v1/export/insights?format={fmt}", 
                                  headers=headers, timeout=30)
            
            if response.status_code == 200:
                content_length = len(response.content)
                print(f"   ✅ {fmt.upper()} export successful ({content_length:,} bytes)")
                
                # Save sample to file for verification
                filename = f"export_test.{fmt}"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"      💾 Saved sample to {filename}")
                
                results[fmt] = True
            else:
                print(f"   ❌ {fmt.upper()} export failed: {response.status_code}")
                print(f"      Response: {response.text[:100]}...")
                results[fmt] = False
                
        except Exception as e:
            print(f"   ❌ {fmt.upper()} export error: {e}")
            results[fmt] = False
    
    return results

def verify_export_content():
    """Verify the content of exported files"""
    print("\n🔍 Verifying export content...")
    
    # Check JSON structure
    try:
        with open('export_test.json', 'r') as f:
            json_data = json.load(f)
        
        required_keys = ['export_metadata', 'model_info', 'channel_performance', 'insights', 'recommendations']
        missing_keys = [key for key in required_keys if key not in json_data]
        
        if not missing_keys:
            print("   ✅ JSON structure is complete")
            print(f"      📊 Contains {len(json_data['channel_performance'])} channels")
            print(f"      💡 Contains {len(json_data['insights'])} insights")
            print(f"      🎯 Contains {len(json_data['recommendations'])} recommendations")
        else:
            print(f"   ❌ JSON missing keys: {missing_keys}")
            
    except Exception as e:
        print(f"   ❌ JSON verification failed: {e}")
    
    # Check CSV structure
    try:
        with open('export_test.csv', 'r') as f:
            csv_content = f.read()
        
        if "MMM INSIGHTS EXPORT" in csv_content and "CHANNEL PERFORMANCE" in csv_content:
            print("   ✅ CSV structure is correct")
            lines = csv_content.split('\n')
            print(f"      📄 Contains {len(lines)} lines")
        else:
            print("   ❌ CSV structure is incorrect")
            
    except Exception as e:
        print(f"   ❌ CSV verification failed: {e}")
    
    # Check TXT structure
    try:
        with open('export_test.txt', 'r') as f:
            txt_content = f.read()
        
        if "MMM INSIGHTS & RECOMMENDATIONS REPORT" in txt_content and "CHANNEL PERFORMANCE" in txt_content:
            print("   ✅ TXT structure is correct")
            lines = txt_content.split('\n')
            print(f"      📄 Contains {len(lines)} lines")
        else:
            print("   ❌ TXT structure is incorrect")
            
    except Exception as e:
        print(f"   ❌ TXT verification failed: {e}")

def cleanup_test_files():
    """Clean up test files"""
    test_files = ['export_test.json', 'export_test.csv', 'export_test.txt']
    for file in test_files:
        try:
            if os.path.exists(file):
                os.remove(file)
        except:
            pass

def main():
    print("🧪 COMPREHENSIVE EXPORT FUNCTIONALITY TEST")
    print("=" * 50)
    
    # Test 1: Service Health
    print("\n1️⃣ Testing service health...")
    if not test_service_health():
        print("❌ Services not ready. Please run 'pnpm dev' first.")
        return False
    
    # Test 2: Authentication
    print("\n2️⃣ Testing authentication...")
    token = login()
    if not token:
        print("❌ Authentication failed. Please ensure database is seeded.")
        return False
    
    # Test 3: Export Preview
    print("\n3️⃣ Testing export preview...")
    if not test_export_preview(token):
        print("❌ Export preview failed.")
        return False
    
    # Test 4: Export Formats
    print("\n4️⃣ Testing export formats...")
    format_results = test_export_formats(token)
    
    # Test 5: Content Verification
    verify_export_content()
    
    # Summary
    print("\n📋 TEST SUMMARY")
    print("=" * 30)
    successful_formats = sum(1 for success in format_results.values() if success)
    print(f"✅ Successful formats: {successful_formats}/3")
    
    for fmt, success in format_results.items():
        status = "✅" if success else "❌"
        print(f"{status} {fmt.upper()} export")
    
    # Cleanup
    print("\n🧹 Cleaning up test files...")
    cleanup_test_files()
    
    if successful_formats == 3:
        print("\n🎉 ALL EXPORT TESTS PASSED!")
        print("The Export Recommendations feature is working perfectly!")
        return True
    else:
        print(f"\n⚠️  {3 - successful_formats} export format(s) failed.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
