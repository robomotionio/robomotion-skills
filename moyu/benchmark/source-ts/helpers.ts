const PRIORITY_WEIGHTS: Record<string, number> = {
  high: 3,
  medium: 2,
  low: 1,
};

interface Task {
  id: number;
  title: string;
  status: string;
  assignee: string | null;
  priority: string;
  created_at: string;
  completed_at?: string;
  tags?: string[];
}

export function calculatePriorityScore(task: Task): number {
  const weight = PRIORITY_WEIGHTS[task.priority] ?? 2;
  const created = new Date(task.created_at);
  const ageDays = Math.floor(
    (Date.now() - created.getTime()) / (1000 * 60 * 60 * 24)
  );
  return weight * 10 + ageDays;
}

export function formatTaskDisplay(task: Task, score?: number): string {
  const icon = task.status === "completed" ? "\u2713" : "\u25CB";
  const assignee = task.assignee ?? "unassigned";
  let line = `${icon} #${task.id} [${task.priority}] ${task.title} (@${assignee})`;
  if (score !== undefined) {
    line += ` [score: ${score}]`;
  }
  return line;
}

export function parseDateString(dateStr: string): Date | null {
  try {
    const d = new Date(dateStr);
    return isNaN(d.getTime()) ? null : d;
  } catch {
    return null;
  }
}
