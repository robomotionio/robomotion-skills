---
name: robomotion-projects
description: Start and work in a Robomotion project with the robomotion command - one folder per job, the person's device sign-in, the project's flow and app skills, then validate, run on the person's robot and read the run's log. Use whenever you build, change, check or run a Robomotion flow or app.
license: Apache-2.0
compatibility: Needs the robomotion command (mounted by the Hermes launcher 0.26.5+ for this group) and outbound network access to the person's Robomotion workspace and github.com.
---

# Robomotion projects

The `robomotion` command is on your `PATH`. `robomotion help <command>` explains
any command; read it instead of guessing a flag.

## One folder per job

Every job gets its own folder under `/workspace/projects/`, named for the job
(`/workspace/projects/supplier-prices`). Work only inside it. Everything the
command keeps for a project (its sign-in, the robot it runs on, run logs) is
kept in the project's `.robomotion/` folder.

## Starting a project

Create it with the command; it signs in first when the folder is not signed in:

```sh
cd /workspace/projects
robomotion create flow "Supplier prices" --workspace <their-workspace> --dir supplier-prices --no-browser > create.log 2>&1 &
```

`create app` instead of `create flow` when the job has screens. Read
`create.log` for the sign-in line with the link and the code, and send the
person exactly that: "Approve my sign-in to your workspace: open <link> and
enter the code <code>." Wait for the command to finish (check `create.log`
every 20 seconds, up to 10 minutes). Never ask for a password or an API key.

Then, inside the project:

```sh
cd /workspace/projects/supplier-prices
robomotion skills install
```

This puts the flow and app skills in `.claude/skills/` (`creating-flow`,
`building-app`, `running-flow`, `validating-flow`, `testing-flow`,
`searching-packages` and others). Read the whole `SKILL.md` of the one that
owns the job before you write anything, and follow it.

## Checking and running

```sh
robomotion validate                         # until it is clean
robomotion get robots                       # the person's robots
robomotion run --robot "<name>" --timeout 600
robomotion logs --last                      # the last run's events again
```

`run` builds the flow, runs it on the person's robot and follows its events to
the end: `flow_end` with `success`, or the node that failed and why. Run on one
of the person's own robots, never on an Application Robot (the robots named
after hired agents or apps). Exit code 3 means the robot runs on another
computer and its log is not here: say so, and ask the person to check the run
in the Designer.

## What you never do

- Never read, list or copy anything outside your project folders: no other
  folder's `.robomotion/`, no sign-in, key or session file that is not the
  one this project's sign-in made.
- Never put a password, key or code in a flow, a file or a message. Logins
  go in the person's Robomotion vault and the flow reads them from there.
