#!/usr/bin/env python3
"""
API Key Generator for Bharat Bytes Genesis Backend
"""

import sys
import os

# Add app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from utils.helpers import generate_api_key


def main():
    print("=" * 60)
    print("Bharat Bytes Genesis - API Key Generator")
    print("=" * 60)
    print()
    
    # Generate a new API key
    api_key = generate_api_key(32)
    
    print("Generated API Key:")
    print("-" * 60)
    print(api_key)
    print("-" * 60)
    print()
    
    print("To use this API key:")
    print("1. Update your .env file with:")
    print(f"   API_KEY={api_key}")
    print()
    print("2. Include it in frontend API requests:")
    print("   Headers: { 'X-API-Key': '" + api_key + "' }")
    print()
    print("3. For testing with curl:")
    print(f"   curl -H 'X-API-Key: {api_key}' http://localhost:8000/health")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
