import { describe, it, expect } from 'vitest';

/**
 * normalizeJiraHost — replicated from electron/handlers/ipc-handlers.ts
 * and mcp-orchestrator/src/tools/automations.ts (identical logic in both).
 */
function normalizeJiraHost(domain: string): string {
  let host = domain.trim().replace(/^https?:\/\//, '').replace(/\/+$/, '');
  if (!host.includes('.')) {
    host = `${host}.atlassian.net`;
  }
  return host;
}

describe('normalizeJiraHost', () => {
  // ── Legacy subdomain-only values (backward compat) ──────────────────────

  it('appends .atlassian.net to bare subdomain', () => {
    expect(normalizeJiraHost('mycompany')).toBe('mycompany.atlassian.net');
  });

  it('handles single-word subdomain with extra whitespace', () => {
    expect(normalizeJiraHost('  mycompany  ')).toBe('mycompany.atlassian.net');
  });

  // ── Full Atlassian Cloud hostnames ──────────────────────────────────────

  it('passes through full atlassian.net hostname', () => {
    expect(normalizeJiraHost('mycompany.atlassian.net')).toBe('mycompany.atlassian.net');
  });

  it('does not double-append .atlassian.net', () => {
    expect(normalizeJiraHost('mycompany.atlassian.net')).toBe('mycompany.atlassian.net');
  });

  // ── Self-hosted / custom domains ───────────────────────────────────────

  it('passes through self-hosted domain', () => {
    expect(normalizeJiraHost('jira.example.com')).toBe('jira.example.com');
  });

  it('passes through self-hosted domain with subdomain', () => {
    expect(normalizeJiraHost('issues.corp.example.com')).toBe('issues.corp.example.com');
  });

  it('passes through IP-based host with port-like subdomain', () => {
    // e.g. jira.10.0.0.1 — has dots, should not append
    expect(normalizeJiraHost('jira.10.0.0.1')).toBe('jira.10.0.0.1');
  });

  // ── https:// prefix stripping ──────────────────────────────────────────

  it('strips https:// prefix from full hostname', () => {
    expect(normalizeJiraHost('https://mycompany.atlassian.net')).toBe('mycompany.atlassian.net');
  });

  it('strips http:// prefix from full hostname', () => {
    expect(normalizeJiraHost('http://jira.example.com')).toBe('jira.example.com');
  });

  it('strips https:// prefix from bare subdomain', () => {
    expect(normalizeJiraHost('https://mycompany')).toBe('mycompany.atlassian.net');
  });

  // ── Trailing slash stripping ───────────────────────────────────────────

  it('strips trailing slash from hostname', () => {
    expect(normalizeJiraHost('mycompany.atlassian.net/')).toBe('mycompany.atlassian.net');
  });

  it('strips multiple trailing slashes', () => {
    expect(normalizeJiraHost('jira.example.com///')).toBe('jira.example.com');
  });

  it('strips both https:// prefix and trailing slash', () => {
    expect(normalizeJiraHost('https://mycompany.atlassian.net/')).toBe('mycompany.atlassian.net');
  });

  // ── Edge cases ─────────────────────────────────────────────────────────

  it('handles empty string (returns .atlassian.net — caller validates)', () => {
    // Empty after trim has no dot → appends suffix
    expect(normalizeJiraHost('')).toBe('.atlassian.net');
  });

  it('handles whitespace-only string', () => {
    expect(normalizeJiraHost('   ')).toBe('.atlassian.net');
  });

  it('handles hostname with port in subdomain style', () => {
    // "jira.example.com:8080" — has a dot, passes through
    expect(normalizeJiraHost('jira.example.com:8080')).toBe('jira.example.com:8080');
  });

  it('handles mixed case', () => {
    expect(normalizeJiraHost('MyCompany.Atlassian.Net')).toBe('MyCompany.Atlassian.Net');
  });
});
