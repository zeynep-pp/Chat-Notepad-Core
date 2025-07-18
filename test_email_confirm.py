#!/usr/bin/env python3
"""
Test script for email confirmation endpoint
"""

import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_email_confirm_endpoint():
    """Test the email confirmation endpoint"""
    
    # Test data with dummy token
    payload = {
        "token": "dummy_token_for_testing"
    }
    
    url = "http://localhost:8000/auth/confirm-email"
    
    logger.info(f"🧪 Testing email confirmation endpoint: {url}")
    logger.info(f"📤 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload)
        
        logger.info(f"📊 Status Code: {response.status_code}")
        logger.info(f"📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 404:
            logger.error("❌ 404 Error - Endpoint not found")
        elif response.status_code == 400:
            logger.info("✅ Endpoint exists! Got expected 400 error for dummy token")
            logger.info(f"Response: {response.json()}")
        elif response.status_code == 422:
            logger.info("✅ Endpoint exists! Got validation error (expected)")
            logger.info(f"Response: {response.json()}")
        else:
            logger.info(f"📊 Status: {response.status_code}")
            logger.info(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        logger.error("❌ Connection refused - Server not running?")
        logger.info("💡 Start the server with: uvicorn app.main:app --reload")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_email_confirm_endpoint()