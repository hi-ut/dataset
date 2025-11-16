#!/usr/bin/env python3
"""
IIIF Presentation API v2 to v3 converter
Converts manifest.json files from v2 to v3 format
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List


def convert_metadata(v2_metadata: List[Dict]) -> List[Dict]:
    """Convert metadata from v2 to v3 format"""
    v3_metadata = []
    for item in v2_metadata:
        v3_metadata.append({
            "label": {"ja": [item["label"]]},
            "value": {"ja": [item["value"]]}
        })
    return v3_metadata


def convert_thumbnail(v2_thumbnail: Dict) -> List[Dict]:
    """Convert thumbnail from v2 to v3 format"""
    if not v2_thumbnail:
        return []

    return [{
        "id": v2_thumbnail["@id"],
        "type": "Image",
        "format": v2_thumbnail.get("format", "image/jpeg"),
        "width": v2_thumbnail.get("width"),
        "height": v2_thumbnail.get("height")
    }]


def convert_canvas(v2_canvas: Dict) -> Dict:
    """Convert canvas from v2 to v3 format"""
    v3_canvas = {
        "id": v2_canvas["@id"].replace("/canvas/", "/canvas/"),
        "type": "Canvas",
        "label": {"ja": [v2_canvas.get("label", "")]},
        "height": v2_canvas["height"],
        "width": v2_canvas["width"],
        "items": []
    }

    # Convert images to annotation page
    if "images" in v2_canvas and v2_canvas["images"]:
        annotations = []
        for v2_image in v2_canvas["images"]:
            resource = v2_image.get("resource", {})
            annotation = {
                "id": v2_image["@id"],
                "type": "Annotation",
                "motivation": "painting",
                "body": {
                    "id": resource["@id"],
                    "type": "Image",
                    "format": resource.get("format", "image/jpeg"),
                    "height": resource.get("height"),
                    "width": resource.get("width")
                },
                "target": v3_canvas["id"]
            }
            annotations.append(annotation)

        v3_canvas["items"] = [{
            "id": v2_canvas["@id"] + "/page",
            "type": "AnnotationPage",
            "items": annotations
        }]

    # Convert thumbnail
    if "thumbnail" in v2_canvas:
        v3_canvas["thumbnail"] = convert_thumbnail(v2_canvas["thumbnail"])

    return v3_canvas


def convert_manifest(v2_manifest: Dict, v3_base_url: str) -> Dict:
    """Convert entire manifest from v2 to v3 format"""

    # Extract ID and create v3 ID
    v2_id = v2_manifest["@id"]
    manifest_name = v2_id.split("/")[-2]  # e.g., nishikie_hi-0001
    v3_id = f"{v3_base_url}/{manifest_name}/manifest.json"

    v3_manifest = {
        "@context": "http://iiif.io/api/presentation/3/context.json",
        "id": v3_id,
        "type": "Manifest",
        "label": {"ja": [v2_manifest.get("label", "")]},
    }

    # Add metadata
    if "metadata" in v2_manifest:
        v3_manifest["metadata"] = convert_metadata(v2_manifest["metadata"])

    # Add summary (from description if exists)
    if "description" in v2_manifest:
        v3_manifest["summary"] = {"ja": [v2_manifest["description"]]}

    # Add requiredStatement (attribution)
    if "attribution" in v2_manifest:
        v3_manifest["requiredStatement"] = {
            "label": {"ja": ["提供"]},
            "value": {"ja": [v2_manifest["attribution"]]}
        }

    # Add rights
    if "license" in v2_manifest:
        v3_manifest["rights"] = v2_manifest["license"]

    # Add logo as provider
    if "logo" in v2_manifest:
        v3_manifest["provider"] = [{
            "id": "https://www.hi.u-tokyo.ac.jp/",
            "type": "Agent",
            "label": {"ja": ["東京大学史料編纂所"]},
            "logo": [{
                "id": v2_manifest["logo"],
                "type": "Image",
                "format": "image/x-icon"
            }]
        }]

    # Add thumbnail
    if "thumbnail" in v2_manifest:
        v3_manifest["thumbnail"] = convert_thumbnail(v2_manifest["thumbnail"])

    # Add viewingDirection
    if "viewingDirection" in v2_manifest:
        v3_manifest["viewingDirection"] = v2_manifest["viewingDirection"]

    # Convert sequences to items (canvases)
    if "sequences" in v2_manifest and v2_manifest["sequences"]:
        sequence = v2_manifest["sequences"][0]
        if "canvases" in sequence:
            v3_manifest["items"] = [
                convert_canvas(canvas) for canvas in sequence["canvases"]
            ]

    return v3_manifest


def main():
    # Set paths
    base_dir = Path(__file__).parent / "docs" / "iiif"
    v3_dir = base_dir / "3"

    # Get v3 base URL
    v3_base_url = "https://hi-ut.github.io/dataset/iiif/3"

    # Find all manifest.json files (excluding v3 directory)
    manifest_files = []
    for manifest_path in base_dir.rglob("manifest.json"):
        # Skip if in v3 directory
        if "/3/" in str(manifest_path):
            continue
        manifest_files.append(manifest_path)

    print(f"Found {len(manifest_files)} manifest files to convert")

    converted_count = 0
    error_count = 0

    for manifest_path in manifest_files:
        try:
            # Read v2 manifest
            with open(manifest_path, 'r', encoding='utf-8') as f:
                v2_manifest = json.load(f)

            # Get manifest folder name (e.g., nishikie_hi-0001)
            manifest_folder = manifest_path.parent.name

            # Create output directory
            output_dir = v3_dir / manifest_folder
            output_dir.mkdir(parents=True, exist_ok=True)

            # Convert manifest
            v3_manifest = convert_manifest(v2_manifest, v3_base_url)

            # Write v3 manifest
            output_path = output_dir / "manifest.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(v3_manifest, f, ensure_ascii=False, indent=4)

            converted_count += 1
            if converted_count % 100 == 0:
                print(f"Converted {converted_count} manifests...")

        except Exception as e:
            print(f"Error converting {manifest_path}: {e}")
            error_count += 1

    print(f"\nConversion complete!")
    print(f"Successfully converted: {converted_count}")
    print(f"Errors: {error_count}")


if __name__ == "__main__":
    main()
