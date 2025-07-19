#!/usr/bin/env python3

"""
Test script for Notes API endpoints
Run this to test the note storage functionality
"""

import requests
import json
from uuid import uuid4

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword123"

def test_notes_api():
    """Test all note API endpoints"""
    
    print("🧪 Testing Notes API...")
    
    # Step 1: Sign up or sign in to get auth token
    print("\n1. Authenticating user...")
    
    # Try to sign up
    signup_data = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
        "full_name": "Test User"
    }
    
    response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
    if response.status_code not in [200, 201]:
        print(f"   Signup failed (probably user exists): {response.status_code}")
        # Try to sign in instead
        signin_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        response = requests.post(f"{BASE_URL}/auth/signin", json=signin_data)
        if response.status_code not in [200, 201]:
            print(f"   ❌ Authentication failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    auth_data = response.json()
    access_token = auth_data.get("access_token")
    
    if not access_token:
        print("   ❌ No access token received")
        return False
    
    print(f"   ✅ Authenticated successfully")
    
    # Headers for authenticated requests
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Step 2: Create a test note
    print("\n2. Creating test note...")
    
    create_data = {
        "title": "Test Note",
        "content": "This is a test note content",
        "is_favorite": False,
        "tags": ["test", "api"]
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/notes/", json=create_data, headers=headers)
    if response.status_code not in [200, 201]:
        print(f"   ❌ Create note failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    note_data = response.json()
    note_id = note_data["id"]
    print(f"   ✅ Note created with ID: {note_id}")
    
    # Step 3: Get the note
    print("\n3. Getting note by ID...")
    
    response = requests.get(f"{BASE_URL}/api/v1/notes/{note_id}", headers=headers)
    if response.status_code != 200:
        print(f"   ❌ Get note failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    retrieved_note = response.json()
    print(f"   ✅ Note retrieved: {retrieved_note['title']}")
    
    # Step 4: Update the note
    print("\n4. Updating note...")
    
    update_data = {
        "title": "Updated Test Note",
        "content": "This is updated content",
        "is_favorite": True,
        "tags": ["test", "api", "updated"]
    }
    
    response = requests.put(f"{BASE_URL}/api/v1/notes/{note_id}", json=update_data, headers=headers)
    if response.status_code != 200:
        print(f"   ❌ Update note failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    updated_note = response.json()
    print(f"   ✅ Note updated: {updated_note['title']}")
    
    # Step 5: List notes
    print("\n5. Listing notes...")
    
    response = requests.get(f"{BASE_URL}/api/v1/notes/?page=1&per_page=10", headers=headers)
    if response.status_code != 200:
        print(f"   ❌ List notes failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    notes_list = response.json()
    print(f"   ✅ Listed {len(notes_list['notes'])} notes")
    
    # Step 6: Search notes
    print("\n6. Searching notes...")
    
    response = requests.get(f"{BASE_URL}/api/v1/notes/search?query=test", headers=headers)
    if response.status_code != 200:
        print(f"   ❌ Search notes failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    search_results = response.json()
    print(f"   ✅ Found {len(search_results['notes'])} notes matching 'test'")
    
    # Step 7: Get favorite notes
    print("\n7. Getting favorite notes...")
    
    response = requests.get(f"{BASE_URL}/api/v1/notes/favorites", headers=headers)
    if response.status_code != 200:
        print(f"   ❌ Get favorites failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    favorites = response.json()
    print(f"   ✅ Found {len(favorites)} favorite notes")
    
    # Step 8: Get user tags
    print("\n8. Getting user tags...")
    
    response = requests.get(f"{BASE_URL}/api/v1/notes/tags", headers=headers)
    if response.status_code != 200:
        print(f"   ❌ Get tags failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    tags = response.json()
    print(f"   ✅ Found tags: {tags}")
    
    # Step 9: Delete the note
    print("\n9. Deleting note...")
    
    response = requests.delete(f"{BASE_URL}/api/v1/notes/{note_id}", headers=headers)
    if response.status_code != 200:
        print(f"   ❌ Delete note failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    print(f"   ✅ Note deleted successfully")
    
    # Step 10: Verify note is deleted
    print("\n10. Verifying note deletion...")
    
    response = requests.get(f"{BASE_URL}/api/v1/notes/{note_id}", headers=headers)
    if response.status_code != 404:
        print(f"   ❌ Note should be deleted but still exists: {response.status_code}")
        return False
    
    print(f"   ✅ Note properly deleted")
    
    print("\n🎉 All tests passed!")
    return True

if __name__ == "__main__":
    try:
        print("🚀 Starting Notes API tests...")
        print(f"Base URL: {BASE_URL}")
        
        success = test_notes_api()
        
        if success:
            print("\n✅ All tests completed successfully!")
        else:
            print("\n❌ Some tests failed!")
            
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()