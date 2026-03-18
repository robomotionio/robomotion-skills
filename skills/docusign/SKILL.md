---
name: "docusign"
description: "DocuSign eSignature — send documents for signing, manage envelopes and templates, track recipients. Supports envelope creation, status tracking, and document download via `robomotion docusign`. Do NOT use for Adobe Sign, HelloSign, PandaDoc, or other e-signature tools."
---

# DocuSign

The `robomotion docusign` CLI connects to DocuSign's eSignature API to send documents for electronic signing, manage envelopes and templates, track recipient status, and download completed documents.

## When to use
- Send documents for electronic signature via envelopes
- Create envelopes from templates with recipient data
- Track envelope and recipient signing status
- List templates and download completed documents

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install docusign`
- DocuSign API credentials (integration key, account ID) configured via Robomotion vault

## Workflow
1. Install: `robomotion install docusign`
2. Connect: `robomotion docusign docusign_connect` → returns a `client-id`
3. Create envelope: `robomotion docusign docusign_create_envelope --client-id <id> --template-id <tmpl> --recipients <json>`
4. Check status: `robomotion docusign docusign_get_envelope --client-id <id> --envelope-id <env>`
5. Disconnect: `robomotion docusign docusign_disconnect --client-id <id>`

## Commands Reference
- `robomotion docusign docusign_connect`
  Connects to Docusign API using OAuth2 and returns a client ID for subsequent operations
- `robomotion docusign docusign_disconnect --client-id`
  Closes the Docusign connection and releases resources
- `robomotion docusign docusign_create_envelope --client-id --document-path --signer-email --signer-name --email-subject --email-message --cc-email --cc-name [--initial-status]`
  Creates a new envelope with a document and recipients for signing
- `robomotion docusign docusign_create_envelope_from_template --client-id --template-id --email-subject --template-roles --email-message [--initial-status]`
  Creates a new envelope using a predefined template with role assignments
- `robomotion docusign docusign_send_envelope --client-id --envelope-id`
  Sends a draft envelope to recipients for signing
- `robomotion docusign docusign_get_envelope --client-id --envelope-id`
  Retrieves details and status of a specific envelope
- `robomotion docusign docusign_list_envelopes --client-id --from-date --to-date [--status-filter] [--100]`
  Lists envelopes with optional filtering by date and status
- `robomotion docusign docusign_download_document --client-id --envelope-id --save-path [--document]`
  Downloads a document from an envelope and saves it to the specified path
- `robomotion docusign docusign_void_envelope --client-id --envelope-id --void-reason`
  Voids an in-progress envelope، canceling the signature request
- `robomotion docusign docusign_list_templates --client-id --search-text [--100]`
  Lists available document templates in your Docusign account
- `robomotion docusign docusign_get_template --client-id --template-id`
  Retrieves detailed information about a specific template including roles and documents

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
