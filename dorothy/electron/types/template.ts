import type { AgentCharacter, AgentProvider, AgentPermissionMode, AgentEffort } from './index';

export interface AgentTemplate {
  id: string;
  builtin: boolean;
  /** True if this built-in has been customized by the user. Always false for user templates. */
  overridden?: boolean;
  displayName: string;
  description: string;
  icon: string;
  tags: string[];
  character: AgentCharacter;
  provider: AgentProvider;
  model?: string;
  localModel?: string;
  permissionMode: AgentPermissionMode;
  effort?: AgentEffort;
  skills: string[];
  obsidianVaultPaths?: string[];
  savedPrompt?: string;
  createdAt: string;
  updatedAt: string;
}

/** User overrides on a built-in template. The built-in's id is the key in the store. */
export interface BuiltinOverride {
  displayName?: string;
  description?: string;
  icon?: string;
  tags?: string[];
  character?: AgentCharacter;
  provider?: AgentProvider;
  model?: string;
  localModel?: string;
  permissionMode?: AgentPermissionMode;
  effort?: AgentEffort;
  skills?: string[];
  obsidianVaultPaths?: string[];
  savedPrompt?: string;
  updatedAt: string;
}

export interface TemplateStore {
  user: AgentTemplate[];
  overrides: Record<string, BuiltinOverride>;
}

export const TEMPLATE_EXPORT_KIND = 'dorothy.agent-template' as const;
export const TEMPLATE_EXPORT_VERSION = 1 as const;

/** Wire format for sharing templates between Dorothy installs. */
export interface TemplateExport {
  version: typeof TEMPLATE_EXPORT_VERSION;
  kind: typeof TEMPLATE_EXPORT_KIND;
  exportedAt: string;
  templates: AgentTemplateInput[];
}

export interface AgentTemplateInput {
  displayName: string;
  description?: string;
  icon?: string;
  tags?: string[];
  character?: AgentCharacter;
  provider?: AgentProvider;
  model?: string;
  localModel?: string;
  permissionMode?: AgentPermissionMode;
  effort?: AgentEffort;
  skills?: string[];
  obsidianVaultPaths?: string[];
  savedPrompt?: string;
}

export interface AgentTemplatePatch {
  id: string;
  displayName?: string;
  description?: string;
  icon?: string;
  tags?: string[];
  character?: AgentCharacter;
  provider?: AgentProvider;
  model?: string;
  localModel?: string;
  permissionMode?: AgentPermissionMode;
  effort?: AgentEffort;
  skills?: string[];
  obsidianVaultPaths?: string[];
  savedPrompt?: string;
}
