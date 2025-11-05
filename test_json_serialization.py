#!/usr/bin/env python3
"""
Test to verify JSON serialization of date objects in TableRow model.
This test ensures that the fix for "Object of type date is not JSON serializable" works.
"""
import sys
import os
import json
from datetime import date

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models import TableRow, Table


def test_table_row_json_serialization():
    """Test that TableRow with date fields can be JSON serialized"""
    print("\n=== Testing TableRow JSON Serialization ===")
    
    # Create a sample row with dates
    row = TableRow(
        location='Test Location',
        website='http://test.com',
        websiteToJobs='http://test.com/jobs',
        hasJob=True,
        name='Test Job Position',
        salary='50000-60000 EUR',
        homeOfficeOption=True,
        period='Vollzeit',
        employmentType='Unbefristet',
        applicationDate=date(2025, 12, 31),
        occupyStart=date(2026, 1, 1),
        foundOn='2025-11-05',
        comments='Test comment'
    )
    
    # Test individual row serialization
    row_dict = row.model_dump(mode='json')
    
    # Verify dates are strings
    assert isinstance(row_dict['applicationDate'], str), \
        f"applicationDate should be str, got {type(row_dict['applicationDate'])}"
    assert row_dict['applicationDate'] == '2025-12-31', \
        f"applicationDate should be '2025-12-31', got {row_dict['applicationDate']}"
    
    assert isinstance(row_dict['occupyStart'], str), \
        f"occupyStart should be str, got {type(row_dict['occupyStart'])}"
    assert row_dict['occupyStart'] == '2026-01-01', \
        f"occupyStart should be '2026-01-01', got {row_dict['occupyStart']}"
    
    print("✓ Row dates are serialized to strings")
    
    # Verify it's JSON serializable
    try:
        json_str = json.dumps(row_dict)
        print("✓ Row is JSON serializable")
    except TypeError as e:
        raise AssertionError(f"Row should be JSON serializable, but got error: {e}")
    
    # Parse back and verify
    parsed = json.loads(json_str)
    assert parsed['applicationDate'] == '2025-12-31'
    assert parsed['occupyStart'] == '2026-01-01'
    print("✓ JSON round-trip successful")
    
    return True


def test_table_json_serialization():
    """Test that Table with multiple TableRows can be JSON serialized"""
    print("\n=== Testing Table JSON Serialization ===")
    
    # Create multiple rows with different date scenarios
    rows = [
        TableRow(
            location='Location 1',
            website='http://test1.com',
            websiteToJobs='http://test1.com/jobs',
            hasJob=True,
            name='Job 1',
            applicationDate=date(2025, 11, 30),
            occupyStart=date(2025, 12, 15)
        ),
        TableRow(
            location='Location 2',
            website='http://test2.com',
            websiteToJobs='http://test2.com/jobs',
            hasJob=True,
            name='Job 2',
            applicationDate=None,  # Test None dates
            occupyStart=None
        ),
        TableRow(
            location='Location 3',
            website='http://test3.com',
            websiteToJobs='http://test3.com/jobs',
            hasJob=False,  # Test without job
            applicationDate=None,
            occupyStart=None
        )
    ]
    
    table = Table(rows=rows)
    
    # Test table serialization with mode='json'
    table_dict = table.model_dump(mode='json')
    
    # Verify dates in first row
    assert isinstance(table_dict['rows'][0]['applicationDate'], str)
    assert table_dict['rows'][0]['applicationDate'] == '2025-11-30'
    print("✓ First row dates are serialized correctly")
    
    # Verify None dates in second row
    assert table_dict['rows'][1]['applicationDate'] is None
    assert table_dict['rows'][1]['occupyStart'] is None
    print("✓ None dates are handled correctly")
    
    # Verify it's JSON serializable
    try:
        json_str = json.dumps(table_dict)
        print("✓ Table is JSON serializable")
    except TypeError as e:
        raise AssertionError(f"Table should be JSON serializable, but got error: {e}")
    
    # Parse back and verify
    parsed = json.loads(json_str)
    assert len(parsed['rows']) == 3
    assert parsed['rows'][0]['applicationDate'] == '2025-11-30'
    assert parsed['rows'][1]['applicationDate'] is None
    print("✓ JSON round-trip successful for table with multiple rows")
    
    return True


def test_model_dump_default_mode():
    """Test that model_dump() without mode parameter still uses date objects"""
    print("\n=== Testing model_dump() Default Behavior ===")
    
    row = TableRow(
        location='Test',
        website='http://test.com',
        websiteToJobs='http://test.com/jobs',
        hasJob=True,
        applicationDate=date(2025, 12, 31)
    )
    
    # Without mode parameter, dates should remain as date objects
    dump_default = row.model_dump()
    assert isinstance(dump_default['applicationDate'], date), \
        "Default model_dump() should keep dates as date objects"
    print("✓ Default model_dump() keeps dates as date objects")
    
    # This should NOT be JSON serializable
    try:
        json.dumps(dump_default)
        raise AssertionError("Default model_dump() should NOT be JSON serializable")
    except TypeError:
        print("✓ Default model_dump() is not JSON serializable (as expected)")
    
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Testing JSON Serialization of Date Objects")
    print("=" * 60)
    
    tests = [
        test_table_row_json_serialization,
        test_table_json_serialization,
        test_model_dump_default_mode,
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
