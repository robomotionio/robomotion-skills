import { expect, test } from '@playwright/test';
import { mkdir, mkdtemp, readFile, readdir, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { initCommand } from '../../src/commands/init.js';

// ZIP containing release/.claude/skills/test/SKILL.md with "release fixture".
const releaseZip = Buffer.from(
  'UEsDBBQAAAAIAE9SWl1tv+CuEQAAAA8AAAAkAAAAcmVsZWFzZS8uY2xhdWRlL3NraWxscy90ZXN0L1NLSUxMLm1kK0rNSU0sTlVIy6woKS1KBQBQSwECFAAUAAAACABPUlpdbb/grhEAAAAPAAAAJAAAAAAAAAAAAAAAgAEAAAAAcmVsZWFzZS8uY2xhdWRlL3NraWxscy90ZXN0L1NLSUxMLm1kUEsFBgAAAAABAAEAUgAAAFMAAAAAAA==',
  'base64'
);

for (const outcome of ['success', 'download failure', 'extraction failure'] as const) {
  test(`legacy install removes temporary downloads after ${outcome}`, async () => {
    const scratch = await mkdtemp(join(tmpdir(), 'uipro-legacy-test-'));
    const downloads = join(scratch, 'downloads');
    const target = join(scratch, 'project');
    await mkdir(downloads);
    await mkdir(target);

    const previousCwd = process.cwd();
    const previousFetch = globalThis.fetch;
    const tempKeys = ['TMPDIR', 'TEMP', 'TMP'] as const;
    const previousEnv = tempKeys.map(key => process.env[key]);
    const requests: string[] = [];
    const assetUrl = 'https://example.invalid/release.zip';

    try {
      process.chdir(target);
      for (const key of tempKeys) process.env[key] = downloads;
      globalThis.fetch = async (input) => {
        const url = String(input);
        requests.push(url);
        if (url.endsWith('/releases/latest')) {
          return Response.json({
            tag_name: 'v-test',
            assets: [{ name: 'release.zip', browser_download_url: assetUrl }],
          });
        }
        expect(url).toBe(assetUrl);
        if (outcome === 'download failure') return new Response(null, { status: 503 });
        return new Response(outcome === 'success' ? releaseZip : 'invalid ZIP');
      };

      await initCommand({ ai: 'claude', legacy: true });

      expect(requests).toHaveLength(2);
      if (outcome === 'success') {
        expect(await readFile(join(target, '.claude/skills/test/SKILL.md'), 'utf8'))
          .toBe('release fixture');
      }
      expect(await readdir(downloads)).toEqual([]);
    } finally {
      globalThis.fetch = previousFetch;
      process.chdir(previousCwd);
      tempKeys.forEach((key, index) => {
        if (previousEnv[index] === undefined) delete process.env[key];
        else process.env[key] = previousEnv[index];
      });
      await rm(scratch, { recursive: true, force: true });
    }
  });
}
