#!/usr/bin/env python3
"""
Integration test to verify the JSON serialization fix in the complete flow.
This simulates the actual scenario where data is sent to the frontend callback.
"""
import sys
import os
import json
from datetime import date
from unittest.mock import AsyncMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models import TableRow, Table


def test_json_callback_simulation():
    """
    Simulate the exact scenario from main.py where table.model_dump() is used
    to send data to the frontend callback via httpx.AsyncClient.post()
    """
    print("\n=== Testing JSON Callback Simulation ===")
    
    # Create a table with date fields (simulating real job data)
    rows = [
        TableRow(
            location='Reutlingen',
            website='https://karriere.kreis-reutlingen.de',
            websiteToJobs='https://karriere.kreis-reutlingen.de/jobs',
            hasJob=True,
            name='Sachbearbeiterin im Bereich Grundsicherung',
            salary='A9-A11',
            homeOfficeOption=True,
            period='Vollzeit',
            employmentType='Unbefristet',
            applicationDate=date(2025, 12, 15),
            occupyStart=None,  # Test None date
            foundOn='2025-11-05',
            comments='Test job'
        ),
        TableRow(
            location='Stuttgart',
            website='https://example.com',
            websiteToJobs='https://example.com/careers',
            hasJob=True,
            name='Another position',
            applicationDate=date(2025, 11, 30),
            occupyStart=date(2026, 1, 15),
            foundOn='2025-11-05'
        )
    ]
    
    table = Table(rows=rows)
    
    # This is the exact call from main.py line 112
    table_data = table.model_dump(mode='json')
    
    print(f"✓ Created table with {len(table_data['rows'])} rows")
    
    # Verify the data structure is correct
    assert 'rows' in table_data
    assert len(table_data['rows']) == 2
    print("✓ Table structure is correct")
    
    # Verify dates are serialized as strings
    first_row = table_data['rows'][0]
    assert isinstance(first_row['applicationDate'], str), \
        f"applicationDate should be str, got {type(first_row['applicationDate'])}"
    assert first_row['applicationDate'] == '2025-12-15'
    assert first_row['occupyStart'] is None  # None should remain None
    print("✓ First row dates are correctly serialized")
    
    second_row = table_data['rows'][1]
    assert isinstance(second_row['applicationDate'], str)
    assert isinstance(second_row['occupyStart'], str)
    assert second_row['applicationDate'] == '2025-11-30'
    assert second_row['occupyStart'] == '2026-01-15'
    print("✓ Second row dates are correctly serialized")
    
    # This simulates what httpx.AsyncClient.post() does internally
    # The json parameter triggers json.dumps() on the data
    try:
        json_string = json.dumps(table_data)
        print("✓ Data is JSON serializable (httpx will succeed)")
    except TypeError as e:
        raise AssertionError(f"Data should be JSON serializable for httpx, but got error: {e}")
    
    # Verify it can be parsed back (simulating frontend receiving the data)
    parsed_data = json.loads(json_string)
    assert len(parsed_data['rows']) == 2
    assert parsed_data['rows'][0]['location'] == 'Reutlingen'
    assert parsed_data['rows'][0]['applicationDate'] == '2025-12-15'
    print("✓ Data can be sent and received successfully")
    
    # Verify all fields are present
    expected_fields = [
        'location', 'website', 'websiteToJobs', 'hasJob', 'name', 
        'salary', 'homeOfficeOption', 'period', 'employmentType',
        'applicationDate', 'occupyStart', 'foundOn', 'comments'
    ]
    for field in expected_fields:
        assert field in first_row, f"Field {field} should be present"
    print("✓ All expected fields are present in the serialized data")
    
    return True


def test_error_scenario_without_fix():
    """
    Test what would happen without the fix (using model_dump() without mode='json')
    This demonstrates why the fix was necessary
    """
    print("\n=== Testing Error Scenario Without Fix ===")
    
    row = TableRow(
        location='Test',
        website='http://test.com',
        websiteToJobs='http://test.com/jobs',
        hasJob=True,
        applicationDate=date(2025, 12, 31)
    )
    
    table = Table(rows=[row])
    
    # Without mode='json' (the old broken code)
    table_data_broken = table.model_dump()
    
    # This is what httpx would try to do, and it would fail
    try:
        json.dumps(table_data_broken)
        raise AssertionError("This should have failed without the fix!")
    except TypeError as e:
        assert "Object of type date is not JSON serializable" in str(e)
        print(f"✓ Confirmed old code would fail with: {e}")
    
    return True


def run_all_tests():
    """Run all integration tests"""
    print("\n" + "=" * 60)
    print("Testing JSON Serialization Integration")
    print("=" * 60)
    
    tests = [
        test_json_callback_simulation,
        test_error_scenario_without_fix,
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
