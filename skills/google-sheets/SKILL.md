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

## Workflow
1. Install: `robomotion install googlesheets`
2. Connect: `robomotion googlesheets connect` → returns a `client-id`
3. Read range: `robomotion googlesheets get_range --client-id <id> --spreadsheet-id <id> --range <A1:D10>`
4. Write: `robomotion googlesheets set_range --client-id <id> --spreadsheet-id <id> --range <A1> --values <data>`
5. Disconnect: `robomotion googlesheets disconnect --client-id <id>`

## Commands Reference
- `robomotion googlesheets open_spreadsheet --spreadsheet-url`
  Opens a Google Spreadsheet by URL and returns its ID
- `robomotion googlesheets create_spreadsheet --title [--sharewith]`
  Creates a new Google Spreadsheet
- `robomotion googlesheets switch_sheet --spreadsheet-id --sheet-name`
  Switches to a different sheet tab in the spreadsheet
- `robomotion googlesheets add_sheet --spreadsheet-id --sheet-name`
  Adds a new sheet tab to an existing Google Spreadsheet
- `robomotion googlesheets set_cell_value --spreadsheet-id --cell --cell-value`
  Sets the value of a single cell
- `robomotion googlesheets get_cell_value --spreadsheet-id --cell`
  Gets the value of a single cell
- `robomotion googlesheets insert_row --spreadsheet-id --start-cell --row`
  Inserts row data at specified cell or appends to last row
- `robomotion googlesheets delete_row --spreadsheet-id --row-number`
  Deletes an entire row from the current sheet
- `robomotion googlesheets insert_column --spreadsheet-id --start-cell --column`
  Inserts column data starting at specified cell
- `robomotion googlesheets delete_column --spreadsheet-id --column`
  Deletes an entire column from the current sheet
- `robomotion googlesheets get_row --spreadsheet-id --row-number`
  Gets all values from a specific row
- `robomotion googlesheets get_column --spreadsheet-id --start-cell`
  Gets all values from a column starting at specified cell
- `robomotion googlesheets clear_range --spreadsheet-id --start-cell --end-cell`
  Clears all values from a specified cell range without deleting the cells
- `robomotion googlesheets get_range --spreadsheet-id --from-cell --to-cell [--target]`
  Gets data from a cell range as a table
- `robomotion googlesheets set_range --spreadsheet-id --start-cell --end-cell --table`
  Writes table data to a cell range
- `robomotion googlesheets append_range --spreadsheet-id --table`
  Appends table data as new rows at the end of the current sheet
- `robomotion googlesheets get_sheets --spreadsheet-id`
  Gets list of all sheet tabs in the spreadsheet
- `robomotion googlesheets rename_sheet --spreadsheet-id --sheet-name --new-sheet-name`
  Renames a sheet tab in the spreadsheet
- `robomotion googlesheets delete_sheet --spreadsheet-id --sheet-name`
  Deletes a sheet tab from the spreadsheet
- `robomotion googlesheets format_range --spreadsheet-id --from-cell --to-cell [--format]`
  Applies number format (Number٫ Date٫ Time٫ Text) to a cell range
- `robomotion googlesheets find_replace --spreadsheet-id --from-cell --to-cell --find --replacement [--target]`
  Finds and replaces text in a spreadsheet range
- `robomotion googlesheets append_sheets --spreadsheet-id-1 --source-sheet-name --spreadsheet-id-2 --append-from-sheet-name`
  Appends data from the second sheet to the first sheet (skips header row from second sheet)
- `robomotion googlesheets merge_sheets --spreadsheet-id-1 --first-sheet-name --spreadsheet-id-2 --second-sheet-name`
  Merges data from second sheet into first sheet horizontally

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
