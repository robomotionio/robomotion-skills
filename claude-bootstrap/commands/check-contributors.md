# Check Contributors

Checks who's working on the project and optionally converts to a multi-person project with team state management.

---

## What This Command Does

1. **Detect current state** - Is this a solo or team project?
2. **Show active contributors** - Who's working on what right now?
3. **Offer conversion** - Convert solo → team project if needed

---

## Phase 1: Detect Project Type

Check for team structure:

```bash
# Check if team coordination exists
ls _project_specs/team/state.md 2>/dev/null
ls _project_specs/team/contributors.md 2>/dev/null

# Check git contributors
git shortlog -sn --all 2>/dev/null | head -10

# Check recent activity
git log --oneline --since="7 days ago" --format="%an" | sort | uniq -c | sort -rn
```

### If Team Structure Exists

Report current state:

```
📊 Team Project Detected

Contributors:
┌──────────┬────────────────┬──────────┐
│ Handle   │ Focus Area     │ Status   │
├──────────┼────────────────┼──────────┤
│ @alice   │ Backend, Auth  │ 🟢 Active │
│ @bob     │ Frontend       │ 🟡 Paused │
└──────────┴────────────────┴──────────┘

Active Sessions:
• @alice working on TODO-042 (src/auth/*)
• No conflicts detected

Claimed Todos:
• TODO-042 - @alice (since 2024-01-15)
• TODO-038 - @bob (since 2024-01-14)

Recent Decisions:
• [2024-01-15] JWT vs Sessions - chose JWT (@alice)

Run 'cat _project_specs/team/state.md' for full details.
```

### If Solo Project

```
👤 Solo Project Detected

Git contributors found:
• alice@example.com (142 commits)
• bob@example.com (38 commits)  ← Recent activity

This project has multiple git contributors but no team coordination.

Would you like to:
1. Convert to team project (adds team state management)
2. Keep as solo project (no changes)
```

---

## Phase 2: Convert to Team Project

If user chooses to convert:

### Step 1: Create Team Structure

```bash
mkdir -p _project_specs/team/handoffs
```

### Step 2: Create state.md

```markdown
# Team State

*Last synced: [TIMESTAMP]*

## Active Sessions

| Contributor | Working On | Started | Files Touched | Status |
|-------------|------------|---------|---------------|--------|
| - | - | - | - | - |

## Claimed Todos

| Todo | Claimed By | Since | ETA |
|------|------------|-------|-----|
| - | - | - | - |

## Recently Completed (Last 48h)

| Todo | Completed By | When | PR |
|------|--------------|------|-----|
| - | - | - | - |

## Conflicts to Watch

| Area | Contributors | Notes |
|------|--------------|-------|
| - | - | - |

## Announcements

- [DATE] Project converted to team coordination mode
```

### Step 3: Create contributors.md

Ask user about team members:

```
Who are the team members? (I'll help you fill this out)

For each person, I need:
- Handle (e.g., @alice)
- Name
- Focus areas (e.g., Backend, Auth)
- Timezone
- Status (Active/Part-time)
```

Then create:

```markdown
# Contributors

## Team Members

| Handle | Name | Focus Areas | Timezone | Status |
|--------|------|-------------|----------|--------|
| @[handle] | [name] | [areas] | [tz] | Active |

## Ownership

| Area | Primary | Backup | Notes |
|------|---------|--------|-------|
| - | - | - | Define as you work |

## Communication

- Slack: #[channel]
- PRs: Tag area owner for review
```

### Step 4: Update active.md

Add claim annotation format to existing todos:

```markdown
<!--
TEAM PROJECT - Claim format:
**Claimed:** @handle (YYYY-MM-DD HH:MM TZ)

Always claim a todo before starting work.
Check team/state.md for who's working on what.
-->

## [TODO-XXX] Description

**Status:** pending
**Claimed:** -

...
```

### Step 5: Update CLAUDE.md

Add team-coordination.md to skills list:

```markdown
## Skills
Read and follow these skills before writing any code:
- .claude/skills/base.md
- .claude/skills/team-coordination.md  ← Add this
...
```

### Step 6: Copy Skill

```bash
cp ~/.claude/skills/team-coordination.md .claude/skills/
```

---

## Phase 3: Summary

After conversion:

```
✅ Converted to Team Project

Created:
• _project_specs/team/state.md
• _project_specs/team/contributors.md
• _project_specs/team/handoffs/
• .claude/skills/team-coordination.md

Updated:
• _project_specs/todos/active.md (added claim format)
• CLAUDE.md (added team-coordination skill)

Next steps:
1. Fill out contributors.md with your team
2. Each team member should read team-coordination.md
3. Claim todos before starting work
4. Update state.md at start/end of each session

Commit these changes:
  git add _project_specs/team .claude/skills/team-coordination.md CLAUDE.md
  git commit -m "Enable team coordination for multi-person project"
  git push origin main
```

---

## Quick Check Mode

For quick status without conversion prompt:

```
/check-contributors --status
```

Output:

```
📊 Quick Status

Type: Team Project / Solo Project
Contributors: 3 (2 active this week)
Active Now: @alice (TODO-042)
Claimed: 2 todos
Conflicts: None

Last state update: 2 hours ago
```

---

## Reverting to Solo

If team coordination is no longer needed:

```
/check-contributors --solo
```

This:
1. Archives `_project_specs/team/` to `_project_specs/team-archive-[date]/`
2. Removes claim annotations from todos
3. Removes team-coordination.md from CLAUDE.md skills
4. Keeps decisions.md (valuable history)

---

## Usage

```bash
# Check who's working and see options
/check-contributors

# Quick status only
/check-contributors --status

# Force conversion to team project
/check-contributors --team

# Revert to solo project
/check-contributors --solo
```
