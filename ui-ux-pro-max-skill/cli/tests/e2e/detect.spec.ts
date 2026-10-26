import { expect, test } from '@playwright/test';
import { mkdir, mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { detectAIType, getAITypeDescription } from '../../src/utils/detect.js';

test('a sole .agents directory detects every consumer and still suggests codex', async () => {
  const scratch = await mkdtemp(join(tmpdir(), 'uipro-detect-agents-'));
  await mkdir(join(scratch, '.agents'));

  const { detected, suggested } = detectAIType(scratch);

  // All four .agents consumers are detected, OpenClaw included.
  expect(detected).toEqual(['antigravity', 'codex', 'universal', 'openclaw']);
  // The shared folder must not degrade the suggestion to "all" now that a
  // fourth consumer exists — it stays on the .agents-family default.
  expect(suggested).toBe('codex');
});

test('openclaw has a platform description', async () => {
  expect(getAITypeDescription('openclaw')).toBe('OpenClaw (.agents/skills/)');
});
