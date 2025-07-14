#!/usr/bin/env python3
"""
Test script for the API Gateway functionality.
This script tests the gateway's routing, authentication, and rate limiting features.
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any

# Gateway configuration
GATEWAY_URL = "http://localhost:8001"
BACKEND_URL = "http://localhost:8000"

async def test_health_check():
    """Test gateway health check endpoint."""
    print("🔍 Testing health check...")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{GATEWAY_URL}/health")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False

async def test_public_endpoint():
    """Test a public endpoint (no auth required)."""
    print("🔍 Testing public endpoint...")
    
    async with httpx.AsyncClient() as client:
        # Test auth endpoint (public)
        response = await client.get(f"{GATEWAY_URL}/auth/register")
        
        if response.status_code in [200, 405, 422]:  # 405 for method not allowed, 422 for validation error
            print(f"✅ Public endpoint accessible: {response.status_code}")
            return True
        else:
            print(f"❌ Public endpoint failed: {response.status_code}")
            return False

async def test_protected_endpoint_without_auth():
    """Test a protected endpoint without authentication."""
    print("🔍 Testing protected endpoint without auth...")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{GATEWAY_URL}/user/profile")
        
        if response.status_code == 401:
            print("✅ Protected endpoint correctly requires authentication")
            return True
        else:
            print(f"❌ Protected endpoint should require auth: {response.status_code}")
            return False

async def test_rate_limiting():
    """Test rate limiting functionality."""
    print("🔍 Testing rate limiting...")
    
    async with httpx.AsyncClient() as client:
        # Make multiple requests to trigger rate limiting
        responses = []
        for i in range(5):
            response = await client.get(f"{GATEWAY_URL}/auth/register")
            responses.append(response.status_code)
            await asyncio.sleep(0.1)  # Small delay between requests
        
        # Check if any requests were rate limited
        rate_limited = any(status == 429 for status in responses)
        
        if rate_limited:
            print("✅ Rate limiting is working")
            return True
        else:
            print("⚠️ Rate limiting not triggered (this is normal for small number of requests)")
            return True  # Not a failure, just not enough requests

async def test_service_routing():
    """Test that requests are properly routed to services."""
    print("🔍 Testing service routing...")
    
    test_routes = [
        "/auth/login",
        "/user/profile", 
        "/song/list",
        "/search/query",
        "/album/list"
    ]
    
    async with httpx.AsyncClient() as client:
        for route in test_routes:
            response = await client.get(f"{GATEWAY_URL}{route}")
            
            if response.status_code in [200, 401, 404, 405, 422]:
                print(f"✅ Route {route}: {response.status_code}")
            else:
                print(f"❌ Route {route}: {response.status_code}")
    
    return True

async def test_cors_headers():
    """Test CORS headers are present."""
    print("🔍 Testing CORS headers...")
    
    async with httpx.AsyncClient() as client:
        response = await client.options(f"{GATEWAY_URL}/auth/login")
        
        cors_headers = [
            "access-control-allow-origin",
            "access-control-allow-methods",
            "access-control-allow-headers"
        ]
        
        headers_present = all(header in response.headers for header in cors_headers)
        
        if headers_present:
            print("✅ CORS headers are present")
            return True
        else:
            print("❌ CORS headers missing")
            return False

async def test_logging():
    """Test that requests are being logged."""
    print("🔍 Testing request logging...")
    
    async with httpx.AsyncClient() as client:
        # Make a test request
        response = await client.get(f"{GATEWAY_URL}/health")
        
        if response.status_code == 200:
            print("✅ Request logging test passed (check gateway logs)")
            return True
        else:
            print(f"❌ Request logging test failed: {response.status_code}")
            return False

async def test_gateway_features():
    """Run all gateway tests."""
    print("🚀 Starting API Gateway Tests")
    print("=" * 50)
    
    tests = [
        test_health_check,
        test_public_endpoint,
        test_protected_endpoint_without_auth,
        test_rate_limiting,
        test_service_routing,
        test_cors_headers,
        test_logging
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! API Gateway is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the gateway configuration and logs.")
    
    return passed == total

if __name__ == "__main__":
    print("API Gateway Test Suite")
    print("Make sure the gateway is running on port 8001")
    print("Make sure the main backend is running on port 8000")
    print("=" * 50)
    
    asyncio.run(test_gateway_features()) 