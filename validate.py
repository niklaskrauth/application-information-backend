#!/usr/bin/env python3
"""
Validation script to test the application setup and basic functionality.
Run this after installing dependencies to ensure everything is configured correctly.
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    errors = []
    
    try:
        from app.models import WebsiteEntry, ApplicationInfo, ProcessingResponse
        print("  ✓ Models module")
    except Exception as e:
        errors.append(f"Models: {e}")
        print(f"  ✗ Models module: {e}")
    
    try:
        from app.config import settings
        print("  ✓ Config module")
    except Exception as e:
        errors.append(f"Config: {e}")
        print(f"  ✗ Config module: {e}")
    
    try:
        from app.services import ExcelReader, WebScraper, ContentExtractor, AIAgent, ApplicationProcessor
        print("  ✓ Services module")
    except Exception as e:
        errors.append(f"Services: {e}")
        print(f"  ✗ Services module: {e}")
    
    try:
        from app.main import app
        print("  ✓ FastAPI app")
    except Exception as e:
        errors.append(f"FastAPI: {e}")
        print(f"  ✗ FastAPI app: {e}")
    
    return len(errors) == 0, errors


def test_configuration():
    """Test configuration and environment setup"""
    print("\nTesting configuration...")
    
    from app.config import settings
    
    if settings.OPENAI_API_KEY:
        print(f"  ✓ OpenAI API key configured")
    else:
        print(f"  ⚠ OpenAI API key not set (AI features will be disabled)")
    
    print(f"  ✓ App host: {settings.APP_HOST}")
    print(f"  ✓ App port: {settings.APP_PORT}")
    print(f"  ✓ Excel file path: {settings.EXCEL_FILE_PATH}")
    
    return True


def test_excel_file():
    """Test if Excel file exists and can be read"""
    print("\nTesting Excel file...")
    
    from app.config import settings
    
    if os.path.exists(settings.EXCEL_FILE_PATH):
        print(f"  ✓ Excel file exists at {settings.EXCEL_FILE_PATH}")
        
        try:
            from app.services import ExcelReader
            reader = ExcelReader(settings.EXCEL_FILE_PATH)
            entries = reader.read_entries()
            print(f"  ✓ Successfully read {len(entries)} entries from Excel")
            
            for entry in entries:
                print(f"    - {entry.name}: {entry.url}")
            
            return True
        except Exception as e:
            print(f"  ✗ Error reading Excel file: {e}")
            return False
    else:
        print(f"  ⚠ Excel file not found at {settings.EXCEL_FILE_PATH}")
        print(f"    Run: python create_sample_excel.py")
        return False


def test_fastapi():
    """Test FastAPI app creation"""
    print("\nTesting FastAPI app...")
    
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        response = client.get("/")
        
        if response.status_code == 200:
            print("  ✓ FastAPI app is working")
            print(f"    Response: {response.json()}")
            return True
        else:
            print(f"  ✗ FastAPI app returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ Error testing FastAPI: {e}")
        return False


def main():
    """Run all validation tests"""
    print("=" * 60)
    print("Application Information Backend - Validation Tests")
    print("=" * 60)
    print()
    
    all_passed = True
    
    # Test imports
    imports_ok, errors = test_imports()
    if not imports_ok:
        print("\n✗ Import tests failed. Please install dependencies:")
        print("  pip install -r requirements.txt")
        return 1
    
    # Test configuration
    config_ok = test_configuration()
    all_passed = all_passed and config_ok
    
    # Test Excel file
    excel_ok = test_excel_file()
    all_passed = all_passed and excel_ok
    
    # Test FastAPI
    fastapi_ok = test_fastapi()
    all_passed = all_passed and fastapi_ok
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All validation tests passed!")
        print("\nYou can now start the server with:")
        print("  python -m uvicorn app.main:app --reload")
        print("\nOr use the convenience script:")
        print("  ./run.sh")
    else:
        print("⚠ Some tests failed. Please check the errors above.")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
