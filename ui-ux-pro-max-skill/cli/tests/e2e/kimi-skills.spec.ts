import { expect, test } from '@playwright/test';
import { existsSync } from 'node:fs';
import { mkdir, mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { detectAIType, getAITypeDescription } from '../../src/utils/detect.js';
import {
  generatePlatformFiles,
  listBundledSubSkills,
  loadPlatformConfig,
  renderSkillFile,
} from '../../src/utils/template.js';

// Kimi Code loads project skills from .kimi-code/skills/<name>/SKILL.md
// (and .agents/skills/). SKILL.md needs name and description frontmatter:
// https://www.kimi.com/code/docs/en/kimi-code-cli/customization/skills.html

function scratchDir(name: string): Promise<string> {
  return mkdtemp(join(tmpdir(), `uipro-kimi-${name}-`));
}

test('kimi SKILL.md has the name and description frontmatter Kimi Code requires', async () => {
  const config = await loadPlatformConfig('kimi');
  const content = await renderSkillFile(config);
  const frontmatter = content.match(/^---\n([\s\S]*?)\n---\n/)?.[1] ?? '';

  expect(frontmatter).toMatch(/^name: ui-ux-pro-max$/m);
  expect(frontmatter).toMatch(/^description: "UI\/UX design intelligence/m);
});

test('kimi installs the skill, its data and the sub-skills under .kimi-code/skills', async () => {
  const scratch = await scratchDir('install');

  await generatePlatformFiles(scratch, 'kimi');

  const skills = join(scratch, '.kimi-code', 'skills');
  expect(existsSync(join(skills, 'ui-ux-pro-max', 'SKILL.md'))).toBe(true);
  expect(existsSync(join(skills, 'ui-ux-pro-max', 'scripts', 'search.py'))).toBe(true);
  expect(existsSync(join(skills, 'ui-ux-pro-max', 'data'))).toBe(true);
  for (const name of await listBundledSubSkills()) {
    expect(existsSync(join(skills, name, 'SKILL.md')), name).toBe(true);
  }
});

test('a .kimi-code directory is detected as kimi', async () => {
  const scratch = await scratchDir('detect');
  await mkdir(join(scratch, '.kimi-code'));

  const { detected, suggested } = detectAIType(scratch);

  expect(detected).toEqual(['kimi']);
  expect(suggested).toBe('kimi');
  expect(getAITypeDescription('kimi')).toBe('Kimi Code (.kimi-code/skills/)');
});
