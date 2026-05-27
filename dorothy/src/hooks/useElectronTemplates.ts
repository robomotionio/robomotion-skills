'use client';

import { useCallback, useEffect, useState } from 'react';
import { isElectron } from './useElectron';
import type { AgentTemplate, AgentTemplateInput, AgentTemplatePatch } from '@/types/electron';

export function useElectronTemplates() {
  const [templates, setTemplates] = useState<AgentTemplate[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (!isElectron() || !window.electronAPI?.template) {
      setIsLoading(false);
      return;
    }
    try {
      const result = await window.electronAPI.template.list();
      setTemplates(result.templates);
      setError(result.error ?? null);
    } catch (err) {
      console.error('Failed to list templates:', err);
      setError(err instanceof Error ? err.message : 'Failed to list templates');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  const create = useCallback(async (input: AgentTemplateInput) => {
    if (!window.electronAPI?.template) throw new Error('Electron API not available');
    const result = await window.electronAPI.template.create(input);
    await refresh();
    return result;
  }, [refresh]);

  const update = useCallback(async (patch: AgentTemplatePatch) => {
    if (!window.electronAPI?.template) throw new Error('Electron API not available');
    const result = await window.electronAPI.template.update(patch);
    await refresh();
    return result;
  }, [refresh]);

  const remove = useCallback(async (id: string) => {
    if (!window.electronAPI?.template) throw new Error('Electron API not available');
    const result = await window.electronAPI.template.delete(id);
    await refresh();
    return result;
  }, [refresh]);

  const duplicate = useCallback(async (id: string) => {
    if (!window.electronAPI?.template) throw new Error('Electron API not available');
    const result = await window.electronAPI.template.duplicate(id);
    await refresh();
    return result;
  }, [refresh]);

  const exportTemplates = useCallback(async (ids: string[]) => {
    if (!window.electronAPI?.template) throw new Error('Electron API not available');
    return window.electronAPI.template.export(ids);
  }, []);

  const importTemplates = useCallback(async (payload: unknown) => {
    if (!window.electronAPI?.template) throw new Error('Electron API not available');
    const result = await window.electronAPI.template.import(payload);
    await refresh();
    return result;
  }, [refresh]);

  return {
    templates,
    builtinTemplates: templates.filter(t => t.builtin),
    userTemplates: templates.filter(t => !t.builtin),
    isLoading,
    error,
    refresh,
    create,
    update,
    remove,
    duplicate,
    exportTemplates,
    importTemplates,
  };
}
