#!/usr/bin/env python3
"""
Setup script for RAG Q&A Chatbot
Helps verify AWS credentials and Bedrock access
"""

import sys
import subprocess
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def check_python_version():
    """Check if Python version is 3.8+"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. Please upgrade Python.")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def check_aws_credentials():
    """Check if AWS credentials are configured"""
    try:
        import boto3
        session = boto3.Session()
        
        if session.get_credentials() is None:
            print("❌ AWS credentials not configured")
            print("   Run: aws configure")
            return False
        
        print("✅ AWS credentials found")
        region = session.region_name or "us-east-1"
        print(f"   Region: {region}")
        return True
    except Exception as e:
        print(f"❌ Error checking AWS credentials: {str(e)}")
        return False


def check_bedrock_access():
    """Check access to Bedrock models"""
    try:
        import boto3
        
        client = boto3.client("bedrock", region_name="us-east-1")
        
        # List available models
        response = client.list_foundation_models()
        models = response.get("modelSummaries", [])
        
        required_models = [
            "amazon.titan-embed-text-v1",
            "anthropic.claude-3-sonnet"
        ]
        
        available = [m["modelId"] for m in models]
        
        print("✅ Bedrock API accessible")
        print(f"   Available models: {len(models)}")
        
        for required in required_models:
            found = any(required in m for m in available)
            status = "✅" if found else "⚠️"
            print(f"   {status} {required}")
        
        return True
    except Exception as e:
        print(f"❌ Error accessing Bedrock: {str(e)}")
        print("   Make sure you have Bedrock model access enabled in AWS Console")
        return False


def install_dependencies():
    """Install Python dependencies"""
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    try:
        print("\n📦 Installing dependencies...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)]
        )
        print("✅ Dependencies installed successfully")
        return True
    except Exception as e:
        print(f"❌ Error installing dependencies: {str(e)}")
        return False


def main():
    """Run setup checks"""
    print("=" * 60)
    print("🤖 RAG Q&A Chatbot - Setup Verification")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("AWS Credentials", check_aws_credentials),
        ("Bedrock Access", check_bedrock_access),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n🔍 Checking {name}...")
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    
    if all(results):
        print(f"✅ All checks passed ({passed}/{total})")
        print("\n📝 Next steps:")
        print("   1. Prepare PDF files")
        print("   2. Run: streamlit run app.py")
        print("   3. Upload PDFs and ask questions!")
    else:
        print(f"⚠️  Some checks failed ({passed}/{total})")
        print("\n❓ Troubleshooting:")
        if not results[0]:
            print("   • Upgrade Python: https://www.python.org/downloads/")
        if not results[1]:
            print("   • Configure AWS: aws configure")
            print("   • Or set environment variables")
        if not results[2]:
            print("   • Enable Bedrock: AWS Console → Bedrock → Model Access")
    
    print("\n" + "=" * 60)
    
    return all(results)


if __name__ == "__main__":
    # Environment variables are loaded from .env file via load_dotenv()
    success = main()
    sys.exit(0 if success else 1)
