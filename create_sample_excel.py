#!/usr/bin/env python3
"""
Script to create a sample Excel file for testing the application.
"""
from openpyxl import Workbook

def create_sample_excel():
    wb = Workbook()
    ws = wb.active
    ws.title = 'Applications'

    # Add headers
    ws['A1'] = 'id'
    ws['B1'] = 'name'
    ws['C1'] = 'url'
    ws['D1'] = 'description'

    # Add sample data
    ws['A2'] = 1
    ws['B2'] = 'Example Company'
    ws['C2'] = 'https://www.example.com'
    ws['D2'] = 'A sample company website'

    ws['A3'] = 2
    ws['B3'] = 'Tech Startup'
    ws['C3'] = 'https://www.github.com'
    ws['D3'] = 'Open source platform'

    ws['A4'] = 3
    ws['B4'] = 'Healthcare App'
    ws['C4'] = 'https://www.wikipedia.org'
    ws['D4'] = 'Free encyclopedia'

    wb.save('data/applications.xlsx')
    print('Sample Excel file created successfully at data/applications.xlsx')

if __name__ == '__main__':
    create_sample_excel()
