'use client';

import { useEffect, useState } from 'react';
import { Loader2, Plus, Sparkles, Upload } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { isElectron, useElectronSkills } from '@/hooks/useElectron';
import { useElectronTemplates } from '@/hooks/useElectronTemplates';
import type { AgentTemplate, AgentTemplateInput } from '@/types/electron';
import { DesktopRequiredMessage } from '@/components/AgentList';
import { TemplateCard } from '@/components/Templates/TemplateCard';
import { InstantiateDialog } from '@/components/Templates/InstantiateDialog';
import { TemplateFormDialog } from '@/components/Templates/TemplateFormDialog';
import { ImportDialog } from '@/components/Templates/ImportDialog';
import TerminalDialog from '@/components/TerminalDialog';
import { SKILLS_DATABASE, fetchSkillsFromMarketplace, type Skill } from '@/lib/skills-database';

export default function TemplatesPage() {
  const router = useRouter();
  const hasElectron = isElectron();
  const { builtinTemplates, userTemplates, isLoading, create, update, remove, duplicate, exportTemplates, importTemplates } = useElectronTemplates();
  const { installedSkills, refresh: refreshSkills } = useElectronSkills();

  const [instantiateTarget, setInstantiateTarget] = useState<AgentTemplate | null>(null);
  const [editTarget, setEditTarget] = useState<AgentTemplate | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [showImport, setShowImport] = useState(false);

  const [liveSkills, setLiveSkills] = useState<Skill[] | null>(null);
  const [installSkillTarget, setInstallSkillTarget] = useState<{ repo: string; title: string } | null>(null);
  const [installError, setInstallError] = useState<string | null>(null);

  useEffect(() => {
    fetchSkillsFromMarketplace().then(s => { if (s) setLiveSkills(s); }).catch(() => {});
  }, []);

  function findSkillRepo(skillName: string): string | null {
    const candidates = liveSkills ?? SKILLS_DATABASE;
    const lower = skillName.toLowerCase();
    const match = candidates.find(s => s.name.toLowerCase() === lower);
    return match ? match.repo : null;
  }

  function handleInstallSkill(skillName: string) {
    const repo = findSkillRepo(skillName);
    if (!repo) {
      setInstallError(`"${skillName}" isn't in the public marketplace. Install it manually from the Skills page.`);
      return;
    }
    setInstallSkillTarget({ repo: `${repo}/${skillName}`, title: skillName });
  }

  if (!hasElectron) {
    return (
      <div className="p-6">
        <DesktopRequiredMessage />
      </div>
    );
  }

  async function handleCreate(input: AgentTemplateInput) {
    const result = await create(input);
    return { success: result.success, error: result.error };
  }

  async function handleUpdate(input: AgentTemplateInput) {
    if (!editTarget) return { success: false, error: 'No template selected' };
    const result = await update({ id: editTarget.id, ...input });
    return { success: result.success, error: result.error };
  }

  async function handleDelete(template: AgentTemplate) {
    if (!confirm(`Delete template "${template.displayName}"? This cannot be undone.`)) return;
    await remove(template.id);
  }

  async function handleReset(template: AgentTemplate) {
    if (!confirm(`Reset "${template.displayName}" to its default settings?`)) return;
    await remove(template.id);
  }

  async function handleDuplicate(template: AgentTemplate) {
    await duplicate(template.id);
  }

  async function handleExport(template: AgentTemplate) {
    const result = await exportTemplates([template.id]);
    if (!result.success || !result.payload) return;
    const filename = `${template.displayName.toLowerCase().replace(/[^a-z0-9-]+/g, '-').replace(/^-+|-+$/g, '') || 'template'}.dorothy-template.json`;
    const blob = new Blob([JSON.stringify(result.payload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between gap-3 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-primary" />
            Agent Templates
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Pick a role, point it at a project, get an agent. No setup required.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowImport(true)}
            className="flex items-center gap-1.5 px-3 py-2 border border-border bg-card text-xs font-medium text-foreground hover:bg-accent/50 transition-colors"
          >
            <Upload className="w-4 h-4" />
            Import
          </button>
          <button
            onClick={() => setShowCreate(true)}
            className="flex items-center gap-1.5 px-3 py-2 bg-foreground text-background text-xs font-medium hover:bg-foreground/90 transition-colors"
          >
            <Plus className="w-4 h-4" />
            New blank template
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-20 text-muted-foreground">
          <Loader2 className="w-5 h-5 animate-spin mr-2" />
          Loading templates…
        </div>
      ) : (
        <>
          <section className="mb-8">
            <h2 className="text-sm font-semibold text-foreground uppercase tracking-wider mb-3">
              Built-in roles
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {builtinTemplates.map(t => (
                <TemplateCard
                  key={t.id}
                  template={t}
                  installedSkills={installedSkills}
                  onUse={() => setInstantiateTarget(t)}
                  onEdit={() => setEditTarget(t)}
                  onDuplicate={() => handleDuplicate(t)}
                  onReset={t.overridden ? () => handleReset(t) : undefined}
                  onExport={() => handleExport(t)}
                  onInstallSkill={handleInstallSkill}
                />
              ))}
            </div>
          </section>

          <section>
            <h2 className="text-sm font-semibold text-foreground uppercase tracking-wider mb-3">
              Your templates
            </h2>
            {userTemplates.length === 0 ? (
              <div className="border border-dashed border-border bg-secondary/20 p-8 text-center">
                <p className="text-sm text-muted-foreground mb-3">
                  You haven&apos;t saved any templates yet.
                </p>
                <p className="text-xs text-muted-foreground">
                  Duplicate a built-in role to customize it, or create a blank template.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {userTemplates.map(t => (
                  <TemplateCard
                    key={t.id}
                    template={t}
                    installedSkills={installedSkills}
                    onUse={() => setInstantiateTarget(t)}
                    onEdit={() => setEditTarget(t)}
                    onDuplicate={() => handleDuplicate(t)}
                    onDelete={() => handleDelete(t)}
                    onExport={() => handleExport(t)}
                    onInstallSkill={handleInstallSkill}
                  />
                ))}
              </div>
            )}
          </section>
        </>
      )}

      {instantiateTarget && (
        <InstantiateDialog
          template={instantiateTarget}
          onClose={() => setInstantiateTarget(null)}
          onCreated={() => router.push('/agents')}
        />
      )}

      {showCreate && (
        <TemplateFormDialog
          installedSkills={installedSkills}
          onClose={() => setShowCreate(false)}
          onSubmit={handleCreate}
        />
      )}

      {editTarget && (
        <TemplateFormDialog
          initialTemplate={editTarget}
          installedSkills={installedSkills}
          onClose={() => setEditTarget(null)}
          onSubmit={handleUpdate}
        />
      )}

      {showImport && (
        <ImportDialog
          onClose={() => setShowImport(false)}
          onImport={importTemplates}
        />
      )}

      <TerminalDialog
        open={!!installSkillTarget}
        repo={installSkillTarget?.repo ?? ''}
        title={installSkillTarget?.title ?? ''}
        availableProviders={['claude', 'codex', 'gemini']}
        onClose={() => {
          setInstallSkillTarget(null);
          refreshSkills();
        }}
      />

      {installError && (
        <div className="fixed bottom-4 right-4 z-50 max-w-sm bg-card border border-amber-500/40 px-4 py-3 shadow-lg flex flex-col gap-2">
          <p className="text-xs text-foreground">{installError}</p>
          <div className="flex items-center justify-end gap-2">
            <button
              onClick={() => setInstallError(null)}
              className="text-xs text-muted-foreground hover:text-foreground px-2 py-1"
            >
              Dismiss
            </button>
            <button
              onClick={() => { setInstallError(null); router.push('/skills'); }}
              className="text-xs bg-foreground text-background font-medium px-2 py-1 hover:bg-foreground/90"
            >
              Open Skills page
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
