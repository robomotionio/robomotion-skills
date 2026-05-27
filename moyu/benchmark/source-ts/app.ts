import * as fs from "fs";
import * as path from "path";
import { calculatePriorityScore, formatTaskDisplay } from "./helpers";

const DATA_FILE = path.join(__dirname, "tasks.json");

interface Task {
  id: number;
  title: string;
  status: "pending" | "completed";
  assignee: string | null;
  priority: "high" | "medium" | "low";
  created_at: string;
  completed_at?: string;
  tags?: string[];
}

function loadTasks(): Task[] {
  if (!fs.existsSync(DATA_FILE)) {
    return [];
  }
  const data = fs.readFileSync(DATA_FILE, "utf-8");
  if (!data) return [];
  return JSON.parse(data);
}

function saveTasks(tasks: Task[]): void {
  fs.writeFileSync(DATA_FILE, JSON.stringify(tasks, null, 2));
}

function addTask(
  title: string,
  assignee: string | null = null,
  priority: "high" | "medium" | "low" = "medium"
): Task {
  const tasks = loadTasks();
  const task: Task = {
    id: tasks.length + 1,
    title,
    status: "pending",
    assignee,
    priority,
    created_at: new Date().toISOString(),
  };
  tasks.push(task);
  saveTasks(tasks);
  return task;
}

function completeTask(taskId: number): Task | undefined {
  const tasks = loadTasks();
  for (const task of tasks) {
    if (task.id === taskId) {
      task.status = "completed";
      task.completed_at = new Date().toISOString();
      saveTasks(tasks);
      return task;
    }
  }
  // BUG: returns undefined but callers don't check
  return undefined;
}

function deleteTask(taskId: number): boolean {
  const tasks = loadTasks();
  const filtered = tasks.filter((t) => t.id !== taskId);
  // BUG: doesn't check if anything was actually removed
  saveTasks(filtered);
  return true;
}

function listTasks(status?: string): Task[] {
  const tasks = loadTasks();
  if (status) {
    return tasks.filter((t) => t.status === status);
  }
  return tasks;
}

function search(query: string): Task[] {
  const tasks = loadTasks();
  const results: Task[] = [];
  for (const task of tasks) {
    if (task.title.toLowerCase().includes(query.toLowerCase())) {
      results.push(task);
    }
  }
  return results;
}

function getStats(): { total: number; completed: number; pending: number } {
  const tasks = loadTasks();
  let completed = 0;
  let pending = 0;
  for (const task of tasks) {
    if (task.status === "completed") completed++;
    else if (task.status === "pending") pending++;
  }
  return { total: tasks.length, completed, pending };
}

function displayAll(): void {
  const tasks = loadTasks();
  for (const task of tasks) {
    const score = calculatePriorityScore(task);
    console.log(formatTaskDisplay(task, score));
  }
}

// CLI entry point
const args = process.argv.slice(2);
const cmd = args[0];

if (!cmd) {
  console.log(
    "Usage: ts-node app.ts [add|complete|delete|list|search|stats|display]"
  );
  process.exit(1);
}

switch (cmd) {
  case "add": {
    const title = args[1] || "Untitled";
    const assignee = args[2] || null;
    const task = addTask(title, assignee);
    console.log(`Added task #${task.id}: ${task.title}`);
    break;
  }
  case "complete": {
    const result = completeTask(parseInt(args[1]));
    if (result) console.log(`Completed: ${result.title}`);
    break;
  }
  case "delete": {
    const taskId = parseInt(args[1]);
    deleteTask(taskId);
    console.log(`Deleted task #${taskId}`);
    break;
  }
  case "list": {
    const tasks = listTasks(args[1]);
    for (const t of tasks) {
      console.log(`  [${t.status}] #${t.id}: ${t.title}`);
    }
    break;
  }
  case "search": {
    const results = search(args[1]);
    console.log(`Found ${results.length} results:`);
    for (const t of results) {
      console.log(`  #${t.id}: ${t.title}`);
    }
    break;
  }
  case "stats": {
    const stats = getStats();
    console.log(
      `Total: ${stats.total}, Completed: ${stats.completed}, Pending: ${stats.pending}`
    );
    break;
  }
  case "display":
    displayAll();
    break;
}

export {
  loadTasks,
  saveTasks,
  addTask,
  completeTask,
  deleteTask,
  listTasks,
  search,
  getStats,
};
