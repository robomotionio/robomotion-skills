---
name: "microsoft-ad"
description: "Active Directory — manage users, groups, organizational units, and group memberships. Supports LDAP-based user/group CRUD and OU management via `robomotion activedirectory`. Do NOT use for Azure AD/Entra ID, Okta, Auth0, or other identity providers."
---

# Active Directory

The `robomotion activedirectory` CLI connects to on-premises Active Directory via LDAP for user and group management. It creates, reads, updates, and deletes users; manages groups and group memberships; and handles organizational unit operations.

## When to use
- Create, update, disable, or delete Active Directory user accounts
- Manage AD groups and add/remove members
- List and search users or groups in organizational units
- Manage organizational units (OUs)

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install activedirectory`
- Active Directory LDAP connection credentials configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install activedirectory`
2. Connect with session:
   ```
   robomotion activedirectory ad_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion activedirectory ad_list_users --client-id "<client-id>" --ou <ou-dn> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion activedirectory ad_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Commands Reference
- `robomotion activedirectory add_user_to_group --access-id --group-object-id --user-id [--opt-tenant-id] [--opt-client-id] --output json`
  Adds a user as a member to a group in Azure Active Directory
- `robomotion activedirectory connect --tenant-id --client-id --session --output json`
  Connects to Azure Active Directory using client credentials and returns an access ID
- `robomotion activedirectory create_group --func --access-id [--opt-tenant-id] [--opt-client-id] --output json`
  Creates a new group in Azure Active Directory
- `robomotion activedirectory create_user --func --access-id [--opt-tenant-id] [--opt-client-id] --output json`
  Creates a new user in Azure Active Directory with the specified properties
- `robomotion activedirectory delete_group --access-id --group-object-id [--opt-tenant-id] [--opt-client-id] --output json`
  Deletes a group from Azure Active Directory
- `robomotion activedirectory delete_user --user-id --access-id [--opt-tenant-id] [--opt-client-id] --output json`
  Deletes a user from Azure Active Directory
- `robomotion activedirectory delete_user_from_group --access-id --group-object-id --user-id [--opt-tenant-id] [--opt-client-id] --output json`
  Removes a user from a group in Azure Active Directory
- `robomotion activedirectory get_group --access-id --group-object-id [--opt-tenant-id] [--opt-client-id] --output json`
  Retrieves detailed information about a specific group from Azure Active Directory
- `robomotion activedirectory get_user --user-id --access-id [--opt-tenant-id] [--opt-client-id] --output json`
  Retrieves detailed information about a specific user from Azure Active Directory
- `robomotion activedirectory list_all_groups --access-id [--opt-tenant-id] [--opt-client-id] --output json`
  Retrieves a list of all groups from Azure Active Directory
- `robomotion activedirectory list_all_users --access-id [--opt-tenant-id] [--opt-client-id] --output json`
  Retrieves a list of all users from Azure Active Directory
- `robomotion activedirectory list_group_members --access-id --group-object-id [--opt-tenant-id] [--opt-client-id] --output json`
  Retrieves a list of all members of a group from Azure Active Directory
- `robomotion activedirectory update_group --func --group-object-id --access-id [--opt-tenant-id] [--opt-client-id] --output json`
  Updates properties of an existing group in Azure Active Directory
- `robomotion activedirectory update_user --func --user-id --access-id [--opt-tenant-id] [--opt-client-id] --output json`
  Updates properties of an existing user in Azure Active Directory

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)
