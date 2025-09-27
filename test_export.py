#!/usr/bin/env python3
"""
Test script for export functionality
"""

import requests
import json
import os

API_BASE = "http://localhost:8000"

def login():
    """Login and get token"""
    response = requests.post(f"{API_BASE}/api/v1/auth/login", data={
        "username": "test@example.com",
        "password": "test123"
    })
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def test_export_preview(token):
    """Test export preview"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/api/v1/export/insights/preview", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Export preview successful")
        print(f"Generated {len(data['insights'])} insights and {len(data['recommendations'])} recommendations")
        return True
    else:
        print(f"❌ Export preview failed: {response.status_code} - {response.text}")
        return False

def test_export_formats(token):
    """Test different export formats"""
    headers = {"Authorization": f"Bearer {token}"}
    formats = ["json", "csv", "txt"]
    
    for fmt in formats:
        response = requests.get(f"{API_BASE}/api/v1/export/insights?format={fmt}", headers=headers)
        
        if response.status_code == 200:
            print(f"✅ Export {fmt.upper()} successful ({len(response.content)} bytes)")
            
            # Save sample to file
            filename = f"sample_export.{fmt}"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"   Saved sample to {filename}")
        else:
            print(f"❌ Export {fmt.upper()} failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    print("🧪 Testing Export Functionality")
    print("=" * 40)
    
    # Login
    print("1. Logging in...")
    token = login()
    if not token:
        exit(1)
    
    print("2. Testing export preview...")
    if not test_export_preview(token):
        exit(1)
    
    print("3. Testing export formats...")
    test_export_formats(token)
    
    print("\n🎉 All tests completed!")
