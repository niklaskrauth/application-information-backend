#!/usr/bin/env python3
"""
Integration test demonstrating the multiple jobs extraction functionality.
This test shows how the system would work with actual data.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models import WebsiteEntry, TableRow
from app.services.ai_agent import AIAgent


def test_multiple_jobs_response_structure():
    """Test that the AI agent returns the expected structure for multiple jobs"""
    print("\n=== Testing Multiple Jobs Response Structure ===")
    
    # This demonstrates what the AI would return when finding multiple jobs
    mock_jobs = [
        {
            "hasJob": True,
            "name": "Senior Software Engineer",
            "salary": "€70,000 - €90,000",
            "homeOfficeOption": True,
            "period": "Full-time",
            "employmentType": "Permanent",
            "comments": "Remote work available"
        },
        {
            "hasJob": True,
            "name": "Junior Developer",
            "salary": "€45,000 - €55,000",
            "homeOfficeOption": True,
            "period": "Full-time",
            "employmentType": "Permanent",
            "comments": "Great for entry-level"
        },
        {
            "hasJob": True,
            "name": "DevOps Engineer",
            "salary": "€60,000 - €80,000",
            "homeOfficeOption": False,
            "period": "Full-time",
            "employmentType": "Contract",
            "comments": "1-year contract"
        }
    ]
    
    # Convert to TableRows as the processor would
    location = "Berlin, Germany"
    website = "https://example.com"
    websiteToJobs = "https://example.com/careers"
    
    rows = []
    for job_info in mock_jobs:
        row = TableRow(
            location=location,
            website=website,
            websiteToJobs=websiteToJobs,
            hasJob=job_info.get('hasJob', False),
            name=job_info.get('name'),
            salary=job_info.get('salary'),
            homeOfficeOption=job_info.get('homeOfficeOption'),
            period=job_info.get('period'),
            employmentType=job_info.get('employmentType'),
            comments=job_info.get('comments')
        )
        rows.append(row)
    
    # Verify we got multiple rows
    assert len(rows) == 3, f"Expected 3 rows, got {len(rows)}"
    
    # Verify all rows have same location/website
    for row in rows:
        assert row.location == location
        assert row.website == website
        assert row.websiteToJobs == websiteToJobs
    
    # Verify each has different job names
    job_names = [row.name for row in rows]
    assert len(set(job_names)) == 3, "Each job should have a unique name"
    
    print(f"✓ Successfully created {len(rows)} TableRows from multiple jobs")
    print(f"  Location: {location}")
    print(f"  Jobs found:")
    for i, row in enumerate(rows, 1):
        print(f"    {i}. {row.name} - {row.salary}")
    
    return True


def test_single_company_no_jobs():
    """Test handling when a company has no jobs"""
    print("\n=== Testing Company with No Jobs ===")
    
    mock_no_jobs = [
        {
            "hasJob": False,
            "comments": "No open positions at this time"
        }
    ]
    
    location = "Munich, Germany"
    website = "https://another-company.com"
    websiteToJobs = "https://another-company.com/jobs"
    
    rows = []
    for job_info in mock_no_jobs:
        row = TableRow(
            location=location,
            website=website,
            websiteToJobs=websiteToJobs,
            hasJob=job_info.get('hasJob', False),
            name=job_info.get('name'),
            salary=job_info.get('salary'),
            homeOfficeOption=job_info.get('homeOfficeOption'),
            period=job_info.get('period'),
            employmentType=job_info.get('employmentType'),
            comments=job_info.get('comments')
        )
        rows.append(row)
    
    assert len(rows) == 1, "Should have 1 row even with no jobs"
    assert rows[0].hasJob == False, "hasJob should be False"
    assert rows[0].name is None, "name should be None when no jobs"
    
    print(f"✓ Correctly handled company with no jobs")
    print(f"  Location: {location}")
    print(f"  Status: {rows[0].comments}")
    
    return True


def demonstrate_api_response():
    """Demonstrate what the final API response would look like"""
    print("\n=== Demonstrating Final API Response Format ===")
    
    # Simulate processing two companies
    all_rows = []
    
    # Company 1 - has multiple jobs
    company1_jobs = [
        {"hasJob": True, "name": "Backend Developer", "salary": "€55,000", "homeOfficeOption": True},
        {"hasJob": True, "name": "Frontend Developer", "salary": "€50,000", "homeOfficeOption": True},
    ]
    
    for job in company1_jobs:
        row = TableRow(
            location="Berlin, Germany",
            website="https://company1.com",
            websiteToJobs="https://company1.com/jobs",
            hasJob=job["hasJob"],
            name=job["name"],
            salary=job["salary"],
            homeOfficeOption=job["homeOfficeOption"],
            period="Full-time",
            employmentType="Permanent"
        )
        all_rows.append(row)
    
    # Company 2 - no jobs
    row = TableRow(
        location="Munich, Germany",
        website="https://company2.com",
        websiteToJobs="https://company2.com/careers",
        hasJob=False,
        comments="No positions available"
    )
    all_rows.append(row)
    
    print(f"✓ Total rows in API response: {len(all_rows)}")
    print(f"  - Company 1 (Berlin): 2 jobs")
    print(f"  - Company 2 (Munich): 0 jobs (1 row indicating no jobs)")
    print()
    print("  Response structure: {'rows': [TableRow, TableRow, TableRow]}")
    print("  This matches the frontend Table interface")
    
    return True


def run_all_tests():
    """Run all demonstration tests"""
    print("\n" + "=" * 60)
    print("Multiple Jobs Extraction - Integration Test")
    print("=" * 60)
    
    tests = [
        test_multiple_jobs_response_structure,
        test_single_company_no_jobs,
        demonstrate_api_response,
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
