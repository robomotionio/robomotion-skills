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

## Workflow
1. Install: `robomotion install openweather`
2. Connect: `robomotion openweather openweather_connect` → returns a `client-id`
3. Get weather: `robomotion openweather openweather_current --client-id <id> --city <city>`
4. Disconnect: `robomotion openweather openweather_disconnect --client-id <id>`

## Commands Reference
- `robomotion openweather openweather_connect`
  Connects to OpenWeather API and returns a client ID for subsequent operations
- `robomotion openweather openweather_disconnect --client-id`
  Closes the OpenWeather connection and releases resources
- `robomotion openweather get_current_weather --client-id --latitude --longitude [--units] [--language]`
  Gets current weather data for a location by coordinates
- `robomotion openweather get_forecast --client-id --latitude --longitude [--units] [--language] [--40]`
  Gets 5-day weather forecast for a location by coordinates
- `robomotion openweather get_air_pollution --client-id --latitude --longitude`
  Gets air quality and pollution data for a location by coordinates
- `robomotion openweather geocoding_search --client-id --city-name [--5]`
  Searches for locations by city name and returns coordinates

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
