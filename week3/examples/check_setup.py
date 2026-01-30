#!/usr/bin/env python3
"""
Pre-flight check script for Gemini + MCP integration
Verifies all prerequisites are met before running
"""

import sys
import os
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print(f"\n{'=' * 70}")
    print(f"  {text}")
    print('=' * 70)

def check_python_version():
    """Check Python version"""
    print("\n1️⃣  Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (Need 3.8+)")
        return False

def check_packages():
    """Check required packages"""
    print("\n2️⃣  Checking required packages...")
    
    packages = {
        'httpx': 'HTTP client',
        'google.generativeai': 'Gemini SDK',
        'dotenv': 'Environment variables'
    }
    
    all_installed = True
    for package, description in packages.items():
        try:
            __import__(package.replace('.', '/'))
            print(f"   ✅ {package:25} ({description})")
        except ImportError:
            print(f"   ❌ {package:25} ({description}) - NOT INSTALLED")
            all_installed = False
    
    if not all_installed:
        print("\n   💡 Install missing packages with:")
        print("      cd week3/examples")
        print("      pip install -r requirements.txt")
    
    return all_installed

def check_env_file():
    """Check .env file"""
    print("\n3️⃣  Checking environment configuration...")
    
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if not env_file.exists():
        print(f"   ❌ .env file not found")
        if env_example.exists():
            print(f"   💡 Copy from template:")
            print(f"      cp .env.example .env")
        return False
    else:
        print(f"   ✅ .env file exists")
        
        # Check if it has the required variables
        with open(env_file) as f:
            content = f.read()
            
        has_gemini = 'GEMINI_API_KEY' in content
        has_mcp_url = 'MCP_SERVER_URL' in content
        has_mcp_key = 'MCP_API_KEY' in content
        
        if has_gemini and 'your-gemini-api-key' not in content:
            print(f"   ✅ GEMINI_API_KEY is set")
        else:
            print(f"   ❌ GEMINI_API_KEY not configured")
            print(f"   💡 Get your API key from: https://makersuite.google.com/app/apikey")
        
        if has_mcp_url:
            print(f"   ✅ MCP_SERVER_URL is set")
        else:
            print(f"   ❌ MCP_SERVER_URL not set")
        
        if has_mcp_key:
            print(f"   ✅ MCP_API_KEY is set")
        else:
            print(f"   ❌ MCP_API_KEY not set")
        
        return has_gemini and has_mcp_url and has_mcp_key

def check_mcp_server():
    """Check if MCP server is reachable"""
    print("\n4️⃣  Checking MCP server connectivity...")
    
    try:
        import httpx
        from dotenv import load_dotenv
        
        load_dotenv()
        server_url = os.getenv('MCP_SERVER_URL', 'http://localhost:8000')
        
        print(f"   🔍 Testing: {server_url}")
        
        try:
            response = httpx.get(f"{server_url}/health", timeout=5.0)
            if response.status_code == 200:
                print(f"   ✅ MCP server is reachable")
                return True
            else:
                print(f"   ❌ MCP server returned status {response.status_code}")
                return False
        except httpx.ConnectError:
            print(f"   ❌ Cannot connect to MCP server")
            print(f"   💡 Make sure the server is running:")
            print(f"      cd week3/server")
            print(f"      python main.py")
            return False
        except httpx.TimeoutException:
            print(f"   ❌ Connection timeout")
            return False
    
    except ImportError:
        print(f"   ⚠️  Cannot test (httpx not installed)")
        return None

def main():
    """Run all checks"""
    
    print_header("🔍 Gemini + MCP Integration Pre-flight Check")
    
    # Change to examples directory if needed
    if Path('examples').exists() and not Path('gemini_integration.py').exists():
        os.chdir('examples')
        print(f"\n📂 Changed directory to: {os.getcwd()}")
    
    # Run checks
    checks = {
        'Python Version': check_python_version(),
        'Required Packages': check_packages(),
        'Environment Config': check_env_file(),
        'MCP Server': check_mcp_server()
    }
    
    # Summary
    print_header("📊 Summary")
    
    passed = sum(1 for v in checks.values() if v is True)
    failed = sum(1 for v in checks.values() if v is False)
    skipped = sum(1 for v in checks.values() if v is None)
    
    print()
    for check_name, result in checks.items():
        if result is True:
            print(f"   ✅ {check_name}")
        elif result is False:
            print(f"   ❌ {check_name}")
        else:
            print(f"   ⚠️  {check_name} (skipped)")
    
    print(f"\n   Total: {passed} passed, {failed} failed, {skipped} skipped")
    
    # Final verdict
    print_header("🎯 Status")
    
    if failed == 0:
        print("\n   ✅ All checks passed! You're ready to go!")
        print("\n   🚀 Run Gemini integration:")
        print("      python gemini_integration.py")
    elif failed <= 2:
        print("\n   ⚠️  Some checks failed, but you might still be able to run")
        print("\n   💡 Fix the issues above and try again")
    else:
        print("\n   ❌ Too many checks failed")
        print("\n   💡 Please fix the issues above before running")
    
    print()
    print('=' * 70)
    print()
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
