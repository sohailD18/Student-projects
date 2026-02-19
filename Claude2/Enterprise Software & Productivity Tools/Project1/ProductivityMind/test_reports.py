"""
Simple test script to check if reports API works
Run with: python test_reports.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'productivity_core.settings')
django.setup()

from tasks.views import api_reports_summary
from django.test import RequestFactory
from django.utils import timezone
from datetime import timedelta

print("=== Testing Reports API ===\n")

# Create a mock request
factory = RequestFactory()

# Test with 30 days
request = factory.get('/api/reports/summary/', {'days': '30'})

try:
    print("1. Testing reports API endpoint...")
    response = api_reports_summary(request)
    print(f"   Status Code: {response.status_code}")

    if response.status_code == 200:
        import json
        data = json.loads(response.content)
        print(f"   ✓ Response received successfully!")
        print(f"   - Success: {data.get('success')}")
        if 'report' in data:
            report = data['report']
            print(f"   - Report keys: {list(report.keys())}")
            if 'summary' in report:
                summary = report['summary']
                print(f"   - Summary: {summary}")
    else:
        print(f"   ✗ Error response:")
        print(f"   {response.content.decode()}")

except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Test Complete ===")
