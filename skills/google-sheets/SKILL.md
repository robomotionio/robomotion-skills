---
name: "google-sheets"
description: "Google Sheets — read, write, append, and manage spreadsheet data, sheets, and formatting. Supports cell operations, range reads/writes, and sheet management via `robomotion googlesheets`. Do NOT use for Excel 365, Airtable, or CSV files."
---

# Google Sheets

The `robomotion googlesheets` CLI connects to Google Sheets API for spreadsheet operations. It reads and writes cell ranges, appends rows, manages worksheets, and handles spreadsheet creation and formatting.

## When to use
- Read or write cell ranges and individual cells in Google Sheets
- Append rows to spreadsheets
- Create spreadsheets and manage worksheets

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install googlesheets`
- Google Sheets OAuth2 or Service Account credentials configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install googlesheets`
2. Connect with session:
   ```
   robomotion googlesheets connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion googlesheets get_range --client-id "<client-id>" --spreadsheet-id <id> --range <A1:D10> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion googlesheets disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion googlesheets open_spreadsheet --spreadsheet-url --output json`
  Opens a Google Spreadsheet by URL and returns its ID
- `robomotion googlesheets create_spreadsheet --title [--sharewith] --output json`
  Creates a new Google Spreadsheet
- `robomotion googlesheets switch_sheet --spreadsheet-id --sheet-name --output json`
  Switches to a different sheet tab in the spreadsheet
- `robomotion googlesheets add_sheet --spreadsheet-id --sheet-name --output json`
  Adds a new sheet tab to an existing Google Spreadsheet
- `robomotion googlesheets set_cell_value --spreadsheet-id --cell --cell-value --output json`
  Sets the value of a single cell
- `robomotion googlesheets get_cell_value --spreadsheet-id --cell --output json`
  Gets the value of a single cell
- `robomotion googlesheets insert_row --spreadsheet-id --start-cell --row --output json`
  Inserts row data at specified cell or appends to last row
- `robomotion googlesheets delete_row --spreadsheet-id --row-number --output json`
  Deletes an entire row from the current sheet
- `robomotion googlesheets insert_column --spreadsheet-id --start-cell --column --output json`
  Inserts column data starting at specified cell
- `robomotion googlesheets delete_column --spreadsheet-id --column --output json`
  Deletes an entire column from the current sheet
- `robomotion googlesheets get_row --spreadsheet-id --row-number --output json`
  Gets all values from a specific row
- `robomotion googlesheets get_column --spreadsheet-id --start-cell --output json`
  Gets all values from a column starting at specified cell
- `robomotion googlesheets clear_range --spreadsheet-id --start-cell --end-cell --output json`
  Clears all values from a specified cell range without deleting the cells
- `robomotion googlesheets get_range --spreadsheet-id --from-cell --to-cell [--target] --output json`
  Gets data from a cell range as a table
- `robomotion googlesheets set_range --spreadsheet-id --start-cell --end-cell --table --output json`
  Writes table data to a cell range
- `robomotion googlesheets append_range --spreadsheet-id --table --output json`
  Appends table data as new rows at the end of the current sheet
- `robomotion googlesheets get_sheets --spreadsheet-id --output json`
  Gets list of all sheet tabs in the spreadsheet
- `robomotion googlesheets rename_sheet --spreadsheet-id --sheet-name --new-sheet-name --output json`
  Renames a sheet tab in the spreadsheet
- `robomotion googlesheets delete_sheet --spreadsheet-id --sheet-name --output json`
  Deletes a sheet tab from the spreadsheet
- `robomotion googlesheets format_range --spreadsheet-id --from-cell --to-cell [--format] --output json`
  Applies number format (Number٫ Date٫ Time٫ Text) to a cell range
- `robomotion googlesheets find_replace --spreadsheet-id --from-cell --to-cell --find --replacement [--target] --output json`
  Finds and replaces text in a spreadsheet range
- `robomotion googlesheets append_sheets --spreadsheet-id-1 --source-sheet-name --spreadsheet-id-2 --append-from-sheet-name --output json`
  Appends data from the second sheet to the first sheet (skips header row from second sheet)
- `robomotion googlesheets merge_sheets --spreadsheet-id-1 --first-sheet-name --spreadsheet-id-2 --second-sheet-name --output json`
  Merges data from second sheet into first sheet horizontally

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
