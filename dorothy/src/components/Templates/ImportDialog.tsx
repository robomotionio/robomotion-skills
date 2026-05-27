'use client';

import { useEffect, useRef, useState } from 'react';
import { FileText, Loader2, Upload, X } from 'lucide-react';

interface ImportDialogProps {
  onClose: () => void;
  onImport: (payload: unknown) => Promise<{ success: boolean; imported?: number; skipped?: number; errors?: string[]; error?: string }>;
}

interface ParsedPreview {
  count: number;
  names: string[];
}

export function ImportDialog({ onClose, onImport }: ImportDialogProps) {
  const [text, setText] = useState('');
  const [parsed, setParsed] = useState<unknown>(null);
  const [preview, setPreview] = useState<ParsedPreview | null>(null);
  const [parseError, setParseError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const dialogRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

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

  function tryParse(value: string) {
    setText(value);
    setParseError(null);
    setSubmitError(null);
    if (!value.trim()) {
      setParsed(null);
      setPreview(null);
      return;
    }
    try {
      const json = JSON.parse(value);
      if (!json || typeof json !== 'object') {
        setParseError('JSON must be an object');
        setParsed(null);
        setPreview(null);
        return;
      }
      if (json.kind !== 'dorothy.agent-template') {
        setParseError('Not a Dorothy template file (missing kind: "dorothy.agent-template")');
        setParsed(null);
        setPreview(null);
        return;
      }
      if (!Array.isArray(json.templates)) {
        setParseError('Missing or invalid "templates" array');
        setParsed(null);
        setPreview(null);
        return;
      }
      const items = json.templates as unknown[];
      const names = items
        .filter((t): t is { displayName: string } =>
          !!t && typeof t === 'object' && typeof (t as { displayName?: unknown }).displayName === 'string'
        )
        .map(t => t.displayName);
      setParsed(json);
      setPreview({ count: names.length, names });
    } catch (err) {
      setParseError(err instanceof Error ? err.message : 'Invalid JSON');
      setParsed(null);
      setPreview(null);
    }
  }

  async function handleFile(file: File) {
    const content = await file.text();
    tryParse(content);
  }

  async function handleSubmit() {
    if (!parsed) return;
    setSubmitting(true);
    setSubmitError(null);
    try {
      const result = await onImport(parsed);
      if (!result.success) {
        setSubmitError(result.error ?? 'Import failed');
        return;
      }
      onClose();
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : 'Import failed');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div ref={dialogRef} className="bg-card border border-border w-full max-w-xl max-h-[90vh] flex flex-col">
        <div className="px-5 py-4 border-b border-border flex items-center justify-between gap-3">
          <h2 className="font-semibold text-foreground">Import templates</h2>
          <button onClick={onClose} className="p-1 text-muted-foreground hover:text-foreground" title="Close">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-3">
          <p className="text-xs text-muted-foreground">
            Paste a Dorothy template JSON below or upload a <code className="text-foreground bg-secondary px-1">.json</code> file. Imported templates land under <strong>Your templates</strong>.
          </p>

          <div className="flex items-center gap-2">
            <button
              onClick={() => fileInputRef.current?.click()}
              className="flex items-center gap-1.5 px-2.5 py-1.5 text-xs bg-secondary border border-border hover:bg-accent/50 transition-colors"
            >
              <Upload className="w-3 h-3" />
              Upload file
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="application/json,.json"
              className="hidden"
              onChange={e => {
                const f = e.target.files?.[0];
                if (f) handleFile(f);
                e.target.value = '';
              }}
            />
          </div>

          <textarea
            value={text}
            onChange={e => tryParse(e.target.value)}
            placeholder='{ "kind": "dorothy.agent-template", "version": 1, "templates": [...] }'
            rows={10}
            className="w-full px-2 py-1.5 bg-secondary border border-border text-xs text-foreground placeholder:text-muted-foreground outline-none focus:border-primary/40 font-mono resize-y"
          />

          {parseError && (
            <p className="text-xs text-amber-700 dark:text-amber-400 bg-amber-500/10 border border-amber-500/30 px-2 py-1.5">{parseError}</p>
          )}

          {preview && (
            <div className="border border-border bg-secondary/30 px-3 py-2">
              <p className="text-xs font-medium text-foreground mb-1.5 flex items-center gap-1.5">
                <FileText className="w-3 h-3" />
                {preview.count} template{preview.count === 1 ? '' : 's'} ready to import
              </p>
              <ul className="text-xs text-muted-foreground list-disc pl-5 space-y-0.5">
                {preview.names.slice(0, 8).map((n, i) => <li key={`${n}-${i}`}>{n}</li>)}
                {preview.names.length > 8 && <li>…and {preview.names.length - 8} more</li>}
              </ul>
            </div>
          )}

          {submitError && (
            <p className="text-xs text-destructive bg-destructive/10 border border-destructive/30 px-2 py-1.5">{submitError}</p>
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
            disabled={!parsed || submitting}
            className="px-3 py-1.5 text-xs bg-foreground text-background font-medium hover:bg-foreground/90 transition-colors disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1.5"
          >
            {submitting && <Loader2 className="w-3 h-3 animate-spin" />}
            Import
          </button>
        </div>
      </div>
    </div>
  );
}
