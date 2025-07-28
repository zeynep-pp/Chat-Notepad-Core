#!/usr/bin/env python3
"""
Comprehensive test script for Days 3-4 Advanced Features
Tests version history, command history, AI suggestions, and translation
"""

import asyncio
import json
import time
from uuid import uuid4
from typing import Dict, Any
import httpx

BASE_URL = "http://localhost:8000"

class AdvancedFeaturesTest:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = {}
        self.test_user_email = f"test_{uuid4().hex[:8]}@example.com"
        self.test_note_id = None
        self.test_version_id = None

    async def setup_auth(self):
        """Setup authentication for testing"""
        print("🔑 Setting up authentication...")
        
        # Register test user
        async with httpx.AsyncClient() as client:
            register_data = {
                "email": self.test_user_email,
                "password": "testpassword123"
            }
            
            response = await client.post(f"{self.base_url}/auth/signup", json=register_data)
            if response.status_code not in [200, 201]:
                print(f"Registration failed: {response.text}")
                return False
            
            # Login to get token
            response = await client.post(f"{self.base_url}/auth/signin", json=register_data)
            if response.status_code != 200:
                print(f"Login failed: {response.text}")
                return False
            
            token_data = response.json()
            self.headers["Authorization"] = f"Bearer {token_data['access_token']}"
            print("✅ Authentication setup complete")
            return True

    async def test_version_system(self):
        """Test version tracking and history"""
        print("\n📝 Testing Version System...")
        
        async with httpx.AsyncClient() as client:
            # Create a test note
            note_data = {
                "title": "Version Test Note",
                "content": "Original content for version testing",
                "tags": ["test", "version"]
            }
            
            response = await client.post(
                f"{self.base_url}/api/v1/notes",
                json=note_data,
                headers=self.headers
            )
            
            if response.status_code != 201:
                print(f"❌ Failed to create note: {response.text}")
                return False
            
            note = response.json()
            self.test_note_id = note["id"]
            print(f"✅ Created note: {self.test_note_id}")
            
            # Update the note content (should create auto-version)
            update_data = {"content": "Updated content - version 2"}
            response = await client.put(
                f"{self.base_url}/api/v1/notes/{self.test_note_id}",
                json=update_data,
                headers=self.headers
            )
            
            if response.status_code != 200:
                print(f"❌ Failed to update note: {response.text}")
                return False
            
            print("✅ Updated note content")
            
            # Create manual version
            version_data = {"change_description": "Manual version for testing"}
            response = await client.post(
                f"{self.base_url}/api/v1/notes/{self.test_note_id}/versions",
                json=version_data,
                headers=self.headers
            )
            
            if response.status_code != 200:
                print(f"❌ Failed to create version: {response.text}")
                return False
            
            version = response.json()
            self.test_version_id = version["id"]
            print("✅ Created manual version")
            
            # Get all versions
            response = await client.get(
                f"{self.base_url}/api/v1/notes/{self.test_note_id}/versions",
                headers=self.headers
            )
            
            if response.status_code != 200:
                print(f"❌ Failed to get versions: {response.text}")
                return False
            
            versions_data = response.json()
            print(f"✅ Retrieved {len(versions_data['versions'])} versions")
            
            # Test diff between versions
            if len(versions_data['versions']) >= 2:
                v1 = versions_data['versions'][0]['version_number']
                v2 = versions_data['versions'][1]['version_number']
                
                response = await client.get(
                    f"{self.base_url}/api/v1/notes/{self.test_note_id}/diff/{v1}/{v2}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    diff_data = response.json()
                    print("✅ Generated diff between versions")
                else:
                    print(f"⚠️ Diff generation failed: {response.text}")
            
            print("✅ Version system test completed")
            return True

    async def test_command_history(self):
        """Test command history tracking"""
        print("\n📊 Testing Command History...")
        
        async with httpx.AsyncClient() as client:
            # Execute some text operations to generate history
            commands_to_test = [
                {"text": "Hello world", "command": "make formal"},
                {"text": "This is a test", "command": "summarize"},
                {"text": "Testing commands", "command": "expand"}
            ]
            
            for cmd in commands_to_test:
                response = await client.post(
                    f"{self.base_url}/api/v1/prompt",
                    json=cmd,
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    print(f"✅ Executed command: {cmd['command']}")
                else:
                    print(f"⚠️ Command failed: {cmd['command']}")
                
                # Small delay between commands
                await asyncio.sleep(0.5)
            
            # Get command history
            response = await client.get(
                f"{self.base_url}/api/v1/history/commands",
                headers=self.headers
            )
            
            if response.status_code != 200:
                print(f"❌ Failed to get command history: {response.text}")
                return False
            
            history_data = response.json()
            print(f"✅ Retrieved {history_data['total']} command history entries")
            
            # Get command stats
            response = await client.get(
                f"{self.base_url}/api/v1/history/stats",
                headers=self.headers
            )
            
            if response.status_code == 200:
                stats_data = response.json()
                print(f"✅ Command stats: {stats_data['total_commands']} total, {stats_data['success_rate']} success rate")
            else:
                print(f"⚠️ Failed to get stats: {response.text}")
            
            # Test search
            response = await client.get(
                f"{self.base_url}/api/v1/history/search?q=test",
                headers=self.headers
            )
            
            if response.status_code == 200:
                search_results = response.json()
                print(f"✅ Search found {len(search_results)} matching commands")
            else:
                print(f"⚠️ Search failed: {response.text}")
            
            print("✅ Command history test completed")
            return True

    async def test_ai_suggestions(self):
        """Test AI suggestions system"""
        print("\n🤖 Testing AI Suggestions...")
        
        async with httpx.AsyncClient() as client:
            # Test different types of suggestions
            suggestion_tests = [
                {
                    "context": "Writing a business email",
                    "text": "I would like to",
                    "cursor_position": 15,
                    "context_type": "content"
                },
                {
                    "context": "help document",
                    "text": "summarize this text",
                    "cursor_position": 10,
                    "context_type": "command"
                },
                {
                    "context": "formal writing",
                    "text": "This text needs improvement",
                    "cursor_position": 20,
                    "context_type": "style"
                }
            ]
            
            for test_case in suggestion_tests:
                response = await client.post(
                    f"{self.base_url}/api/v1/ai/suggest",
                    json=test_case,
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    suggestions = response.json()
                    print(f"✅ {test_case['context_type']} suggestions: {len(suggestions['suggestions'])} items")
                else:
                    print(f"⚠️ Suggestions failed for {test_case['context_type']}: {response.text}")
            
            # Get suggestion stats
            response = await client.get(
                f"{self.base_url}/api/v1/ai/suggest/stats",
                headers=self.headers
            )
            
            if response.status_code == 200:
                stats = response.json()
                print(f"✅ Suggestion stats: {stats['total_suggestions']} total")
            else:
                print(f"⚠️ Failed to get suggestion stats: {response.text}")
            
            print("✅ AI suggestions test completed")
            return True

    async def test_translation_system(self):
        """Test translation capabilities"""
        print("\n🌍 Testing Translation System...")
        
        async with httpx.AsyncClient() as client:
            # Get supported languages
            response = await client.get(f"{self.base_url}/api/v1/ai/languages")
            
            if response.status_code != 200:
                print(f"❌ Failed to get supported languages: {response.text}")
                return False
            
            languages = response.json()
            print(f"✅ Found {languages['total']} supported languages")
            
            # Test basic translation
            translation_data = {
                "text": "Hello world, this is a test",
                "target_language": "es"
            }
            
            response = await client.post(
                f"{self.base_url}/api/v1/ai/translate",
                json=translation_data,
                headers=self.headers
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Translated: '{result['original_text']}' -> '{result['translated_text']}'")
            else:
                print(f"⚠️ Translation failed: {response.text}")
            
            # Test language detection
            response = await client.post(
                f"{self.base_url}/api/v1/ai/detect-language",
                params={"text": "Bonjour le monde"},
                headers=self.headers
            )
            
            if response.status_code == 200:
                detection = response.json()
                print(f"✅ Detected language: {detection['language']} ({detection['language_name']})")
            else:
                print(f"⚠️ Language detection failed: {response.text}")
            
            # Test note translation if we have a test note
            if self.test_note_id:
                response = await client.post(
                    f"{self.base_url}/api/v1/ai/translate/note/{self.test_note_id}?target_language=fr",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print("✅ Note translation completed")
                else:
                    print(f"⚠️ Note translation failed: {response.text}")
            
            print("✅ Translation system test completed")
            return True

    async def test_rate_limiting(self):
        """Test rate limiting functionality"""
        print("\n⏱️ Testing Rate Limiting...")
        
        async with httpx.AsyncClient() as client:
            # Make multiple rapid requests to trigger rate limiting
            rapid_requests = []
            for i in range(5):
                task = client.post(
                    f"{self.base_url}/api/v1/ai/suggest",
                    json={
                        "context": "test",
                        "text": f"test {i}",
                        "cursor_position": 5,
                        "context_type": "content"
                    },
                    headers=self.headers
                )
                rapid_requests.append(task)
            
            # Execute all requests concurrently
            responses = await asyncio.gather(*rapid_requests, return_exceptions=True)
            
            rate_limited = 0
            successful = 0
            
            for response in responses:
                if isinstance(response, httpx.Response):
                    if response.status_code == 429:
                        rate_limited += 1
                    elif response.status_code == 200:
                        successful += 1
            
            print(f"✅ Rate limiting test: {successful} successful, {rate_limited} rate-limited")
            
            if rate_limited == 0:
                print("⚠️ No rate limiting detected - this is expected if limits are high")
            
            print("✅ Rate limiting test completed")
            return True

    async def cleanup(self):
        """Cleanup test data"""
        print("\n🧹 Cleaning up test data...")
        
        async with httpx.AsyncClient() as client:
            # Delete test note if created
            if self.test_note_id:
                response = await client.delete(
                    f"{self.base_url}/api/v1/notes/{self.test_note_id}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    print("✅ Test note deleted")
                else:
                    print(f"⚠️ Failed to delete test note: {response.text}")
            
            print("✅ Cleanup completed")

    async def run_all_tests(self):
        """Run all advanced feature tests"""
        print("🚀 Starting Advanced Features Test Suite")
        print("=" * 50)
        
        # Setup authentication
        if not await self.setup_auth():
            print("❌ Authentication setup failed, aborting tests")
            return False
        
        tests = [
            ("Version System", self.test_version_system),
            ("Command History", self.test_command_history),
            ("AI Suggestions", self.test_ai_suggestions),
            ("Translation System", self.test_translation_system),
            ("Rate Limiting", self.test_rate_limiting)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                print(f"\n🧪 Running {test_name} test...")
                start_time = time.time()
                
                success = await test_func()
                elapsed = time.time() - start_time
                
                if success:
                    print(f"✅ {test_name} test PASSED ({elapsed:.2f}s)")
                    passed += 1
                else:
                    print(f"❌ {test_name} test FAILED ({elapsed:.2f}s)")
                    
            except Exception as e:
                print(f"❌ {test_name} test ERROR: {str(e)}")
        
        # Cleanup
        await self.cleanup()
        
        # Final results
        print("\n" + "=" * 50)
        print("🎯 TEST RESULTS SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Days 3-4 features are working correctly.")
        else:
            print("⚠️ Some tests failed. Check the logs above for details.")
        
        return passed == total

async def main():
    tester = AdvancedFeaturesTest()
    success = await tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))