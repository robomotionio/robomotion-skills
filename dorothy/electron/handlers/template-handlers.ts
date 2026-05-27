import { ipcMain } from 'electron';
import * as fs from 'fs';
import * as path from 'path';
import { v4 as uuidv4 } from 'uuid';
import { DATA_DIR } from '../constants';
import { BUILTIN_TEMPLATES } from '../constants/builtin-templates';
import type {
  AgentTemplate,
  AgentTemplateInput,
  AgentTemplatePatch,
  BuiltinOverride,
  TemplateStore,
  TemplateExport,
} from '../types/template';
import {
  TEMPLATE_EXPORT_KIND,
  TEMPLATE_EXPORT_VERSION,
} from '../types/template';

const TEMPLATES_FILE = path.join(DATA_DIR, 'templates.json');
const TEMPLATES_BACKUP = path.join(DATA_DIR, 'templates.backup.json');

function ensureDir(): void {
  if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
  }
}

function emptyStore(): TemplateStore {
  return { user: [], overrides: {} };
}

function loadStore(): TemplateStore {
  ensureDir();
  if (!fs.existsSync(TEMPLATES_FILE)) return emptyStore();
  try {
    const data = fs.readFileSync(TEMPLATES_FILE, 'utf-8');
    if (!data.trim()) return emptyStore();
    const parsed = JSON.parse(data);

    // Legacy format: bare array of user templates
    if (Array.isArray(parsed)) {
      return {
        user: parsed.filter((t): t is AgentTemplate => !!t && !t.builtin),
        overrides: {},
      };
    }

    // Current format
    return {
      user: Array.isArray(parsed.user) ? parsed.user.filter((t: AgentTemplate) => !t.builtin) : [],
      overrides: typeof parsed.overrides === 'object' && parsed.overrides ? parsed.overrides : {},
    };
  } catch (err) {
    console.error('Failed to load templates.json:', err);
    return emptyStore();
  }
}

function saveStore(store: TemplateStore): void {
  ensureDir();
  if (fs.existsSync(TEMPLATES_FILE)) {
    const existing = fs.readFileSync(TEMPLATES_FILE, 'utf-8');
    if (existing.trim().length > 2) {
      fs.writeFileSync(TEMPLATES_BACKUP, existing);
    }
  }
  fs.writeFileSync(TEMPLATES_FILE, JSON.stringify(store, null, 2));
}

function applyOverride(builtin: AgentTemplate, override: BuiltinOverride | undefined): AgentTemplate {
  if (!override) return { ...builtin, overridden: false };
  return {
    ...builtin,
    ...override,
    id: builtin.id,
    builtin: true,
    overridden: true,
    createdAt: builtin.createdAt,
    updatedAt: override.updatedAt,
  };
}

function buildFromInput(input: AgentTemplateInput): AgentTemplate {
  const now = new Date().toISOString();
  return {
    id: uuidv4(),
    builtin: false,
    displayName: input.displayName,
    description: input.description ?? '',
    icon: input.icon ?? '🤖',
    tags: input.tags ?? [],
    character: input.character ?? 'robot',
    provider: input.provider ?? 'claude',
    model: input.model,
    localModel: input.localModel,
    permissionMode: input.permissionMode ?? 'normal',
    effort: input.effort,
    skills: input.skills ?? [],
    obsidianVaultPaths: input.obsidianVaultPaths,
    savedPrompt: input.savedPrompt,
    createdAt: now,
    updatedAt: now,
  };
}

function overrideFromPatch(patch: AgentTemplatePatch, prev?: BuiltinOverride): BuiltinOverride {
  const merged: BuiltinOverride = {
    ...prev,
    updatedAt: new Date().toISOString(),
  };
  // Only assign fields that were actually provided in the patch
  if (patch.displayName !== undefined) merged.displayName = patch.displayName;
  if (patch.description !== undefined) merged.description = patch.description;
  if (patch.icon !== undefined) merged.icon = patch.icon;
  if (patch.tags !== undefined) merged.tags = patch.tags;
  if (patch.character !== undefined) merged.character = patch.character;
  if (patch.provider !== undefined) merged.provider = patch.provider;
  if (patch.model !== undefined) merged.model = patch.model;
  if (patch.localModel !== undefined) merged.localModel = patch.localModel;
  if (patch.permissionMode !== undefined) merged.permissionMode = patch.permissionMode;
  if (patch.effort !== undefined) merged.effort = patch.effort;
  if (patch.skills !== undefined) merged.skills = patch.skills;
  if (patch.obsidianVaultPaths !== undefined) merged.obsidianVaultPaths = patch.obsidianVaultPaths;
  if (patch.savedPrompt !== undefined) merged.savedPrompt = patch.savedPrompt;
  return merged;
}

export function registerTemplateHandlers(): void {
  ipcMain.handle('template:list', async () => {
    try {
      const store = loadStore();
      const builtinsMerged = BUILTIN_TEMPLATES.map(b => applyOverride(b, store.overrides[b.id]));
      return { templates: [...builtinsMerged, ...store.user] };
    } catch (err) {
      console.error('template:list error:', err);
      return {
        templates: BUILTIN_TEMPLATES.map(b => ({ ...b, overridden: false })),
        error: err instanceof Error ? err.message : 'Failed to list templates',
      };
    }
  });

  ipcMain.handle('template:get', async (_event, id: string) => {
    const store = loadStore();
    const builtin = BUILTIN_TEMPLATES.find(t => t.id === id);
    if (builtin) {
      return { template: applyOverride(builtin, store.overrides[id]) };
    }
    const userTemplate = store.user.find(t => t.id === id);
    return { template: userTemplate ?? null };
  });

  ipcMain.handle('template:create', async (_event, input: AgentTemplateInput) => {
    try {
      if (!input?.displayName?.trim()) {
        return { success: false, error: 'displayName is required' };
      }
      const template = buildFromInput(input);
      const store = loadStore();
      store.user.push(template);
      saveStore(store);
      return { success: true, template };
    } catch (err) {
      console.error('template:create error:', err);
      return { success: false, error: err instanceof Error ? err.message : 'Failed to create template' };
    }
  });

  ipcMain.handle('template:update', async (_event, patch: AgentTemplatePatch) => {
    try {
      const store = loadStore();
      const builtin = BUILTIN_TEMPLATES.find(t => t.id === patch.id);

      if (builtin) {
        // Edits on built-ins are stored as overrides; the built-in keeps its slot.
        const nextOverride = overrideFromPatch(patch, store.overrides[patch.id]);
        store.overrides[patch.id] = nextOverride;
        saveStore(store);
        return { success: true, template: applyOverride(builtin, nextOverride) };
      }

      const idx = store.user.findIndex(t => t.id === patch.id);
      if (idx === -1) return { success: false, error: 'Template not found' };

      const merged: AgentTemplate = {
        ...store.user[idx],
        ...patch,
        id: store.user[idx].id,
        builtin: false,
        createdAt: store.user[idx].createdAt,
        updatedAt: new Date().toISOString(),
      };
      store.user[idx] = merged;
      saveStore(store);
      return { success: true, template: merged };
    } catch (err) {
      console.error('template:update error:', err);
      return { success: false, error: err instanceof Error ? err.message : 'Failed to update template' };
    }
  });

  ipcMain.handle('template:delete', async (_event, id: string) => {
    try {
      const store = loadStore();
      const isBuiltin = BUILTIN_TEMPLATES.some(t => t.id === id);

      if (isBuiltin) {
        // Built-ins can't be removed; deleting "resets" the override if any.
        if (!store.overrides[id]) {
          return { success: false, error: 'Built-in templates cannot be deleted.' };
        }
        delete store.overrides[id];
        saveStore(store);
        return { success: true, reset: true };
      }

      const next = store.user.filter(t => t.id !== id);
      if (next.length === store.user.length) {
        return { success: false, error: 'Template not found' };
      }
      store.user = next;
      saveStore(store);
      return { success: true };
    } catch (err) {
      console.error('template:delete error:', err);
      return { success: false, error: err instanceof Error ? err.message : 'Failed to delete template' };
    }
  });

  ipcMain.handle('template:export', async (_event, ids: string[]) => {
    try {
      const store = loadStore();
      const all: AgentTemplate[] = [
        ...BUILTIN_TEMPLATES.map(b => applyOverride(b, store.overrides[b.id])),
        ...store.user,
      ];
      const wanted = ids.length > 0 ? all.filter(t => ids.includes(t.id)) : all;
      if (wanted.length === 0) {
        return { success: false, error: 'No matching templates to export' };
      }
      const payload: TemplateExport = {
        version: TEMPLATE_EXPORT_VERSION,
        kind: TEMPLATE_EXPORT_KIND,
        exportedAt: new Date().toISOString(),
        templates: wanted.map(t => ({
          displayName: t.displayName,
          description: t.description,
          icon: t.icon,
          tags: t.tags,
          character: t.character,
          provider: t.provider,
          model: t.model,
          localModel: t.localModel,
          permissionMode: t.permissionMode,
          effort: t.effort,
          skills: t.skills,
          obsidianVaultPaths: t.obsidianVaultPaths,
          savedPrompt: t.savedPrompt,
        })),
      };
      return { success: true, payload };
    } catch (err) {
      console.error('template:export error:', err);
      return { success: false, error: err instanceof Error ? err.message : 'Failed to export templates' };
    }
  });

  ipcMain.handle('template:import', async (_event, payload: unknown) => {
    try {
      if (!payload || typeof payload !== 'object') {
        return { success: false, error: 'Invalid file: not an object' };
      }
      const p = payload as Partial<TemplateExport>;
      if (p.kind !== TEMPLATE_EXPORT_KIND) {
        return { success: false, error: 'Not a Dorothy template file' };
      }
      if (p.version !== TEMPLATE_EXPORT_VERSION) {
        return { success: false, error: `Unsupported template version: ${String(p.version)}` };
      }
      if (!Array.isArray(p.templates) || p.templates.length === 0) {
        return { success: false, error: 'No templates found in file' };
      }

      const store = loadStore();
      const created: AgentTemplate[] = [];
      const errors: string[] = [];

      for (const raw of p.templates) {
        if (!raw || typeof raw !== 'object' || typeof raw.displayName !== 'string' || !raw.displayName.trim()) {
          errors.push('Skipped a template missing displayName');
          continue;
        }
        const template = buildFromInput(raw);
        store.user.push(template);
        created.push(template);
      }

      if (created.length > 0) saveStore(store);

      return {
        success: created.length > 0,
        imported: created.length,
        skipped: errors.length,
        errors,
        templates: created,
      };
    } catch (err) {
      console.error('template:import error:', err);
      return { success: false, error: err instanceof Error ? err.message : 'Failed to import templates' };
    }
  });

  ipcMain.handle('template:duplicate', async (_event, id: string) => {
    try {
      const store = loadStore();
      const builtin = BUILTIN_TEMPLATES.find(t => t.id === id);
      const source = builtin
        ? applyOverride(builtin, store.overrides[id])
        : store.user.find(t => t.id === id);
      if (!source) return { success: false, error: 'Template not found' };

      const copy = buildFromInput({
        displayName: `${source.displayName} (copy)`,
        description: source.description,
        icon: source.icon,
        tags: source.tags,
        character: source.character,
        provider: source.provider,
        model: source.model,
        localModel: source.localModel,
        permissionMode: source.permissionMode,
        effort: source.effort,
        skills: source.skills,
        obsidianVaultPaths: source.obsidianVaultPaths,
        savedPrompt: source.savedPrompt,
      });
      store.user.push(copy);
      saveStore(store);
      return { success: true, template: copy };
    } catch (err) {
      console.error('template:duplicate error:', err);
      return { success: false, error: err instanceof Error ? err.message : 'Failed to duplicate template' };
    }
  });
}
