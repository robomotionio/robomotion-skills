---
name: "openweather"
description: "OpenWeatherMap — get current weather, forecasts, air quality, and historical weather data for any location. Supports geocoding and multiple weather data types via `robomotion openweather`. Do NOT use for AccuWeather or other weather services."
---

# OpenWeather

The `robomotion openweather` CLI connects to OpenWeatherMap API for weather data retrieval. It gets current weather conditions, multi-day forecasts, air quality data, and historical weather for any location by city name or coordinates.

## When to use
- Get current weather conditions for any city or coordinates
- Retrieve multi-day weather forecasts
- Check air quality index and pollutant levels
- Access historical weather data

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install openweather`
- OpenWeatherMap API key configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install openweather`
2. Connect with session:
   ```
   robomotion openweather openweather_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion openweather openweather_current --client-id "<client-id>" --city <city> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion openweather openweather_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion openweather openweather_connect --session --output json`
  Connects to OpenWeather API and returns a client ID for subsequent operations
- `robomotion openweather openweather_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the OpenWeather connection and releases resources
- `robomotion openweather get_current_weather --client-id --latitude --longitude [--units] [--language] --session-id "<session-id>" --output json`
  Gets current weather data for a location by coordinates
- `robomotion openweather get_forecast --client-id --latitude --longitude [--units] [--language] [--40] --session-id "<session-id>" --output json`
  Gets 5-day weather forecast for a location by coordinates
- `robomotion openweather get_air_pollution --client-id --latitude --longitude --session-id "<session-id>" --output json`
  Gets air quality and pollution data for a location by coordinates
- `robomotion openweather geocoding_search --client-id --city-name [--5] --session-id "<session-id>" --output json`
  Searches for locations by city name and returns coordinates

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
