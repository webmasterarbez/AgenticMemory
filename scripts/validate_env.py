#!/usr/bin/env python3
"""
Quick validation script to check .env configuration
Run this to verify all required variables are set correctly
"""

import sys
import os
from pathlib import Path

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def check_dotenv():
    """Check if python-dotenv is installed"""
    try:
        from dotenv import load_dotenv
        return True, load_dotenv
    except ImportError:
        return False, None

def validate_url(url, name):
    """Validate a URL"""
    issues = []
    
    if not url:
        issues.append(f"{RED}✗{RESET} {name} is not set")
        return False, issues
    
    if not url.startswith('https://'):
        issues.append(f"{RED}✗{RESET} {name} must start with 'https://' (got: {url[:30]}...)")
        return False, issues
    
    if 'execute-api' not in url:
        issues.append(f"{YELLOW}⚠{RESET} {name} doesn't look like an API Gateway URL")
    
    if url.startswith('https://'):
        issues.append(f"{GREEN}✓{RESET} {name} format is valid")
    
    return True, issues

def validate_key(key, name):
    """Validate a secret key"""
    issues = []
    
    if not key:
        issues.append(f"{RED}✗{RESET} {name} is not set")
        return False, issues
    
    if not key.startswith('wsec_'):
        issues.append(f"{RED}✗{RESET} {name} must start with 'wsec_' (got: {key[:10]}...)")
        return False, issues
    
    if len(key) < 20:
        issues.append(f"{YELLOW}⚠{RESET} {name} seems too short (length: {len(key)})")
    
    issues.append(f"{GREEN}✓{RESET} {name} format is valid")
    return True, issues

def main():
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}  AgenticMemory Configuration Validation{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    # Check dotenv
    has_dotenv, load_dotenv = check_dotenv()
    if not has_dotenv:
        print(f"{RED}✗ python-dotenv not installed{RESET}")
        print(f"  Install with: pip install python-dotenv\n")
        sys.exit(1)
    else:
        print(f"{GREEN}✓ python-dotenv installed{RESET}\n")
    
    # Load .env file (in project root, not scripts folder)
    env_path = Path(__file__).parent.parent / '.env'
    if not env_path.exists():
        print(f"{RED}✗ .env file not found at: {env_path}{RESET}\n")
        sys.exit(1)
    
    print(f"{GREEN}✓ .env file found{RESET}\n")
    load_dotenv(env_path)
    
    # Validate all required variables
    all_valid = True
    
    print(f"{BLUE}Checking API Endpoints...{RESET}")
    print("-" * 60)
    
    # ClientData URL
    url = os.getenv('ELEVENLABS_CLIENT_DATA_URL')
    valid, issues = validate_url(url, 'ELEVENLABS_CLIENT_DATA_URL')
    for issue in issues:
        print(f"  {issue}")
    if not valid:
        all_valid = False
    print()
    
    # Retrieve URL
    url = os.getenv('ELEVENLABS_RETRIEVE_URL')
    valid, issues = validate_url(url, 'ELEVENLABS_RETRIEVE_URL')
    for issue in issues:
        print(f"  {issue}")
    if not valid:
        all_valid = False
    print()
    
    # PostCall URL
    url = os.getenv('ELEVENLABS_POST_CALL_URL')
    valid, issues = validate_url(url, 'ELEVENLABS_POST_CALL_URL')
    for issue in issues:
        print(f"  {issue}")
    if not valid:
        all_valid = False
    print()
    
    print(f"{BLUE}Checking Authentication Keys...{RESET}")
    print("-" * 60)
    
    # Workspace Key
    key = os.getenv('ELEVENLABS_WORKSPACE_KEY')
    valid, issues = validate_key(key, 'ELEVENLABS_WORKSPACE_KEY')
    for issue in issues:
        print(f"  {issue}")
    if not valid:
        all_valid = False
    print()
    
    # HMAC Key
    key = os.getenv('ELEVENLABS_HMAC_KEY')
    valid, issues = validate_key(key, 'ELEVENLABS_HMAC_KEY')
    for issue in issues:
        print(f"  {issue}")
    if not valid:
        all_valid = False
    print()
    
    # Check Mem0 credentials
    print(f"{BLUE}Checking Mem0 Credentials...{RESET}")
    print("-" * 60)
    
    mem0_vars = {
        'MEM0_API_KEY': 'm0-',
        'MEM0_ORG_ID': 'org_',
        'MEM0_PROJECT_ID': 'proj_'
    }
    
    for var, prefix in mem0_vars.items():
        value = os.getenv(var)
        if not value:
            print(f"  {YELLOW}⚠{RESET} {var} is not set")
        elif not value.startswith(prefix):
            print(f"  {YELLOW}⚠{RESET} {var} should start with '{prefix}'")
        else:
            print(f"  {GREEN}✓{RESET} {var} is set")
    print()
    
    # Check S3 bucket
    print(f"{BLUE}Checking S3 Configuration...{RESET}")
    print("-" * 60)
    
    bucket = os.getenv('S3_BUCKET_NAME')
    if not bucket:
        print(f"  {YELLOW}⚠{RESET} S3_BUCKET_NAME is not set")
    else:
        print(f"  {GREEN}✓{RESET} S3_BUCKET_NAME is set: {bucket}")
    print()
    
    # Summary
    print(f"{BLUE}{'='*60}{RESET}")
    if all_valid:
        print(f"{GREEN}✓ All required variables are valid!{RESET}")
        print(f"\n{GREEN}You can now run tests without any manual input:{RESET}")
        print(f"  python scripts/test_clientdata.py")
        print(f"  python scripts/test_production_ready.py")
    else:
        print(f"{RED}✗ Some variables are invalid or missing!{RESET}")
        print(f"\n{YELLOW}Fix the issues above and run this script again.{RESET}")
        sys.exit(1)
    print(f"{BLUE}{'='*60}{RESET}\n")

if __name__ == '__main__':
    main()
