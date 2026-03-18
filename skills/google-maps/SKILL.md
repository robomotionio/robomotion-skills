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

## Workflow
1. Install: `robomotion install googlemaps`
2. Connect: `robomotion googlemaps googlemaps_connect` → returns a `client-id`
3. Geocode: `robomotion googlemaps googlemaps_geocode --client-id <id> --address <address>`
4. Disconnect: `robomotion googlemaps googlemaps_disconnect --client-id <id>`

## Commands Reference
- `robomotion googlemaps address_to_coordinates --address`
  Converts a street address to geographic coordinates (geocoding)
- `robomotion googlemaps coordinates_to_address --latitude --longitude`
  Converts geographic coordinates to a human-readable address (reverse geocoding)
- `robomotion googlemaps calculate_distance --coordinate-1 --coordinate-2`
  Calculates straight-line (Haversine) distance between two coordinates
- `robomotion googlemaps get_route_distance --coordinate-1 --coordinate-2`
  Calculates driving route distance between two coordinates using Google Directions API

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
