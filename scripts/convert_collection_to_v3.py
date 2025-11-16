#!/usr/bin/env python3
"""
IIIF Collection v2 to v3 converter
Converts collection JSON files from v2 to v3 format
"""

import json
import os
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


def convert_thumbnail(v2_thumbnail) -> List[Dict]:
    """Convert thumbnail from v2 to v3 format"""
    if not v2_thumbnail:
        return []

    if isinstance(v2_thumbnail, str):
        return [{
            "id": v2_thumbnail,
            "type": "Image"
        }]

    return [{
        "id": v2_thumbnail["@id"],
        "type": "Image",
        "format": v2_thumbnail.get("format", "image/jpeg"),
        "width": v2_thumbnail.get("width"),
        "height": v2_thumbnail.get("height")
    }]


def convert_manifest_reference(v2_manifest: Dict) -> Dict:
    """Convert manifest reference in collection from v2 to v3 format"""
    # Update manifest ID to point to v3 version
    v2_id = v2_manifest["@id"]
    # Extract manifest name (e.g., nishikie_hi-0001)
    manifest_name = v2_id.split("/")[-2]
    v3_id = f"https://hi-ut.github.io/dataset/iiif/3/{manifest_name}/manifest.json"

    v3_manifest = {
        "id": v3_id,
        "type": "Manifest",
        "label": {"ja": [v2_manifest.get("label", "")]}
    }

    # Add metadata if present
    if "metadata" in v2_manifest:
        v3_manifest["metadata"] = convert_metadata(v2_manifest["metadata"])

    # Add thumbnail
    if "thumbnail" in v2_manifest:
        v3_manifest["thumbnail"] = convert_thumbnail(v2_manifest["thumbnail"])

    # Add rights/license
    if "license" in v2_manifest:
        v3_manifest["rights"] = v2_manifest["license"]

    return v3_manifest


def convert_collection_reference(v2_collection: Dict) -> Dict:
    """Convert collection reference from v2 to v3 format"""
    # Update collection ID to point to v3 version
    v2_id = v2_collection["@id"]
    filename = v2_id.split("/")[-1]
    v3_id = f"https://hi-ut.github.io/dataset/iiif/collection/3/{filename}"

    v3_collection = {
        "id": v3_id,
        "type": "Collection",
        "label": {"ja": [v2_collection.get("label", "")]}
    }

    # Add thumbnail
    if "thumbnail" in v2_collection:
        v3_collection["thumbnail"] = convert_thumbnail(v2_collection["thumbnail"])

    return v3_collection


def convert_collection(v2_collection: Dict) -> Dict:
    """Convert entire collection from v2 to v3 format"""

    # Extract ID and create v3 ID
    v2_id = v2_collection["@id"]
    filename = v2_id.split("/")[-1]
    v3_id = f"https://hi-ut.github.io/dataset/iiif/collection/3/{filename}"

    v3_collection = {
        "@context": "http://iiif.io/api/presentation/3/context.json",
        "id": v3_id,
        "type": "Collection",
        "label": {"ja": [v2_collection.get("label", "")]}
    }

    # Add summary (from description if exists)
    if "description" in v2_collection:
        # Remove HTML tags for v3 (or keep if needed)
        description = v2_collection["description"]
        v3_collection["summary"] = {"ja": [description]}

    # Add thumbnail
    if "thumbnail" in v2_collection:
        v3_collection["thumbnail"] = convert_thumbnail(v2_collection["thumbnail"])

    # Handle partOf (was "within" in v2)
    if "within" in v2_collection:
        within_url = v2_collection["within"]
        within_filename = within_url.split("/")[-1]
        v3_collection["partOf"] = [{
            "id": f"https://hi-ut.github.io/dataset/iiif/collection/3/{within_filename}",
            "type": "Collection"
        }]

    # Convert nested collections
    if "collections" in v2_collection:
        v3_collection["items"] = []
        for v2_coll in v2_collection["collections"]:
            v3_collection["items"].append(convert_collection_reference(v2_coll))

    # Convert manifests
    if "manifests" in v2_collection:
        if "items" not in v3_collection:
            v3_collection["items"] = []
        for v2_manifest in v2_collection["manifests"]:
            v3_collection["items"].append(convert_manifest_reference(v2_manifest))

    # Handle behavior hints (vhint in v2)
    if "vhint" in v2_collection:
        # Map v2 viewing hints to v3 behaviors
        vhint = v2_collection["vhint"]
        if vhint == "use-thumb":
            # This is not a standard v3 behavior, but we can keep it as metadata
            pass

    return v3_collection


def main():
    # Set paths
    base_dir = Path(__file__).parent.parent / "docs" / "iiif" / "collection"
    v3_dir = base_dir / "3"
    v3_dir.mkdir(parents=True, exist_ok=True)

    # Find all collection JSON files (excluding v3 directory)
    collection_files = []
    for json_file in base_dir.glob("*.json"):
        collection_files.append(json_file)

    print(f"Found {len(collection_files)} collection files to convert")

    converted_count = 0
    error_count = 0

    for collection_path in collection_files:
        try:
            # Read v2 collection
            with open(collection_path, 'r', encoding='utf-8') as f:
                v2_collection = json.load(f)

            # Convert collection
            v3_collection = convert_collection(v2_collection)

            # Write v3 collection
            output_path = v3_dir / collection_path.name
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(v3_collection, f, ensure_ascii=False, indent=4)

            print(f"Converted: {collection_path.name}")
            converted_count += 1

        except Exception as e:
            print(f"Error converting {collection_path}: {e}")
            error_count += 1

    print(f"\nConversion complete!")
    print(f"Successfully converted: {converted_count}")
    print(f"Errors: {error_count}")


if __name__ == "__main__":
    main()
