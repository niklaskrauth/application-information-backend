#!/usr/bin/env python3
"""
Test to verify foundOn field functionality.
"""
import sys
import os
from datetime import date

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models import TableRow


def test_foundOn_field_exists():
    """Test that foundOn field exists in TableRow model"""
    print("\n=== Testing foundOn Field Exists ===")
    
    # Create a TableRow with foundOn field
    row = TableRow(
        location="Test Location",
        website="https://example.com",
        websiteToJobs="https://example.com/jobs",
        hasJob=True,
        name="Test Job",
        foundOn="Main page"
    )
    
    assert hasattr(row, 'foundOn'), "TableRow should have foundOn attribute"
    assert row.foundOn == "Main page", f"Expected 'Main page', got {row.foundOn}"
    print("✓ foundOn field exists and can be set")
    
    return True


def test_foundOn_field_optional():
    """Test that foundOn field is optional"""
    print("\n=== Testing foundOn Field is Optional ===")
    
    # Create a TableRow without foundOn field
    row = TableRow(
        location="Test Location",
        website="https://example.com",
        websiteToJobs="https://example.com/jobs",
        hasJob=True,
        name="Test Job"
    )
    
    assert row.foundOn is None, f"Expected None, got {row.foundOn}"
    print("✓ foundOn field is optional and defaults to None")
    
    return True


def test_foundOn_with_various_sources():
    """Test foundOn field with various source types"""
    print("\n=== Testing foundOn with Various Sources ===")
    
    sources = [
        "Hauptseite",
        "PDF: Stellenanzeige.pdf",
        "Unterseite: https://example.com/jobs/detail",
        "Job detail page",
        None
    ]
    
    for source in sources:
        row = TableRow(
            location="Test Location",
            website="https://example.com",
            websiteToJobs="https://example.com/jobs",
            hasJob=True,
            name="Test Job",
            foundOn=source
        )
        assert row.foundOn == source, f"Expected {source}, got {row.foundOn}"
    
    print(f"✓ foundOn field accepts various source types ({len(sources)} tested)")
    
    return True


def test_foundOn_in_complete_job():
    """Test foundOn field in a complete job entry"""
    print("\n=== Testing foundOn in Complete Job Entry ===")
    
    row = TableRow(
        location="Berlin, Germany",
        website="https://example.com",
        websiteToJobs="https://example.com/careers",
        hasJob=True,
        name="Verwaltungsfachangestellte",
        salary="€35,000 - €45,000",
        homeOfficeOption=True,
        period="Vollzeit",
        employmentType="Unbefristet",
        applicationDate=date(2025, 12, 31),
        foundOn="PDF: Stellenausschreibung_2025.pdf",
        comments="Gute Aufstiegsmöglichkeiten"
    )
    
    assert row.foundOn == "PDF: Stellenausschreibung_2025.pdf"
    assert row.hasJob == True
    assert row.name == "Verwaltungsfachangestellte"
    
    print("✓ foundOn field works correctly in complete job entry")
    print(f"  Job: {row.name}")
    print(f"  Found on: {row.foundOn}")
    print(f"  Location: {row.location}")
    
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Testing foundOn Field Functionality")
    print("=" * 60)
    
    tests = [
        test_foundOn_field_exists,
        test_foundOn_field_optional,
        test_foundOn_with_various_sources,
        test_foundOn_in_complete_job,
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
