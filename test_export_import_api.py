#!/usr/bin/env python3
"""
Test script for Export/Import API endpoints
Tests the newly implemented export and import functionality
"""

import requests
import json
import os
from io import BytesIO

# Configuration
BASE_URL = "http://127.0.0.1:8000"
TEST_USER_EMAIL = "testexport@example.com"
TEST_USER_PASSWORD = "testpassword123"
TEST_USER_NAME = "Export Test User"

def test_auth_and_get_token():
    """Get authentication token for testing"""
    print("🔐 Testing authentication...")
    
    # Sign up
    signup_data = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
        "full_name": TEST_USER_NAME
    }
    
    response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
    if response.status_code == 201:
        print("✅ User signed up successfully")
    elif response.status_code == 400 and "already registered" in response.text:
        print("ℹ️  User already exists, proceeding with sign-in")
    else:
        print(f"❌ Signup failed: {response.status_code} - {response.text}")
        return None
    
    # Sign in
    signin_data = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/auth/signin", json=signin_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Successfully authenticated")
        return token
    else:
        print(f"❌ Sign-in failed: {response.status_code} - {response.text}")
        return None

def test_create_sample_notes(token):
    """Create sample notes for testing export"""
    print("\n📝 Creating sample notes...")
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    sample_notes = [
        {
            "title": "Export Test Note 1",
            "content": "This is a test note for export functionality.\n\nIt has multiple paragraphs and **markdown** formatting.",
            "tags": ["test", "export"],
            "is_favorite": True
        },
        {
            "title": "Export Test Note 2",
            "content": "Another test note with different content.\n\n- Bullet point 1\n- Bullet point 2\n- Bullet point 3",
            "tags": ["test", "markdown"],
            "is_favorite": False
        },
        {
            "title": "Simple Note",
            "content": "Just a simple note with plain text content for testing purposes.",
            "tags": ["simple"],
            "is_favorite": False
        }
    ]
    
    created_notes = []
    for note_data in sample_notes:
        response = requests.post(f"{BASE_URL}/api/v1/notes/", json=note_data, headers=headers)
        if response.status_code == 200:
            note = response.json()
            created_notes.append(note)
            print(f"✅ Created note: {note['title']}")
        else:
            print(f"❌ Failed to create note: {response.status_code} - {response.text}")
    
    return created_notes

def test_export_formats(token, note_id, note_title):
    """Test all export formats for a single note"""
    print(f"\n📤 Testing export formats for note: {note_title}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test Markdown export
    print("  Testing Markdown export...")
    response = requests.get(f"{BASE_URL}/api/v1/export/markdown/{note_id}", headers=headers)
    if response.status_code == 200:
        print("  ✅ Markdown export successful")
        print(f"  📄 Content length: {len(response.content)} bytes")
        # Save to file
        with open(f"test_export_{note_title.replace(' ', '_')}.md", "wb") as f:
            f.write(response.content)
    else:
        print(f"  ❌ Markdown export failed: {response.status_code}")
    
    # Test TXT export
    print("  Testing TXT export...")
    response = requests.get(f"{BASE_URL}/api/v1/export/txt/{note_id}", headers=headers)
    if response.status_code == 200:
        print("  ✅ TXT export successful")
        print(f"  📄 Content length: {len(response.content)} bytes")
        # Save to file
        with open(f"test_export_{note_title.replace(' ', '_')}.txt", "wb") as f:
            f.write(response.content)
    else:
        print(f"  ❌ TXT export failed: {response.status_code}")
    
    # Test PDF export
    print("  Testing PDF export...")
    response = requests.get(f"{BASE_URL}/api/v1/export/pdf/{note_id}", headers=headers)
    if response.status_code == 200:
        print("  ✅ PDF export successful")
        print(f"  📄 Content length: {len(response.content)} bytes")
        # Save to file
        with open(f"test_export_{note_title.replace(' ', '_')}.pdf", "wb") as f:
            f.write(response.content)
    else:
        print(f"  ❌ PDF export failed: {response.status_code}")
        print(f"  Error: {response.text}")

def test_bulk_export(token, note_ids):
    """Test bulk export functionality"""
    print(f"\n📦 Testing bulk export for {len(note_ids)} notes...")
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Test bulk markdown export
    print("  Testing bulk Markdown export...")
    response = requests.post(
        f"{BASE_URL}/api/v1/export/bulk?format=markdown", 
        json=note_ids, 
        headers=headers
    )
    if response.status_code == 200:
        print("  ✅ Bulk Markdown export successful")
        with open("test_bulk_export.md", "wb") as f:
            f.write(response.content)
    else:
        print(f"  ❌ Bulk Markdown export failed: {response.status_code}")
    
    # Test bulk txt export
    print("  Testing bulk TXT export...")
    response = requests.post(
        f"{BASE_URL}/api/v1/export/bulk?format=txt", 
        json=note_ids, 
        headers=headers
    )
    if response.status_code == 200:
        print("  ✅ Bulk TXT export successful")
        with open("test_bulk_export.txt", "wb") as f:
            f.write(response.content)
    else:
        print(f"  ❌ Bulk TXT export failed: {response.status_code}")

def test_import_formats(token):
    """Test import functionality"""
    print("\n📥 Testing import functionality...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test get supported formats
    print("  Getting supported formats...")
    response = requests.get(f"{BASE_URL}/api/v1/import/formats", headers=headers)
    if response.status_code == 200:
        formats = response.json()
        print("  ✅ Supported formats retrieved:")
        for format_type, description in formats["supported_formats"].items():
            print(f"    - {format_type}: {description}")
    else:
        print(f"  ❌ Failed to get formats: {response.status_code}")
    
    # Create test files for import
    test_files = {
        "test_import.txt": "Test Import Note\n" + "="*20 + "\n\nThis is a test note imported from TXT file.\n\nIt has multiple lines and paragraphs.",
        "test_import.md": "# Test Markdown Import\n\n**Tags:** imported, test\n\nThis is a test note imported from Markdown file.\n\n- Item 1\n- Item 2\n- Item 3",
        "test_import.json": json.dumps({
            "title": "JSON Import Test",
            "content": "This note was imported from JSON format.",
            "tags": ["json", "import", "test"],
            "is_favorite": True
        })
    }
    
    # Create and test import for each file type
    for filename, content in test_files.items():
        print(f"  Testing import of {filename}...")
        
        # Write test file
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Test import
        with open(filename, "rb") as f:
            files = {"file": (filename, f, "text/plain")}
            response = requests.post(f"{BASE_URL}/api/v1/import/file", files=files, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"    ✅ Import successful: {result['imported_count']}/{result['total_count']} notes")
            if result['errors']:
                print(f"    ⚠️  Errors: {result['errors']}")
        else:
            print(f"    ❌ Import failed: {response.status_code} - {response.text}")
        
        # Clean up test file
        os.remove(filename)

def test_export_formats_endpoints(token):
    """Test export formats endpoint"""
    print("\n📋 Testing export formats endpoint...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/api/v1/export/formats", headers=headers)
    if response.status_code == 200:
        formats = response.json()
        print("✅ Export formats retrieved:")
        print(f"  Single note formats: {formats['single_note_formats']}")
        print(f"  Bulk formats: {formats['bulk_formats']}")
        for format_name, description in formats['descriptions'].items():
            print(f"  - {format_name}: {description}")
    else:
        print(f"❌ Failed to get export formats: {response.status_code}")

def main():
    """Main test function"""
    print("🚀 Starting Export/Import API Tests")
    print("=" * 50)
    
    # Get authentication token
    token = test_auth_and_get_token()
    if not token:
        print("❌ Authentication failed, cannot proceed with tests")
        return
    
    # Create sample notes
    notes = test_create_sample_notes(token)
    if not notes:
        print("❌ Failed to create sample notes")
        return
    
    # Test individual note exports
    for note in notes[:2]:  # Test first 2 notes
        test_export_formats(token, note["id"], note["title"])
    
    # Test bulk export
    note_ids = [note["id"] for note in notes]
    test_bulk_export(token, note_ids)
    
    # Test import functionality
    test_import_formats(token)
    
    # Test export formats endpoint
    test_export_formats_endpoints(token)
    
    print("\n" + "=" * 50)
    print("🎉 Export/Import API tests completed!")
    print("\nGenerated files:")
    print("- test_export_*.md (Markdown exports)")
    print("- test_export_*.txt (TXT exports)")
    print("- test_export_*.pdf (PDF exports)")
    print("- test_bulk_export.md (Bulk Markdown)")
    print("- test_bulk_export.txt (Bulk TXT)")

if __name__ == "__main__":
    main()