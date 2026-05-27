'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import { FolderOpen, Loader2, Search, X } from 'lucide-react';
import type { AgentTemplate } from '@/types/electron';
import { useElectronAgents, useElectronFS } from '@/hooks/useElectron';

interface InstantiateDialogProps {
  template: AgentTemplate;
  onClose: () => void;
  onCreated?: (agentId: string) => void;
}

export function InstantiateDialog({ template, onClose, onCreated }: InstantiateDialogProps) {
  const { createAgent, startAgent } = useElectronAgents();
  const { projects, openFolderDialog } = useElectronFS();

  const [projectPath, setProjectPath] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [name, setName] = useState(template.displayName);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const dialogRef = useRef<HTMLDivElement>(null);

  // Click outside / Escape to close
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    const onClick = (e: MouseEvent) => {
      if (dialogRef.current && !dialogRef.current.contains(e.target as Node)) onClose();
    };
    window.addEventListener('keydown', onKey);
    window.addEventListener('mousedown', onClick);
    return () => {
      window.removeEventListener('keydown', onKey);
      window.removeEventListener('mousedown', onClick);
    };
  }, [onClose]);

  const filteredProjects = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return projects;
    return projects.filter(p => p.name.toLowerCase().includes(q) || p.path.toLowerCase().includes(q));
  }, [projects, search]);

  async function handlePickFolder() {
    try {
      const picked = await openFolderDialog();
      if (typeof picked === 'string' && picked) setProjectPath(picked);
    } catch (err) {
      console.error('openFolderDialog failed:', err);
    }
  }

  async function handleCreate() {
    if (!projectPath) {
      setError('Please pick a project first.');
      return;
    }
    setError(null);
    setSubmitting(true);
    try {
      const resolvedModel = template.provider !== 'local' && template.model && template.model !== 'default'
        ? template.model
        : undefined;
      const agent = await createAgent({
        projectPath,
        skills: template.skills,
        character: template.character,
        name: name.trim() || template.displayName,
        permissionMode: template.permissionMode,
        effort: template.effort,
        provider: template.provider,
        model: resolvedModel,
        localModel: template.localModel,
        obsidianVaultPaths: template.obsidianVaultPaths,
      });
      const prompt = template.savedPrompt?.trim() ?? '';
      if (prompt) {
        await startAgent(agent.id, prompt, {
          model: resolvedModel,
          provider: template.provider,
          localModel: template.localModel,
        });
      }
      onCreated?.(agent.id);
      onClose();
    } catch (err) {
      console.error('Failed to create agent from template:', err);
      setError(err instanceof Error ? err.message : 'Failed to create agent');
      setSubmitting(false);
    }
  }

  return (
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div ref={dialogRef} className="bg-card border border-border w-full max-w-lg max-h-[90vh] flex flex-col">
        <div className="px-5 py-4 border-b border-border flex items-center justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0">
            <span className="text-2xl shrink-0">{template.icon}</span>
            <div className="min-w-0">
              <h2 className="font-semibold text-foreground truncate">Use template: {template.displayName}</h2>
              <p className="text-xs text-muted-foreground truncate">Pick a project, name your agent, and we&apos;ll set the rest up.</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 text-muted-foreground hover:text-foreground" title="Close">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
          <div>
            <label className="block text-xs font-medium text-foreground mb-1.5">Agent name</label>
            <input
              type="text"
              value={name}
              onChange={e => setName(e.target.value)}
              maxLength={40}
              className="w-full px-2 py-1.5 bg-secondary border border-border text-sm text-foreground placeholder:text-muted-foreground outline-none focus:border-primary/40"
              placeholder={template.displayName}
            />
          </div>

          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="block text-xs font-medium text-foreground">Project</label>
              <button
                onClick={handlePickFolder}
                className="text-xs text-primary hover:underline flex items-center gap-1"
              >
                <FolderOpen className="w-3 h-3" />
                Pick another folder…
              </button>
            </div>
            <div className="relative mb-2">
              <Search className="absolute left-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
              <input
                type="text"
                value={search}
                onChange={e => setSearch(e.target.value)}
                placeholder="Search your projects…"
                className="w-full pl-7 pr-2 py-1.5 bg-secondary border border-border text-sm text-foreground placeholder:text-muted-foreground outline-none focus:border-primary/40"
              />
            </div>
            <div className="max-h-56 overflow-y-auto border border-border bg-secondary/30">
              {filteredProjects.length === 0 ? (
                <p className="text-xs text-muted-foreground text-center py-4">No projects match. Use &ldquo;Pick another folder…&rdquo; above.</p>
              ) : (
                filteredProjects.map(p => (
                  <button
                    key={p.path}
                    onClick={() => setProjectPath(p.path)}
                    className={`w-full flex flex-col items-start px-3 py-2 text-left text-xs hover:bg-primary/5 transition-colors ${
                      projectPath === p.path ? 'bg-primary/10 border-l-2 border-l-primary' : ''
                    }`}
                  >
                    <span className="font-medium text-foreground">{p.name}</span>
                    <span className="text-[10px] text-muted-foreground truncate w-full">{p.path}</span>
                  </button>
                ))
              )}
            </div>
            {projectPath && !filteredProjects.some(p => p.path === projectPath) && (
              <p className="text-[11px] text-muted-foreground mt-1.5">Selected: <span className="text-foreground">{projectPath}</span></p>
            )}
          </div>

          {error && (
            <p className="text-xs text-destructive bg-destructive/10 border border-destructive/30 px-2 py-1.5">{error}</p>
          )}
        </div>

        <div className="px-5 py-3 border-t border-border flex items-center justify-end gap-2">
          <button
            onClick={onClose}
            className="px-3 py-1.5 text-xs text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors"
            disabled={submitting}
          >
            Cancel
          </button>
          <button
            onClick={handleCreate}
            disabled={!projectPath || submitting}
            className="px-3 py-1.5 text-xs bg-foreground text-background font-medium hover:bg-foreground/90 transition-colors disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1.5"
          >
            {submitting && <Loader2 className="w-3 h-3 animate-spin" />}
            Create agent
          </button>
        </div>
      </div>
    </div>
  );
}
