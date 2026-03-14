---
name: "google-sheets"
description: "Use when the user wants to call the Robomotion Google Sheets package to read, write, or manage data in Google Sheets via the `robomotion googlesheets` CLI. Do NOT use for Excel files, CSV files, or local spreadsheets."
---

# Google Sheets Skill

## When to use
- Read data from Google Sheets
- Write or append rows to Google Sheets
- Create or manage Google Sheets spreadsheets
- Update cells or ranges in Google Sheets

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install googlesheets`
- Credentials configured via Robomotion vault or environment variables

## Workflow
1. Install the package: `robomotion install googlesheets`
2. Run commands: `robomotion googlesheets <command> [flags]`

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
