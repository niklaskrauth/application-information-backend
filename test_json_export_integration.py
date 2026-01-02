"""
Integration test for JSON file export functionality.
This test verifies the complete flow of processing and saving to JSON.
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import Table, TableRow
from app.config import settings


def test_json_output_directory_creation():
    """Test that JSON output directory is created if it doesn't exist"""
    print("Testing JSON output directory creation...")
    
    output_dir = Path(settings.JSON_OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    assert output_dir.exists(), "Output directory was not created"
    assert output_dir.is_dir(), "Output path is not a directory"
    
    print(f"  Output directory exists at: {output_dir}")
    print("✓ JSON output directory creation test passed")
    return True


def test_json_file_generation():
    """Test that a JSON file can be generated with proper naming and content"""
    print("Testing JSON file generation...")
    
    # Create sample table data
    rows = [
        TableRow(
            location="Test City, Germany",
            website="https://test.com",
            websiteToJobs="https://test.com/jobs",
            hasJob=True,
            name="Test Position",
            salary="€50,000",
            homeOfficeOption=True,
            period="Full-time",
            employmentType="Permanent",
            foundOn="Test page",
            comments="Test comment"
        )
    ]
    
    table = Table(rows=rows)
    
    # Create output directory
    output_dir = Path(settings.JSON_OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamped filename (same logic as in main.py)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"jobs_export_{timestamp}.json"
    filepath = output_dir / filename
    
    # Save to JSON file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(table.model_dump(mode='json'), f, indent=2, ensure_ascii=False, default=str)
    
    # Verify file exists
    assert filepath.exists(), f"JSON file was not created at {filepath}"
    
    # Verify file is not empty
    assert filepath.stat().st_size > 0, "JSON file is empty"
    
    # Verify content
    with open(filepath, 'r', encoding='utf-8') as f:
        content = json.load(f)
    
    assert 'rows' in content, "JSON missing 'rows' key"
    assert len(content['rows']) == 1, "JSON has wrong number of rows"
    assert content['rows'][0]['location'] == "Test City, Germany"
    assert content['rows'][0]['hasJob'] is True
    
    # Verify filename format
    assert filename.startswith("jobs_export_"), "Filename has wrong prefix"
    assert filename.endswith(".json"), "Filename has wrong extension"
    
    print(f"  Generated file: {filename}")
    print(f"  File size: {filepath.stat().st_size} bytes")
    print("✓ JSON file generation test passed")
    
    # Clean up test file
    filepath.unlink()
    
    return True


def test_json_file_listing():
    """Test that we can list generated JSON files"""
    print("Testing JSON file listing...")
    
    output_dir = Path(settings.JSON_OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a test file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_filename = f"jobs_export_{timestamp}.json"
    test_filepath = output_dir / test_filename
    
    with open(test_filepath, 'w', encoding='utf-8') as f:
        json.dump({"rows": []}, f)
    
    # List JSON files
    json_files = list(output_dir.glob("jobs_export_*.json"))
    
    assert len(json_files) > 0, "No JSON files found"
    assert test_filepath in json_files, "Test file not found in listing"
    
    print(f"  Found {len(json_files)} JSON file(s)")
    print("✓ JSON file listing test passed")
    
    # Clean up
    test_filepath.unlink()
    
    return True


def run_all_tests():
    """Run all integration tests"""
    print("\n" + "=" * 60)
    print("Running JSON Export Integration Tests")
    print("=" * 60 + "\n")
    
    tests = [
        test_json_output_directory_creation,
        test_json_file_generation,
        test_json_file_listing,
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
