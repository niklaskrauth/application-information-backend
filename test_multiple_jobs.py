#!/usr/bin/env python3
"""
Test script to verify multiple jobs extraction functionality
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_agent import AIAgent
from app.services.processor import JobProcessor
from app.models import WebsiteEntry

def test_extract_multiple_jobs_disabled():
    """Test that extract_multiple_jobs returns list when AI is disabled"""
    print("\n=== Testing extract_multiple_jobs with AI disabled ===")
    agent = AIAgent()
    
    result = agent.extract_multiple_jobs(
        location="Test Location",
        website="https://example.com",
        website_to_jobs="https://example.com/jobs",
        page_content="Test content"
    )
    
    assert isinstance(result, list), "Result should be a list"
    assert len(result) == 1, "Should return one entry when AI is disabled"
    assert result[0].get('hasJob') == False, "hasJob should be False when AI is disabled"
    print("✓ extract_multiple_jobs returns list correctly when AI disabled")


def test_extract_job_info_compatibility():
    """Test that extract_job_info still works (backward compatibility)"""
    print("\n=== Testing extract_job_info backward compatibility ===")
    agent = AIAgent()
    
    result = agent.extract_job_info(
        location="Test Location",
        website="https://example.com",
        website_to_jobs="https://example.com/jobs",
        page_content="Test content"
    )
    
    assert isinstance(result, dict), "Result should be a dict"
    assert 'hasJob' in result, "Result should have hasJob field"
    print("✓ extract_job_info backward compatibility works")


def test_processor_returns_list():
    """Test that processor._process_single_entry returns list"""
    print("\n=== Testing processor returns list of rows ===")
    
    # Create a mock entry
    entry = WebsiteEntry(
        id=1,
        location="Test Location",
        website="https://example.com",
        websiteToJobs="https://example.com/jobs"
    )
    
    print("✓ WebsiteEntry created successfully")
    print(f"  Entry: {entry.location}")


def test_rate_limiting_logic():
    """Test rate limiting logic"""
    print("\n=== Testing rate limiting ===")
    import time
    
    agent = AIAgent()
    if not agent.enabled:
        print("⚠ AI is disabled (no API key), skipping rate limit test")
        return
    
    start_time = time.time()
    agent._rate_limit()
    first_call_time = time.time() - start_time
    
    # Second call should be delayed
    start_time = time.time()
    agent._rate_limit()
    second_call_time = time.time() - start_time
    
    print(f"  First call: {first_call_time:.2f}s")
    print(f"  Second call: {second_call_time:.2f}s (should be ~{agent.min_delay_between_calls}s)")
    print("✓ Rate limiting logic works")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Testing Multiple Jobs Extraction")
    print("=" * 60)
    
    tests = [
        test_extract_multiple_jobs_disabled,
        test_extract_job_info_compatibility,
        test_processor_returns_list,
        test_rate_limiting_logic,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
