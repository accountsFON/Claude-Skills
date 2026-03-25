#!/usr/bin/env python3
"""
Webflow Local SEO — Gap Analysis Script
Finds missing service/product × location combos from JSON data.

Usage:
    python gap_analysis.py <landings_json> <services_json> <locations_json> \
        [--svc-field service] [--loc-field location]

Or import and call find_missing() directly.
"""

import json
import sys
import argparse


def find_missing(landing_items, svc_map, loc_map, svc_field=None, loc_field=None):
    """
    Find missing (location, service/product) combos.

    Args:
        landing_items: list of CMS item dicts (with 'fieldData' key)
        svc_map: dict of {id: name} for services or products
        loc_map: dict of {id: name} for locations
        svc_field: field slug for service/product reference (auto-detected if None)
        loc_field: field slug for location reference (auto-detected if None)

    Returns:
        list of (loc_name, svc_name, loc_id, svc_id) tuples for missing combos
    """
    # Auto-detect field names from first item
    if landing_items and (svc_field is None or loc_field is None):
        sample = landing_items[0].get('fieldData', {})
        if svc_field is None:
            for candidate in ('service', 'product-reference'):
                if candidate in sample:
                    svc_field = candidate
                    break
        if loc_field is None:
            for candidate in ('location', 'location-setting'):
                if candidate in sample:
                    loc_field = candidate
                    break

    # Build existing set using reference IDs
    existing = set()
    for item in landing_items:
        fd = item.get('fieldData', {})
        loc_id = fd.get(loc_field, '') if loc_field else ''
        svc_id = fd.get(svc_field, '') if svc_field else ''
        if loc_id and svc_id:
            existing.add((loc_id, svc_id))

    # Find all missing combos
    missing = []
    for loc_id, loc_name in loc_map.items():
        for svc_id, svc_name in svc_map.items():
            if (loc_id, svc_id) not in existing:
                missing.append((loc_name, svc_name, loc_id, svc_id))

    return missing, existing


def build_map_from_items(items, name_field='name'):
    """Build {id: name} map from a list of CMS items."""
    return {item['id']: item['fieldData'].get(name_field, item['id']) for item in items}


def make_slug(service_name, location_name):
    """Generate a URL-safe slug from service and location names."""
    import re
    combined = f"{service_name} in {location_name}"
    slug = combined.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = re.sub(r'-+', '-', slug)
    return slug


def make_name(service_name, location_name):
    """Generate display name for a local landing item."""
    return f"{service_name} in {location_name}"


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Find missing Webflow local landing combos')
    parser.add_argument('landings', help='JSON file with landing items array')
    parser.add_argument('services', help='JSON file with service/product items array')
    parser.add_argument('locations', help='JSON file with location items array')
    parser.add_argument('--svc-field', default=None, help='Service field slug (auto-detected)')
    parser.add_argument('--loc-field', default=None, help='Location field slug (auto-detected)')
    parser.add_argument('--limit', type=int, default=0, help='Limit output to N missing combos')
    args = parser.parse_args()

    with open(args.landings) as f:
        landings = json.load(f)
    with open(args.services) as f:
        svcs = json.load(f)
    with open(args.locations) as f:
        locs = json.load(f)

    svc_map = build_map_from_items(svcs)
    loc_map = build_map_from_items(locs)

    missing, existing = find_missing(landings, svc_map, loc_map, args.svc_field, args.loc_field)

    print(f"Matrix size: {len(svc_map)} services × {len(loc_map)} locations = {len(svc_map)*len(loc_map)} combos")
    print(f"Existing:    {len(existing)}")
    print(f"Missing:     {len(missing)}")
    print()

    display = missing[:args.limit] if args.limit else missing
    for i, (loc_name, svc_name, loc_id, svc_id) in enumerate(display, 1):
        print(f"{i:3}. {svc_name} in {loc_name}")
        print(f"     slug: {make_slug(svc_name, loc_name)}")
        print(f"     svc_id={svc_id}  loc_id={loc_id}")
