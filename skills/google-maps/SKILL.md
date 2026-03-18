---
name: "google-maps"
description: "Google Maps — geocode addresses, reverse geocode coordinates, search for places, and get directions. Supports location services via `robomotion googlemaps`. Do NOT use for OpenStreetMap, Mapbox, or other mapping services."
---

# Google Maps

The `robomotion googlemaps` CLI connects to Google Maps Platform for geocoding and location services. It converts addresses to coordinates (geocode), coordinates to addresses (reverse geocode), searches for places/businesses, and calculates directions between locations.

## When to use
- Geocode addresses to latitude/longitude coordinates
- Reverse geocode coordinates to human-readable addresses
- Search for places and businesses by query
- Get directions and distance between locations

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install googlemaps`
- Google Maps API key configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install googlemaps`
2. Connect with session:
   ```
   robomotion googlemaps googlemaps_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion googlemaps googlemaps_geocode --client-id "<client-id>" --address <address> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion googlemaps googlemaps_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion googlemaps address_to_coordinates --address --output json`
  Converts a street address to geographic coordinates (geocoding)
- `robomotion googlemaps coordinates_to_address --latitude --longitude --output json`
  Converts geographic coordinates to a human-readable address (reverse geocoding)
- `robomotion googlemaps calculate_distance --coordinate-1 --coordinate-2 --output json`
  Calculates straight-line (Haversine) distance between two coordinates
- `robomotion googlemaps get_route_distance --coordinate-1 --coordinate-2 --output json`
  Calculates driving route distance between two coordinates using Google Directions API

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
