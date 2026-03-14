#!/usr/bin/env python3
"""
Test script for Instamojo webhook
"""

import hashlib
import hmac
import requests
import sys

def generate_mac(data, salt="4e57693050da4345984d7d1360149032"):
    """Generate MAC signature for webhook."""
    sorted_keys = sorted(data.keys())
    message = "|".join(str(data[key]) for key in sorted_keys if key != "mac")
    
    generated_mac = hmac.new(
        salt.encode(),
        message.encode(),
        hashlib.sha1
    ).hexdigest()
    
    return generated_mac

def test_webhook_local():
    """Test webhook on local server."""
    
    # Test data
    test_data = {
        "amount": "20.00",
        "buyer": "test@example.com",
        "buyer_name": "Test User",
        "buyer_phone": "+919999999999",
        "currency": "INR",
        "fees": "0.40",
        "longurl": "https://www.instamojo.com/@khanjansevakendra/test",
        "payment_id": "MOJO123456789",
        "payment_request_id": "pr_test_123",
        "purpose": "Basic Plan - 10 Credits",
        "shorturl": "https://imjo.in/test123",
        "status": "Credit",
        "custom_user_id": "1",
        "custom_plan_name": "basic",
        "custom_order_id": "test-order-123",
    }
    
    # Generate MAC
    test_data["mac"] = generate_mac(test_data)
    
    print("=" * 60)
    print("Testing Instamojo Webhook")
    print("=" * 60)
    print(f"\nTest Data: {test_data}")
    print(f"\nGenerated MAC: {test_data['mac']}")
    
    # Send webhook
    url = "http://localhost:7002/api/payments/webhook"
    print(f"\nSending POST request to: {url}")
    
    try:
        response = requests.post(url, data=test_data, timeout=10)
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {response.json()}")
        
        if response.status_code == 200:
            print("\n✅ Webhook test successful!")
        else:
            print("\n❌ Webhook test failed!")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to server!")
        print("Make sure the server is running on port 7002")
        print("\nStart server with:")
        print("GOOGLE_CLIENT_SECRET='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' rembg s --host 0.0.0.0 --port 7002")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

def verify_mac_example():
    """Show example of MAC verification."""
    
    print("\n" + "=" * 60)
    print("MAC Verification Example")
    print("=" * 60)
    
    # Example data from Instamojo
    data = {
        "amount": "20.00",
        "buyer": "test@example.com",
        "currency": "INR",
        "status": "Credit",
    }
    
    salt = "4e57693050da4345984d7d1360149032"
    
    # Step 1: Sort keys
    sorted_keys = sorted(data.keys())
    print(f"\nSorted Keys: {sorted_keys}")
    
    # Step 2: Create message
    message = "|".join(str(data[key]) for key in sorted_keys)
    print(f"Message: {message}")
    
    # Step 3: Generate MAC
    mac = hmac.new(salt.encode(), message.encode(), hashlib.sha1).hexdigest()
    print(f"Generated MAC: {mac}")
    
    print("\n" + "=" * 60)

def generate_ngrok_command():
    """Generate ngrok command."""
    print("\n" + "=" * 60)
    print("Ngrok Setup for Webhook Testing")
    print("=" * 60)
    print("\n1. Install ngrok:")
    print("   brew install ngrok")
    print("\n2. Configure ngrok (one-time):")
    print("   ngrok config add-authtoken YOUR_TOKEN")
    print("\n3. Start ngrok:")
    print("   ngrok http 7002")
    print("\n4. Copy the HTTPS URL and add to Instamojo dashboard:")
    print("   Example: https://abcd1234.ngrok.io/api/payments/webhook")
    print("\n5. Webhook Secret/Salt:")
    print("   4e57693050da4345984d7d1360149032")
    print("=" * 60)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            test_webhook_local()
        elif sys.argv[1] == "verify":
            verify_mac_example()
        elif sys.argv[1] == "ngrok":
            generate_ngrok_command()
        else:
            print("Usage: python test_webhook.py [test|verify|ngrok]")
    else:
        print("Instamojo Webhook Test Script")
        print("\nCommands:")
        print("  python test_webhook.py test    - Test webhook on local server")
        print("  python test_webhook.py verify  - Show MAC verification example")
        print("  python test_webhook.py ngrok   - Show ngrok setup instructions")
