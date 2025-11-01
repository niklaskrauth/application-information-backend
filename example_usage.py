#!/usr/bin/env python3
"""
Example script demonstrating how to use the Application Information Backend API.
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def check_health():
    """Check if the API is running"""
    print_section("Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        data = response.json()
        
        print(f"Status: {data['status']}")
        print(f"OpenAI Configured: {data['openai_configured']}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure the server is running:")
        print("  python -m uvicorn app.main:app --reload")
        return False


def get_applications():
    """Get list of applications from Excel"""
    print_section("Get Applications List")
    
    try:
        response = requests.get(f"{BASE_URL}/applications")
        response.raise_for_status()
        data = response.json()
        
        print(f"Success: {data['success']}")
        print(f"Count: {data['count']}")
        print("\nApplications:")
        
        for app in data['applications']:
            print(f"  - {app['name']}")
            print(f"    URL: {app['url']}")
            if app.get('description'):
                print(f"    Description: {app['description']}")
            print()
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def process_applications():
    """Process all applications and extract information"""
    print_section("Process Applications")
    
    print("Processing applications... This may take a few minutes.")
    print("(Scraping websites, extracting PDFs/images, and generating AI summaries)")
    
    try:
        response = requests.post(f"{BASE_URL}/process")
        response.raise_for_status()
        data = response.json()
        
        print(f"\nSuccess: {data['success']}")
        print(f"Message: {data['message']}")
        
        if data['success'] and data.get('data'):
            print("\nProcessed Applications:")
            print("-" * 60)
            
            for app in data['data']:
                print(f"\n{app['name']} (ID: {app['id']})")
                print(f"URL: {app['main_url']}")
                
                if app.get('description'):
                    print(f"Description: {app['description']}")
                
                # Links summary
                links = app.get('extracted_links', [])
                pdf_links = [l for l in links if l['link_type'] == 'pdf']
                image_links = [l for l in links if l['link_type'] == 'image']
                webpage_links = [l for l in links if l['link_type'] == 'webpage']
                
                print(f"\nExtracted Links:")
                print(f"  - Webpages: {len(webpage_links)}")
                print(f"  - PDFs: {len(pdf_links)}")
                print(f"  - Images: {len(image_links)}")
                
                # Content summary
                contents = app.get('extracted_contents', [])
                print(f"\nExtracted Contents: {len(contents)} items")
                for content in contents[:3]:  # Show first 3
                    print(f"  - {content['content_type']}: {content['url'][:60]}...")
                
                # AI Summary
                if app.get('summary'):
                    print(f"\nAI Summary:")
                    summary_lines = app['summary'].split('\n')[:5]  # First 5 lines
                    for line in summary_lines:
                        if line.strip():
                            print(f"  {line}")
                    if len(app['summary'].split('\n')) > 5:
                        print("  ...")
                
                print("-" * 60)
            
            # Save full response to file
            output_file = "api_response.json"
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            print(f"\nFull response saved to: {output_file}")
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Run all example API calls"""
    print("\n" + "=" * 60)
    print("  Application Information Backend - API Example")
    print("=" * 60)
    
    # Check if API is running
    if not check_health():
        return 1
    
    # Small delay
    time.sleep(1)
    
    # Get applications list
    if not get_applications():
        return 1
    
    # Ask user if they want to process
    print("\n" + "=" * 60)
    response = input("Do you want to process the applications? (y/n): ").strip().lower()
    
    if response == 'y':
        process_applications()
    else:
        print("\nSkipping processing. You can process later with:")
        print(f"  curl -X POST {BASE_URL}/process")
    
    print("\n" + "=" * 60)
    print("  Example completed!")
    print("=" * 60)
    print("\nNext steps:")
    print("  - View API documentation: http://localhost:8000/docs")
    print("  - Check the api_response.json file for full data")
    print("  - Integrate with your frontend application")
    print("=" * 60 + "\n")
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
