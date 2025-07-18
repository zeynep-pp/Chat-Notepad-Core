#!/usr/bin/env python3
"""
Test script to debug auth endpoint 404 error
"""

import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_auth_endpoint():
    """Test the auth signup endpoint"""
    
    # Test data
    payload = {
        "full_name": "ZEYNEP KOSE",
        "email": "zeynep.j177@gmail.com",
        "password": "Zey126"
    }
    
    url = "http://localhost:8000/auth/signup"
    
    logger.info(f"🧪 Testing endpoint: {url}")
    logger.info(f"📤 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload)
        
        logger.info(f"📊 Status Code: {response.status_code}")
        logger.info(f"📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 404:
            logger.error("❌ 404 Error - Endpoint not found")
            logger.info("🔍 Trying to get available endpoints...")
            
            # Test root endpoint
            root_response = requests.get("http://localhost:8000/")
            logger.info(f"Root endpoint status: {root_response.status_code}")
            if root_response.status_code == 200:
                logger.info(f"Root response: {root_response.json()}")
            
            # Test OpenAPI docs
            docs_response = requests.get("http://localhost:8000/docs")
            logger.info(f"Docs endpoint status: {docs_response.status_code}")
            
        elif response.status_code == 200:
            logger.info("✅ Success!")
            logger.info(f"Response: {response.json()}")
        else:
            logger.error(f"❌ Error {response.status_code}")
            logger.error(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        logger.error("❌ Connection refused - Server not running?")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_auth_endpoint()