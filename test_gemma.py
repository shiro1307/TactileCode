#!/usr/bin/env python
"""Test Gemma 4 integration by uploading a diagram."""

import requests
import json
from pathlib import Path

# Test diagram upload with explicit mime type
file_path = Path('backend/fixtures/sample_architecture_diagram.png')
print(f'File exists: {file_path.exists()}, Size: {file_path.stat().st_size} bytes')

with open(file_path, 'rb') as f:
    files = {'file': ('diagram.png', f, 'image/png')}
    response = requests.post('http://localhost:8000/api/diagrams', files=files, timeout=120)
    
print(f'Status: {response.status_code}')
if response.status_code == 201:
    data = response.json()
    print('Success! Extracted:')
    print(f'  - Nodes: {len(data.get("nodes", []))}')
    print(f'  - Edges: {len(data.get("edges", []))}')
    print(f'  - ID: {data.get("diagram_id")}')
    print('\nFull response:')
    print(json.dumps(data, indent=2)[:2000])
else:
    print('Error:', response.text)
