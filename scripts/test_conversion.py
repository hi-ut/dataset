#!/usr/bin/env python3
"""Test conversion with a single manifest"""

import json
from pathlib import Path
from convert_to_v3 import convert_manifest

# Read test manifest
test_manifest_path = Path("docs/iiif/nishikie_hi-0001/manifest.json")
with open(test_manifest_path, 'r', encoding='utf-8') as f:
    v2_manifest = json.load(f)

# Convert
v3_base_url = "https://hi-ut.github.io/dataset/iiif/3"
v3_manifest = convert_manifest(v2_manifest, v3_base_url)

# Print result
print(json.dumps(v3_manifest, ensure_ascii=False, indent=2))
