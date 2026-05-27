import { useMemo } from 'react';
import type { AgentStatus } from '@/types/electron';
import { isSuperAgentCheck, getStatusPriority } from '@/app/agents/constants';

interface UseAgentFilteringProps {
  agents: AgentStatus[];
  projectFilter: string | null;
  statusFilter?: string | null;
  searchQuery?: string;
  sortBy?: 'created' | 'status' | 'activity' | 'name';
}

interface UniqueProject {
  path: string;
  name: string;
}

export function useAgentFiltering({ agents, projectFilter, statusFilter, searchQuery, sortBy = 'created' }: UseAgentFilteringProps) {
  const uniqueProjects = useMemo(() => {
    const projectSet = new Map<string, string>();
    agents.forEach((agent) => {
      const projectName = agent.projectPath.split('/').pop() || 'Unknown';
      projectSet.set(agent.projectPath, projectName);
    });
    return Array.from(projectSet.entries()).map(([path, name]) => ({ path, name }));
  }, [agents]);

  const filteredAgents = useMemo(() => {
    let filtered = projectFilter ? agents.filter(a => a.projectPath === projectFilter) : agents;

    if (statusFilter) {
      filtered = filtered.filter(a => a.status === statusFilter);
    }

    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      filtered = filtered.filter(a => {
        const name = (a.name || '').toLowerCase();
        const project = (a.projectPath.split('/').pop() || '').toLowerCase();
        const task = (a.currentTask || '').toLowerCase();
        return name.includes(q) || project.includes(q) || task.includes(q);
      });
    }

    return [...filtered].sort((a, b) => {
      const aIsSuper = isSuperAgentCheck(a);
      const bIsSuper = isSuperAgentCheck(b);
      if (aIsSuper && !bIsSuper) return -1;
      if (!aIsSuper && bIsSuper) return 1;

      if (sortBy === 'name') {
        return (a.name || '').localeCompare(b.name || '');
      }
      if (sortBy === 'activity') {
        return new Date(b.lastActivity).getTime() - new Date(a.lastActivity).getTime();
      }
      if (sortBy === 'status') {
        const aPriority = getStatusPriority(a.status);
        const bPriority = getStatusPriority(b.status);
        return aPriority - bPriority;
      }
      // Default: created (newest first); fall back to lastActivity for legacy agents missing createdAt
      const aCreated = new Date(a.createdAt || a.lastActivity).getTime();
      const bCreated = new Date(b.createdAt || b.lastActivity).getTime();
      return bCreated - aCreated;
    });
  }, [agents, projectFilter, statusFilter, searchQuery, sortBy]);

  return {
    filteredAgents,
    uniqueProjects,
  };
}
