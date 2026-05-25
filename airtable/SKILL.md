---
name: airtable
version: 1.0.0
summary: Airtable REST API via curl — list, read, filter, create, update, upsert, and delete records.
tags: ["airtable", "database", "records", "productivity"]
---

# Airtable

Work with Airtable bases, tables, and records through Airtable's REST API using `curl`. A single personal access token (PAT) authenticates every call.

## Capabilities

- List the bases a token can see and inspect a base's table/field schema
- List, get, filter, sort, and paginate records
- Create records (single or batched up to 10)
- Update records with PATCH (merge) and upsert by a merge field
- Delete records (single or batched up to 10)

## Usage

`$BASE_ID` is `app...`, `$TABLE` is the table name or `tbl...` id. Auth is `Authorization: Bearer $AIRTABLE_API_KEY`. Always pass `-s` and pretty-print with `python3 -m json.tool`.

```sh
# Discover: list bases, then a base's schema (field names, ids, select options)
curl -s "https://api.airtable.com/v0/meta/bases" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
curl -s "https://api.airtable.com/v0/meta/bases/$BASE_ID/tables" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool

# List records (first 10) and get one record
curl -s "https://api.airtable.com/v0/$BASE_ID/$TABLE?maxRecords=10" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
curl -s "https://api.airtable.com/v0/$BASE_ID/$TABLE/$RECORD_ID" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool

# Filter — formulas MUST be URL-encoded; let Python stdlib do it
FORMULA="{Status}='Todo'"
ENC=$(python3 -c 'import sys, urllib.parse; print(urllib.parse.quote(sys.argv[1], safe=""))' "$FORMULA")
curl -s "https://api.airtable.com/v0/$BASE_ID/$TABLE?filterByFormula=$ENC&maxRecords=20" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool

# Create one record
curl -s -X POST "https://api.airtable.com/v0/$BASE_ID/$TABLE" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"fields":{"Name":"New task","Status":"Todo","Priority":"High"}}' | python3 -m json.tool

# Create up to 10 in one call (typecast auto-coerces / creates select options)
curl -s -X POST "https://api.airtable.com/v0/$BASE_ID/$TABLE" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"typecast": true, "records": [
        {"fields": {"Name": "Task A", "Status": "Todo"}},
        {"fields": {"Name": "Task B", "Status": "In progress"}}]}' | python3 -m json.tool

# Update (PATCH merges; preserves fields you omit)
curl -s -X PATCH "https://api.airtable.com/v0/$BASE_ID/$TABLE/$RECORD_ID" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"fields":{"Status":"Done"}}' | python3 -m json.tool

# Upsert by a merge field — no record id needed (idempotent syncs)
curl -s -X PATCH "https://api.airtable.com/v0/$BASE_ID/$TABLE" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"performUpsert": {"fieldsToMergeOn": ["Email"]},
       "records": [{"fields": {"Email": "user@example.com", "Status": "Active"}}]}' | python3 -m json.tool

# Delete a record
curl -s -X DELETE "https://api.airtable.com/v0/$BASE_ID/$TABLE/$RECORD_ID" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```

### Field write shapes

| Field type | Write shape |
|---|---|
| Single line / long text | `"Name": "hello"` |
| Number / Checkbox | `"Score": 42` / `"Done": true` |
| Single select | `"Status": "Todo"` (option must exist unless `typecast: true`) |
| Multi-select | `"Tags": ["urgent", "bug"]` |
| Date / DateTime (UTC) | `"Due": "2026-04-01"` / `"At": "2026-04-01T14:30:00.000Z"` |
| Attachment | `"Files": [{"url": "https://…"}]` (Airtable fetches + rehosts) |
| Linked record | `"Owner": ["recXXXXXXXXXXXXXX"]` (array of record ids) |

### Useful formula patterns

`{Email}='user@example.com'` · `FIND('bug', LOWER({Title}))` · `AND({Status}='Todo', {Priority}='High')` · `OR({Owner}='alice', {Owner}='bob')` · `NOT({Assignee}='')` · `IS_AFTER({Due}, TODAY())`

## When to use

- "Add a row to the CRM base for this new lead"
- "List every record in Tasks where Status is Todo and Priority is High"
- "Upsert these contacts by email so we don't create duplicates"
- "Mark record recXXXX as Done"

## When NOT to use

- Prose docs / wikis (use `notion`)
- Issue tracking (use `linear` or `github-issues`)
- Reads on huge tables in one shot — Airtable caps pages at 100 records; loop with `offset`

## Operating notes

- **Inspect the schema before mutating.** `GET /v0/meta/bases/$BASE_ID/tables` confirms exact field names, the primary-field name, and select `options.choices`. Empty fields are omitted from record responses, so a missing key means an empty value, not a missing field.
- **PATCH merges, PUT replaces.** Default to PATCH; PUT clears any field you don't include.
- **Single-select options must exist** or you get `INVALID_MULTIPLE_CHOICE_OPTIONS` — pass `"typecast": true` to auto-create them.
- **Tokens are scoped per base.** A `403` on one base while another works means the PAT's Access list doesn't include that base, not an auth/scope problem.
- **Rate limit: 5 req/sec per base.** Batch related writes into one 10-record call; back off on `429` honoring `Retry-After`.
- **filterByFormula and bracketed params (`sort[0][field]`, `fields[]`, `records[]`) must be URL-encoded.** Use the Python stdlib snippet above; never hand-escape.
- Always read the `errors` array on non-2xx responses — Airtable returns structured codes (`AUTHENTICATION_REQUIRED`, `INVALID_PERMISSIONS`, `MODEL_ID_NOT_FOUND`, …).
- Deletions are not reversible via API — confirm the filter + count with the user before bulk-deleting.

## Attribution

Adapted from the [Nous Hermes Agent](https://github.com/NousResearch/hermes-agent) `airtable` skill (MIT).
