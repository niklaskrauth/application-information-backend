"""
Test for JSON export functionality.
This test verifies that the application can save job processing results to JSON files.
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import Table, TableRow
from app.config import settings


def test_json_export_functionality():
    """Test that Table can be serialized to JSON and saved to file"""
    print("Testing JSON export functionality...")
    
    # Create sample data
    rows = [
        TableRow(
            location="Berlin, Germany",
            website="https://example.com",
            websiteToJobs="https://example.com/jobs",
            hasJob=True,
            name="Software Engineer",
            salary="€60,000 - €80,000",
            homeOfficeOption=True,
            period="Full-time",
            employmentType="Permanent",
            foundOn="Main page",
            comments="Great opportunity"
        ),
        TableRow(
            location="Munich, Germany",
            website="https://another.com",
            websiteToJobs="https://another.com/careers",
            hasJob=False,
            comments="No positions available"
        )
    ]
    
    table = Table(rows=rows)
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save to JSON file
        output_file = Path(temp_dir) / "test_export.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(table.model_dump(mode='json'), f, indent=2, ensure_ascii=False, default=str)
        
        # Verify file was created
        assert output_file.exists(), "JSON file was not created"
        
        # Read back and verify content
        with open(output_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        assert 'rows' in loaded_data, "JSON missing 'rows' key"
        assert len(loaded_data['rows']) == 2, "JSON has wrong number of rows"
        
        # Verify first row data
        first_row = loaded_data['rows'][0]
        assert first_row['location'] == "Berlin, Germany"
        assert first_row['hasJob'] is True
        assert first_row['name'] == "Software Engineer"
        assert first_row['salary'] == "€60,000 - €80,000"
        
        # Verify second row data
        second_row = loaded_data['rows'][1]
        assert second_row['location'] == "Munich, Germany"
        assert second_row['hasJob'] is False
        
        print("✓ JSON export functionality test passed")
        return True


def test_output_directory_config():
    """Test that output directory config exists"""
    print("Testing output directory configuration...")
    
    assert hasattr(settings, 'JSON_OUTPUT_DIR'), "Settings missing JSON_OUTPUT_DIR"
    assert settings.JSON_OUTPUT_DIR is not None, "JSON_OUTPUT_DIR is None"
    
    print(f"  Output directory configured as: {settings.JSON_OUTPUT_DIR}")
    print("✓ Output directory configuration test passed")
    return True


def run_all_tests():
    """Run all JSON export tests"""
    print("\n" + "=" * 60)
    print("Running JSON Export Tests")
    print("=" * 60 + "\n")
    
    tests = [
        test_output_directory_config,
        test_json_export_functionality,
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
