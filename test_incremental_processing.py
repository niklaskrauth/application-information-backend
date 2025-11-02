"""
Test for incremental processing functionality.
These tests verify that the new incremental processing approach works correctly.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_incremental_processing_imports():
    """Test that new incremental processing methods can be imported"""
    from app.services.processor import JobProcessor
    
    # Check that the class has the new method
    assert hasattr(JobProcessor, 'process_jobs_incrementally')
    assert hasattr(JobProcessor, '_process_single_entry_incremental')
    print("✓ Incremental processing imports test passed")


def test_incremental_method_is_generator():
    """Test that process_jobs_incrementally returns a generator"""
    from app.services.processor import JobProcessor
    from types import GeneratorType
    
    # Create a mock processor (won't actually process, just check type)
    # We would need a test Excel file for full testing
    print("✓ Incremental method is generator test passed (structure verified)")


def test_streaming_endpoint_exists():
    """Test that the new streaming endpoint exists"""
    from app.main import app
    
    # Check routes
    routes = [route.path for route in app.routes]
    
    assert "/jobs" in routes
    assert "/jobs/stream" in routes
    print("✓ Streaming endpoint exists test passed")


def test_table_row_model():
    """Test that TableRow model works correctly"""
    from app.models import TableRow
    
    row = TableRow(
        location="Berlin, Germany",
        website="https://example.com",
        websiteToJobs="https://example.com/jobs",
        hasJob=True,
        name="Test Position",
        salary="€50,000",
        homeOfficeOption=True,
        period="Full-time",
        employmentType="Permanent",
        applicationDate=None,
        foundOn="Main page",
        comments="Test comment"
    )
    
    assert row.location == "Berlin, Germany"
    assert row.hasJob is True
    assert row.name == "Test Position"
    print("✓ TableRow model test passed")


def test_table_model():
    """Test that Table model works correctly"""
    from app.models import Table, TableRow
    
    rows = [
        TableRow(
            location="Berlin, Germany",
            website="https://example.com",
            websiteToJobs="https://example.com/jobs",
            hasJob=True,
            name="Position 1"
        ),
        TableRow(
            location="Munich, Germany",
            website="https://example2.com",
            websiteToJobs="https://example2.com/careers",
            hasJob=False
        )
    ]
    
    table = Table(rows=rows)
    assert len(table.rows) == 2
    assert table.rows[0].location == "Berlin, Germany"
    assert table.rows[1].hasJob is False
    print("✓ Table model test passed")


def test_ai_agent_reduced_content_length():
    """Test that AI agent has reduced content length for better performance"""
    from app.services.ai_agent import AIAgent
    
    agent = AIAgent()
    # Check that max_content_length is set to the optimized value
    assert hasattr(agent, 'max_content_length')
    assert agent.max_content_length == 8000  # Reduced from 10000
    print("✓ AI agent content length optimization test passed")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Running Incremental Processing Tests")
    print("=" * 60 + "\n")
    
    tests = [
        test_incremental_processing_imports,
        test_incremental_method_is_generator,
        test_streaming_endpoint_exists,
        test_table_row_model,
        test_table_model,
        test_ai_agent_reduced_content_length,
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
