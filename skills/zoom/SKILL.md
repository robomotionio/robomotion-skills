---
name: "zoom"
description: "Zoom — create and manage meetings, list recordings, and handle meeting participants. Supports meeting scheduling, recording management, and participant tracking via `robomotion zoom`. Do NOT use for Google Meet, Microsoft Teams, or other video platforms."
---

# Zoom

The `robomotion zoom` CLI connects to Zoom for meeting and recording management. It creates and schedules meetings, lists upcoming and past meetings, manages recordings, handles participants, and supports meeting lifecycle operations.

## When to use
- Create, schedule, update, or delete Zoom meetings
- List upcoming meetings and past meeting instances
- Manage and download meeting recordings
- Track meeting participants and registration

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install zoom`
- Zoom OAuth2 or JWT credentials configured via Robomotion vault

## Workflow
1. Install: `robomotion install zoom`
2. Connect: `robomotion zoom zoom_connect` → returns a `client-id`
3. Create meeting: `robomotion zoom zoom_create_meeting --client-id <id> --topic <title> --start-time <time>`
4. List meetings: `robomotion zoom zoom_list_meetings --client-id <id>`
5. Disconnect: `robomotion zoom zoom_disconnect --client-id <id>`

## Commands Reference
- `robomotion zoom zoom_connect`
  Connects to Zoom API using OAuth2 or Server-to-Server credentials
- `robomotion zoom zoom_disconnect --client-id`
  Closes the Zoom connection and releases resources
- `robomotion zoom zoom_create_meeting --client-id --me --topic [--meeting-type] [--start-time] [--60] [--timezone] [--password] [--agenda] [--waiting-room] [--join-before-host] [--mute-upon-entry] [--auto-recording] [--30]`
  Creates a new Zoom meeting with custom settings
- `robomotion zoom zoom_list_meetings --client-id --me [--meeting-type] [--30] [--next-page-token] [--30]`
  Lists all meetings for a specified Zoom user
- `robomotion zoom zoom_get_meeting --client-id --meeting-id [--occurrence-id] [--show-previous-occurrences] [--30]`
  Retrieves details for a specific Zoom meeting
- `robomotion zoom zoom_update_meeting --client-id --meeting-id [--topic] [--meeting-type] [--start-time] [--duration-(minutes)] [--timezone] [--password] [--agenda] [--auto-recording] [--30]`
  Updates an existing Zoom meeting's settings
- `robomotion zoom zoom_delete_meeting --client-id --meeting-id [--occurrence-id] [--schedule-reminder] [--cancel-meeting-reminder] [--30]`
  Deletes or cancels a Zoom meeting
- `robomotion zoom zoom_get_meeting_invitation --client-id --meeting-id [--30]`
  Retrieves the formatted invitation text for a Zoom meeting
- `robomotion zoom zoom_list_past_participants --client-id --meeting-id [--30] [--next-page-token] [--30]`
  Lists participants from a completed Zoom meeting
- `robomotion zoom zoom_list_recordings --client-id --me [--from-date] [--to-date] [--show-trash] [--30] [--next-page-token] [--30]`
  Lists cloud recordings for a Zoom user
- `robomotion zoom zoom_get_meeting_recordings --client-id --meeting-id [--include-folder-items] [--download-url-ttl-(seconds)] [--30]`
  Retrieves all recordings for a specific Zoom meeting
- `robomotion zoom zoom_delete_recording --client-id --meeting-id [--recording-id] [--action] [--30]`
  Deletes or trashes recordings for a Zoom meeting

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
