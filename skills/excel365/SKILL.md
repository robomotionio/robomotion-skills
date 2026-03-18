---
name: "excel365"
description: "Microsoft Excel 365 — read, write, and manage workbooks, worksheets, tables, ranges, cells, rows, columns, and formulas in OneDrive/SharePoint. Full spreadsheet operations via `robomotion excel365`. Do NOT use for Google Sheets, local Excel files, or CSV processing."
---

# Microsoft Excel 365

The `robomotion excel365` CLI connects to Microsoft Excel 365 via the Graph API for full spreadsheet operations. It manages workbooks in OneDrive/SharePoint — reading and writing ranges, cells, rows, columns; managing worksheets and tables; handling formulas and hyperlinks; and supporting append, clear, and delete operations.

## When to use
- Read or write cell ranges, rows, and columns in Excel 365 workbooks
- Create workbooks and worksheets in OneDrive/SharePoint
- Manage Excel tables — get/set/append rows, create tables from ranges
- Get or set formulas and hyperlinks in cells

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install excel365`
- Microsoft 365 OAuth2 credentials configured via Robomotion vault

## Workflow
1. Install: `robomotion install excel365`
2. Open workbook: `robomotion excel365 open_workbook --file-path <path>` → returns a `workbook-id`
3. Read range: `robomotion excel365 read_range --workbook-id <id> --sheet-1 --range-address A1:D10`
4. Write cell: `robomotion excel365 set_cell --workbook-id <id> --sheet-1 --cell-address A1 --value <val>`
5. Close: `robomotion excel365 close_workbook --workbook-id <id>`

## Commands Reference
- `robomotion excel365 open_workbook --file-path --output json`
  Opens an Excel 365 workbook and returns a workbook ID for use in other nodes
- `robomotion excel365 close_workbook --workbook-id --output json`
  Closes an open Excel workbook and releases resources
- `robomotion excel365 create_workbook --workbook-name [--drive-id] [--folder-path] --output json`
  Creates a new Excel workbook in OneDrive or SharePoint and opens it for use
- `robomotion excel365 list_workbooks [--drive-id] [--folder-path] --output json`
  Lists Excel workbooks from OneDrive or SharePoint
- `robomotion excel365 get_workbook --workbook-id --output json`
  Gets details of a specific Excel workbook
- `robomotion excel365 list_worksheets --workbook-id --output json`
  Lists worksheets in an Excel workbook
- `robomotion excel365 create_worksheet --workbook-id --worksheet-name --output json`
  Creates a new worksheet in an Excel workbook
- `robomotion excel365 delete_worksheet --workbook-id --sheet-1 --output json`
  Deletes a worksheet from an Excel workbook
- `robomotion excel365 list_tables --workbook-id --sheet-1 --output json`
  Lists tables in an Excel workbook or worksheet
- `robomotion excel365 create_table --workbook-id --sheet-1 --range-address --column-names --output json`
  Creates a new table from a range in an Excel worksheet
- `robomotion excel365 get_table_rows --workbook-id --table-id --output json`
  Gets rows from an Excel table and outputs in DataTable format
- `robomotion excel365 get_table_row --workbook-id --table-id --row-index --output json`
  Gets a single row from an Excel table by index and returns as JSON object
- `robomotion excel365 set_table_row --workbook-id --table-id --row-index --row --output json`
  Updates a row in an Excel table by index
- `robomotion excel365 append_table_row --workbook-id --table-id --row --output json`
  Appends a new row to an Excel table
- `robomotion excel365 read_range --workbook-id --sheet-1 --range-address --output json`
  Reads data from a cell range in an Excel worksheet and outputs in DataTable format
- `robomotion excel365 write_range --workbook-id --sheet-1 --range-address --table --output json`
  Writes data to a cell range in an Excel worksheet
- `robomotion excel365 get_cell --workbook-id --sheet-1 --cell-address --output json`
  Reads a single cell value from an Excel worksheet
- `robomotion excel365 set_cell --workbook-id --sheet-1 --cell-address --value --output json`
  Writes a value to a single cell in an Excel worksheet
- `robomotion excel365 get_row --workbook-id --sheet-1 --row-number --output json`
  Reads a single row from an Excel worksheet and returns as JSON object
- `robomotion excel365 set_row --workbook-id --sheet-1 --row-number --row --output json`
  Writes values to a specific row in an Excel worksheet
- `robomotion excel365 append_row --workbook-id --sheet-1 --row --output json`
  Appends a new row at the end of data in an Excel worksheet
- `robomotion excel365 delete_row --workbook-id --sheet-1 --row-number --output json`
  Deletes a row at a specific position in an Excel worksheet
- `robomotion excel365 get_column --workbook-id --sheet-1 --column [--start-row] [--end-row] --output json`
  Gets data from a specific column in an Excel worksheet
- `robomotion excel365 insert_column --workbook-id --sheet-1 --column --values --output json`
  Inserts a new column with values at a specific position in an Excel worksheet
- `robomotion excel365 delete_column --workbook-id --sheet-1 --column --output json`
  Deletes one or more columns at a specific position in an Excel worksheet
- `robomotion excel365 clear_range --workbook-id --sheet-1 --range-address --output json`
  Clears content or formatting from a range in an Excel worksheet
- `robomotion excel365 clear_sheet --workbook-id --sheet-1 --output json`
  Clears all content or formatting from an entire Excel worksheet
- `robomotion excel365 get_formula --workbook-id --sheet-1 --cell-address --output json`
  Gets the formula from a single cell in an Excel worksheet
- `robomotion excel365 set_formula --workbook-id --sheet-1 --cell-address --formula --output json`
  Sets a formula in a single cell in an Excel worksheet
- `robomotion excel365 get_hyperlink --workbook-id --sheet-1 --cell-address --output json`
  Gets the hyperlink URL from a single cell in an Excel worksheet

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
