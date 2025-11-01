"""
Basic tests for the application structure and imports.
These tests verify that all components can be imported and basic functionality works.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_models_import():
    """Test that models can be imported"""
    from app.models import (
        WebsiteEntry, 
        ExtractedLink, 
        ExtractedContent, 
        ApplicationInfo, 
        ProcessingResponse
    )
    assert WebsiteEntry is not None
    assert ExtractedLink is not None
    assert ExtractedContent is not None
    assert ApplicationInfo is not None
    assert ProcessingResponse is not None
    print("✓ Models import test passed")


def test_config_import():
    """Test that config can be imported"""
    from app.config import settings
    assert settings is not None
    assert hasattr(settings, 'APP_HOST')
    assert hasattr(settings, 'APP_PORT')
    print("✓ Config import test passed")


def test_services_import():
    """Test that services can be imported"""
    from app.services import (
        ExcelReader,
        WebScraper,
        ContentExtractor,
        AIAgent,
        ApplicationProcessor
    )
    assert ExcelReader is not None
    assert WebScraper is not None
    assert ContentExtractor is not None
    assert AIAgent is not None
    assert ApplicationProcessor is not None
    print("✓ Services import test passed")


def test_main_app_import():
    """Test that FastAPI app can be imported"""
    from app.main import app
    assert app is not None
    print("✓ FastAPI app import test passed")


def test_website_entry_creation():
    """Test creating a WebsiteEntry model"""
    from app.models import WebsiteEntry
    
    entry = WebsiteEntry(
        id=1,
        name="Test",
        url="https://example.com",
        description="Test description"
    )
    assert entry.id == 1
    assert entry.name == "Test"
    assert str(entry.url) == "https://example.com/"
    assert entry.description == "Test description"
    print("✓ WebsiteEntry creation test passed")


def test_extracted_link_creation():
    """Test creating an ExtractedLink model"""
    from app.models import ExtractedLink
    
    link = ExtractedLink(
        url="https://example.com/page",
        link_type="webpage",
        title="Test Page"
    )
    assert link.url == "https://example.com/page"
    assert link.link_type == "webpage"
    assert link.title == "Test Page"
    print("✓ ExtractedLink creation test passed")


def test_processing_response_creation():
    """Test creating a ProcessingResponse model"""
    from app.models import ProcessingResponse
    
    response = ProcessingResponse(
        success=True,
        message="Test message",
        data=None,
        error=None
    )
    assert response.success is True
    assert response.message == "Test message"
    assert response.data is None
    assert response.error is None
    print("✓ ProcessingResponse creation test passed")


def test_web_scraper_initialization():
    """Test WebScraper can be initialized"""
    from app.services import WebScraper
    
    scraper = WebScraper(timeout=30)
    assert scraper is not None
    assert scraper.timeout == 30
    print("✓ WebScraper initialization test passed")


def test_ai_agent_initialization():
    """Test AIAgent can be initialized"""
    from app.services import AIAgent
    
    agent = AIAgent()
    assert agent is not None
    # Agent may be disabled if no API key, that's okay
    print("✓ AIAgent initialization test passed")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Running Basic Tests")
    print("=" * 60 + "\n")
    
    tests = [
        test_models_import,
        test_config_import,
        test_services_import,
        test_main_app_import,
        test_website_entry_creation,
        test_extracted_link_creation,
        test_processing_response_creation,
        test_web_scraper_initialization,
        test_ai_agent_initialization,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
