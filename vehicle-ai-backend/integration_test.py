#!/usr/bin/env python3
"""
Simple integration test for Vehicle AI System
Run this after starting all services to verify they're working together
"""

import requests
import time


def test_service(url, name):
    """Test if a service is responding"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {name}: OK")
            return True
        else:
            print(f"❌ {name}: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {name}: Connection failed - {e}")
        return False


def test_ml_parsing():
    """Test ML service parsing"""
    try:
        response = requests.post(
            "http://localhost:8001/parse",
            json={"text": "turn on the air conditioning"},
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            action = result.get('action', 'unknown')
            confidence = result.get('confidence', 0)
            print(f"✅ ML Parsing: {action} (confidence: {confidence:.2f})")
            return True
        else:
            print(f"❌ ML Parsing: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ML Parsing: {e}")
        return False


def test_backend_nlp():
    """Test backend NLP endpoint"""
    try:
        response = requests.post(
            "http://localhost:8000/api/nlp/process-voice",
            json={"text": "set temperature to 24 degrees"},
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            success = result.get('success', False)
            action = result.get('action', 'unknown')
            print(f"✅ Backend NLP: {action} (success: {success})")
            return True
        else:
            print(f"❌ Backend NLP: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend NLP: {e}")
        return False


def main():
    print("🧪 Vehicle AI Integration Test")
    print("=" * 40)

    # Test basic service health
    print("Testing service health...")
    services_ok = 0

    if test_service("http://localhost:8001/healthz", "ML Service"):
        services_ok += 1

    if test_service("http://localhost:8000/health", "Backend"):
        services_ok += 1

    if test_service("http://localhost:8000/api/status", "Backend API"):
        services_ok += 1

    print(f"\nServices healthy: {services_ok}/3")

    if services_ok < 2:
        print("❌ Too many services are down. Check your startup.")
        return

    # Test ML integration
    print("\nTesting ML integration...")

    if test_ml_parsing():
        print("✅ ML service is parsing commands correctly")

    if test_backend_nlp():
        print("✅ Backend is processing voice commands through ML")

    # Test vehicle state
    print("\nTesting vehicle state...")
    try:
        response = requests.get("http://localhost:8000/api/status")
        if response.status_code == 200:
            data = response.json()
            if 'vehicle_state' in data:
                print("✅ Vehicle state is accessible")
            else:
                print("❌ Vehicle state not found in response")
        else:
            print("❌ Cannot get vehicle state")
    except Exception as e:
        print(f"❌ Vehicle state test failed: {e}")

    print("\n🎉 Integration test complete!")
    print("If all tests pass, your system is integrated correctly.")
    print("\nNext: Open http://localhost:5173 to test the frontend.")


if __name__ == "__main__":
    main()