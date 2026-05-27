'use client';

import { useEffect, useRef, useState } from 'react';
import { Loader2, X } from 'lucide-react';
import type { AgentTemplate, AgentTemplateInput, AgentCharacter, AgentProvider } from '@/types/electron';

const CHARACTERS: AgentCharacter[] = ['robot', 'ninja', 'wizard', 'astronaut', 'knight', 'pirate', 'alien', 'viking'];
const PROVIDERS: AgentProvider[] = ['claude', 'codex', 'gemini'];

interface TemplateFormDialogProps {
  initialTemplate?: AgentTemplate | null;
  installedSkills: string[];
  onClose: () => void;
  onSubmit: (input: AgentTemplateInput) => Promise<{ success: boolean; error?: string }>;
}

export function TemplateFormDialog({ initialTemplate, installedSkills, onClose, onSubmit }: TemplateFormDialogProps) {
  const [displayName, setDisplayName] = useState(initialTemplate?.displayName ?? '');
  const [description, setDescription] = useState(initialTemplate?.description ?? '');
  const [icon, setIcon] = useState(initialTemplate?.icon ?? '🤖');
  const [character, setCharacter] = useState<AgentCharacter>(initialTemplate?.character ?? 'robot');
  const [provider, setProvider] = useState<AgentProvider>(initialTemplate?.provider ?? 'claude');
  // Model is preserved when editing an existing template, but not asked on create —
  // it falls back to the provider's default.
  const initialModel = initialTemplate?.model;
  const [permissionMode, setPermissionMode] = useState<'normal' | 'auto' | 'bypass'>(initialTemplate?.permissionMode ?? 'normal');
  const [skills, setSkills] = useState<string[]>(initialTemplate?.skills ?? []);
  const [savedPrompt, setSavedPrompt] = useState(initialTemplate?.savedPrompt ?? '');

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const dialogRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
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

  function toggleSkill(name: string) {
    setSkills(prev => prev.includes(name) ? prev.filter(s => s !== name) : [...prev, name]);
  }

  async function handleSubmit() {
    if (!displayName.trim()) {
      setError('Name is required');
      return;
    }
    setError(null);
    setSubmitting(true);
    try {
      const result = await onSubmit({
        displayName: displayName.trim(),
        description: description.trim(),
        icon: icon.trim() || '🤖',
        character,
        provider,
        model: initialModel,
        permissionMode,
        skills,
        savedPrompt: savedPrompt.trim() || undefined,
      });
      if (!result.success) {
        setError(result.error ?? 'Failed to save template');
        return;
      }
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save template');
    } finally {
      setSubmitting(false);
    }
  }

  const allSkills = Array.from(new Set([...installedSkills, ...skills])).sort();

  return (
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div ref={dialogRef} className="bg-card border border-border w-full max-w-2xl max-h-[90vh] flex flex-col">
        <div className="px-5 py-4 border-b border-border flex items-center justify-between gap-3">
          <h2 className="font-semibold text-foreground">
            {initialTemplate ? 'Edit template' : 'New template'}
          </h2>
          <button onClick={onClose} className="p-1 text-muted-foreground hover:text-foreground" title="Close">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
          <div className="grid grid-cols-[80px_1fr] gap-3">
            <div>
              <label className="block text-xs font-medium text-foreground mb-1.5">Icon</label>
              <input
                type="text"
                value={icon}
                onChange={e => setIcon(e.target.value)}
                maxLength={4}
                className="w-full px-2 py-1.5 bg-secondary border border-border text-2xl text-center text-foreground outline-none focus:border-primary/40"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-foreground mb-1.5">Name</label>
              <input
                type="text"
                value={displayName}
                onChange={e => setDisplayName(e.target.value)}
                maxLength={40}
                placeholder="e.g. Mobile App Engineer"
                className="w-full px-2 py-1.5 bg-secondary border border-border text-sm text-foreground placeholder:text-muted-foreground outline-none focus:border-primary/40"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-foreground mb-1.5">Short description</label>
            <input
              type="text"
              value={description}
              onChange={e => setDescription(e.target.value)}
              maxLength={120}
              placeholder="What does this agent do? (one sentence)"
              className="w-full px-2 py-1.5 bg-secondary border border-border text-sm text-foreground placeholder:text-muted-foreground outline-none focus:border-primary/40"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-foreground mb-1.5">Character</label>
              <select
                value={character}
                onChange={e => setCharacter(e.target.value as AgentCharacter)}
                className="w-full px-2 py-1.5 bg-secondary border border-border text-sm text-foreground outline-none focus:border-primary/40"
              >
                {CHARACTERS.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-foreground mb-1.5">Provider</label>
              <select
                value={provider}
                onChange={e => setProvider(e.target.value as AgentProvider)}
                className="w-full px-2 py-1.5 bg-secondary border border-border text-sm text-foreground outline-none focus:border-primary/40"
              >
                {PROVIDERS.map(p => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-foreground mb-1.5">How careful?</label>
            <div className="flex gap-2">
              {(['normal', 'auto', 'bypass'] as const).map(m => (
                <button
                  key={m}
                  onClick={() => setPermissionMode(m)}
                  className={`flex-1 px-2 py-1.5 border text-xs transition-colors ${
                    permissionMode === m
                      ? 'bg-primary/15 border-primary text-primary font-medium'
                      : 'bg-secondary border-border text-muted-foreground hover:text-foreground'
                  }`}
                >
                  {m === 'normal' && 'Ask each time'}
                  {m === 'auto' && 'Run freely'}
                  {m === 'bypass' && 'Skip all checks'}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-foreground mb-1.5">
              Skills <span className="text-muted-foreground font-normal">({skills.length} selected)</span>
            </label>
            {allSkills.length === 0 ? (
              <p className="text-xs text-muted-foreground italic">No skills installed yet — visit the Skills page to install some.</p>
            ) : (
              <div className="flex flex-wrap gap-1 max-h-32 overflow-y-auto p-2 border border-border bg-secondary/30">
                {allSkills.map(skill => {
                  const selected = skills.includes(skill);
                  const installed = installedSkills.includes(skill);
                  return (
                    <button
                      key={skill}
                      onClick={() => toggleSkill(skill)}
                      className={`text-[10px] px-1.5 py-0.5 border transition-colors ${
                        selected
                          ? 'bg-primary/15 border-primary/40 text-primary'
                          : installed
                            ? 'bg-secondary border-border text-muted-foreground hover:text-foreground'
                            : 'bg-amber-500/10 border-amber-500/30 text-amber-700 dark:text-amber-400'
                      }`}
                      title={installed ? '' : 'Skill not installed'}
                    >
                      {skill}
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          <div>
            <label className="block text-xs font-medium text-foreground mb-1.5">System prompt (optional)</label>
            <textarea
              value={savedPrompt}
              onChange={e => setSavedPrompt(e.target.value)}
              rows={4}
              placeholder="Tell the agent how to behave. e.g. 'You are a senior frontend engineer…'"
              className="w-full px-2 py-1.5 bg-secondary border border-border text-sm text-foreground placeholder:text-muted-foreground outline-none focus:border-primary/40 resize-y"
            />
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
            onClick={handleSubmit}
            disabled={submitting || !displayName.trim()}
            className="px-3 py-1.5 text-xs bg-foreground text-background font-medium hover:bg-foreground/90 transition-colors disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1.5"
          >
            {submitting && <Loader2 className="w-3 h-3 animate-spin" />}
            {initialTemplate ? 'Save changes' : 'Create template'}
          </button>
        </div>
      </div>
    </div>
  );
}
