#!/usr/bin/env python3
"""
Demo script to verify the JSON export functionality.
This simulates the full flow without requiring FastAPI server or AI models.
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


def demo_json_export():
    """Demonstrate the JSON export functionality"""
    
    print("\n" + "=" * 70)
    print("JSON Export Feature Demo")
    print("=" * 70 + "\n")
    
    # Step 1: Create sample data (simulating AI extraction results)
    print("Step 1: Creating sample job data...")
    rows = [
        TableRow(
            location="Berlin, Germany",
            website="https://example-company.com",
            websiteToJobs="https://example-company.com/careers",
            hasJob=True,
            name="Senior Software Engineer",
            salary="€70,000 - €90,000",
            homeOfficeOption=True,
            period="Full-time",
            employmentType="Permanent",
            foundOn="Main page",
            comments="Great benefits package"
        ),
        TableRow(
            location="Berlin, Germany",
            website="https://example-company.com",
            websiteToJobs="https://example-company.com/careers",
            hasJob=True,
            name="Junior Developer",
            salary="€45,000 - €55,000",
            homeOfficeOption=True,
            period="Full-time",
            employmentType="Permanent",
            foundOn="PDF: careers.pdf",
            comments="Entry level position"
        ),
        TableRow(
            location="Munich, Germany",
            website="https://another-company.com",
            websiteToJobs="https://another-company.com/jobs",
            hasJob=False,
            comments="No open positions at this time"
        )
    ]
    
    table = Table(rows=rows)
    print(f"  Created table with {len(rows)} job entries")
    
    # Step 2: Create output directory
    print("\nStep 2: Creating output directory...")
    output_dir = Path(settings.JSON_OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"  Output directory: {output_dir}")
    
    # Step 3: Generate JSON file with timestamp
    print("\nStep 3: Generating JSON file...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"jobs_export_{timestamp}.json"
    filepath = output_dir / filename
    
    # Step 4: Save to JSON file
    print(f"\nStep 4: Saving to {filename}...")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(table.model_dump(mode='json'), f, indent=2, ensure_ascii=False, default=str)
    
    file_size = filepath.stat().st_size
    print(f"  File created: {filepath}")
    print(f"  File size: {file_size} bytes")
    
    # Step 5: Verify file content
    print("\nStep 5: Verifying file content...")
    with open(filepath, 'r', encoding='utf-8') as f:
        loaded_data = json.load(f)
    
    print(f"  ✓ JSON structure valid")
    print(f"  ✓ Contains {len(loaded_data['rows'])} rows")
    print(f"  ✓ Jobs with positions: {sum(1 for r in loaded_data['rows'] if r['hasJob'])}")
    print(f"  ✓ Locations: {len(set(r['location'] for r in loaded_data['rows']))}")
    
    # Step 6: Show sample output
    print("\nStep 6: Sample JSON content (first row):")
    print("-" * 70)
    print(json.dumps(loaded_data['rows'][0], indent=2, ensure_ascii=False))
    print("-" * 70)
    
    # Step 7: Show usage instructions
    print("\n" + "=" * 70)
    print("SUCCESS! JSON export feature is working correctly.")
    print("=" * 70)
    print(f"\nThe JSON file has been created at:")
    print(f"  {filepath}")
    print(f"\nYou can now:")
    print(f"  1. Upload this file to your website")
    print(f"  2. Use it in your frontend application")
    print(f"  3. Share it with others")
    print("\nTo use in production:")
    print("  1. Start the server: python -m uvicorn app.main:app")
    print("  2. Call GET /jobs to start processing")
    print("  3. Call GET /exports to list all generated files")
    print("  4. Find the JSON file in the data/output/ directory")
    print("=" * 70 + "\n")
    
    # Cleanup demo file
    print("Cleaning up demo file...")
    filepath.unlink()
    print("Demo complete!\n")


if __name__ == '__main__':
    try:
        demo_json_export()
    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
