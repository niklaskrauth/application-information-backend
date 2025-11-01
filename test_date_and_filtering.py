#!/usr/bin/env python3
"""
Test to verify date parsing and job filtering functionality.
"""
import sys
import os
from datetime import date

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.processor import JobProcessor
from app.services.ai_agent import EXCLUDED_JOB_TYPES, INCLUDED_JOB_TYPES, EXCLUDED_QUALIFICATIONS


def test_date_parsing():
    """Test that date parsing works for various formats"""
    print("\n=== Testing Date Parsing ===")
    
    # Test ISO format (YYYY-MM-DD)
    result = JobProcessor._parse_date("2025-12-31")
    assert result == date(2025, 12, 31), f"Expected 2025-12-31, got {result}"
    print("✓ ISO format (YYYY-MM-DD) parsed correctly")
    
    # Test German format (DD.MM.YYYY)
    result = JobProcessor._parse_date("31.12.2025")
    assert result == date(2025, 12, 31), f"Expected 2025-12-31, got {result}"
    print("✓ German format (DD.MM.YYYY) parsed correctly")
    
    # Test slash format (DD/MM/YYYY)
    result = JobProcessor._parse_date("31/12/2025")
    assert result == date(2025, 12, 31), f"Expected 2025-12-31, got {result}"
    print("✓ Slash format (DD/MM/YYYY) parsed correctly")
    
    # Test None input
    result = JobProcessor._parse_date(None)
    assert result is None, f"Expected None, got {result}"
    print("✓ None input handled correctly")
    
    # Test empty string
    result = JobProcessor._parse_date("")
    assert result is None, f"Expected None, got {result}"
    print("✓ Empty string handled correctly")
    
    # Test invalid date
    result = JobProcessor._parse_date("not a date")
    assert result is None, f"Expected None for invalid date, got {result}"
    print("✓ Invalid date handled correctly")
    
    return True


def test_excluded_job_types():
    """Test that excluded job types list is comprehensive"""
    print("\n=== Testing Excluded Job Types ===")
    
    # Check that all variations are included
    assert "Auszubildung" in EXCLUDED_JOB_TYPES
    assert "Azubi" in EXCLUDED_JOB_TYPES
    assert "Praktikum" in EXCLUDED_JOB_TYPES
    assert "Praktikant" in EXCLUDED_JOB_TYPES
    assert "Studium" in EXCLUDED_JOB_TYPES
    assert "Student" in EXCLUDED_JOB_TYPES
    assert "Studentische" in EXCLUDED_JOB_TYPES
    
    print(f"✓ {len(EXCLUDED_JOB_TYPES)} excluded job types defined")
    print(f"  Types: {', '.join(EXCLUDED_JOB_TYPES)}")
    
    return True


def test_included_job_types():
    """Test that included job types list contains administrative roles"""
    print("\n=== Testing Included Job Types ===")
    
    # Check key administrative roles are included
    assert "Verwaltung" in INCLUDED_JOB_TYPES
    assert "Sachbearbeiter" in INCLUDED_JOB_TYPES
    assert "Sekretariatskraft" in INCLUDED_JOB_TYPES
    assert "Bürokraft" in INCLUDED_JOB_TYPES
    
    print(f"✓ {len(INCLUDED_JOB_TYPES)} included job types defined")
    print(f"  Administrative roles: {', '.join(INCLUDED_JOB_TYPES[:5])}...")
    
    return True


def test_excluded_qualifications():
    """Test that excluded qualifications list filters higher education"""
    print("\n=== Testing Excluded Qualifications ===")
    
    # Check that university-level qualifications are excluded
    assert "Bachelor" in EXCLUDED_QUALIFICATIONS
    assert "Master" in EXCLUDED_QUALIFICATIONS
    assert "Diplom" in EXCLUDED_QUALIFICATIONS
    assert "Hochschulabschluss" in EXCLUDED_QUALIFICATIONS
    assert "Universität" in EXCLUDED_QUALIFICATIONS
    # Note: "Studium" is in EXCLUDED_JOB_TYPES, not here to avoid duplication
    
    print(f"✓ {len(EXCLUDED_QUALIFICATIONS)} excluded qualification terms defined")
    print(f"  Terms: {', '.join(EXCLUDED_QUALIFICATIONS)}")
    
    return True


def test_prompt_includes_filters():
    """Test that the AI prompt would include all filter criteria"""
    print("\n=== Testing AI Prompt Filter Criteria ===")
    
    # Verify the lists are populated
    assert len(EXCLUDED_JOB_TYPES) > 0, "EXCLUDED_JOB_TYPES should not be empty"
    assert len(INCLUDED_JOB_TYPES) > 0, "INCLUDED_JOB_TYPES should not be empty"
    assert len(EXCLUDED_QUALIFICATIONS) > 0, "EXCLUDED_QUALIFICATIONS should not be empty"
    
    print("✓ All filter criteria lists are populated")
    print(f"  - {len(EXCLUDED_JOB_TYPES)} excluded job types")
    print(f"  - {len(INCLUDED_JOB_TYPES)} included job types")
    print(f"  - {len(EXCLUDED_QUALIFICATIONS)} excluded qualifications")
    
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Testing Date Parsing and Job Filtering")
    print("=" * 60)
    
    tests = [
        test_date_parsing,
        test_excluded_job_types,
        test_included_job_types,
        test_excluded_qualifications,
        test_prompt_includes_filters,
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
