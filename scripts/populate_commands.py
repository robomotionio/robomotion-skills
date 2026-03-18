#!/usr/bin/env python3
"""
For each skill, install the CLI package and extract real commands via
`robomotion <cli> --list-commands --output json`, then regenerate SKILL.md
with a proper Commands Reference section.
"""

import json
import os
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(REPO_ROOT, "skills")
INDEX_PATH = os.path.join(REPO_ROOT, "skills-index.json")


def get_cli_name_from_skill_md(skill_dir):
    """Extract CLI name from SKILL.md frontmatter description."""
    md_path = os.path.join(skill_dir, "SKILL.md")
    with open(md_path) as f:
        content = f.read()
    # Extract cli name from `robomotion <cli>` pattern in description
    import re
    m = re.search(r'`robomotion (\S+)` CLI', content)
    if m:
        return m.group(1)
    return None


def install_package(cli_name):
    """Install a robomotion package. Returns True on success."""
    try:
        result = subprocess.run(
            ["robomotion", "install", cli_name],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            return True
        # Already installed is fine
        if "already installed" in result.stderr.lower() or "already installed" in result.stdout.lower():
            return True
        print(f"    Install stderr: {result.stderr.strip()}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"    Install timed out for {cli_name}")
        return False
    except Exception as e:
        print(f"    Install error: {e}")
        return False


def get_commands_json(cli_name):
    """Get commands as JSON from robomotion CLI. Returns list of command dicts."""
    try:
        result = subprocess.run(
            ["robomotion", cli_name, "--list-commands", "--output", "json"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            print(f"    list-commands failed: {result.stderr.strip()}")
            return None
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"    JSON parse error: {e}")
        return None
    except subprocess.TimeoutExpired:
        print(f"    list-commands timed out")
        return None
    except Exception as e:
        print(f"    list-commands error: {e}")
        return None


def format_command_line(cli_name, cmd):
    """Format a single command reference line."""
    name = cmd["name"]
    desc = cmd.get("description", "")
    params = cmd.get("parameters") or []

    # Build flags string
    required_flags = []
    optional_flags = []
    for p in params:
        flag = f"--{p['name']}"
        if p.get("required", False):
            required_flags.append(flag)
        else:
            optional_flags.append(f"[{flag}]")

    parts = [f"`robomotion {cli_name} {name}"]
    if required_flags:
        parts[0] += " " + " ".join(required_flags)
    if optional_flags:
        parts[0] += " " + " ".join(optional_flags)
    parts[0] += "`"

    return f"- {parts[0]}\n  {desc}"


def rebuild_skill_md(skill_dir, cli_name, commands):
    """Regenerate SKILL.md with real Commands Reference section."""
    md_path = os.path.join(skill_dir, "SKILL.md")
    with open(md_path) as f:
        content = f.read()

    # Build commands reference section
    cmd_lines = []
    for cmd in commands:
        cmd_lines.append(format_command_line(cli_name, cmd))
    commands_section = "## Commands Reference\n" + "\n".join(cmd_lines)

    # Check if Commands Reference already exists
    if "## Commands Reference" in content:
        # Replace existing section (everything between ## Commands Reference and next ## or end)
        import re
        content = re.sub(
            r'## Commands Reference\n.*?(?=\n## |\Z)',
            commands_section + "\n",
            content,
            flags=re.DOTALL
        )
    else:
        # Insert before ## Environment
        if "## Environment" in content:
            content = content.replace(
                "## Environment",
                commands_section + "\n\n## Environment"
            )
        else:
            # Append at end
            content = content.rstrip() + "\n\n" + commands_section + "\n"

    with open(md_path, "w") as f:
        f.write(content)


def main():
    # Get list of all skills and their CLI names
    skills = []
    for name in sorted(os.listdir(SKILLS_DIR)):
        skill_dir = os.path.join(SKILLS_DIR, name)
        if not os.path.isdir(skill_dir):
            continue
        cli_name = get_cli_name_from_skill_md(skill_dir)
        if cli_name:
            skills.append((name, cli_name, skill_dir))

    # Allow filtering by skill name via command line
    filter_names = set()
    if len(sys.argv) > 1 and sys.argv[1] != "--all":
        filter_names = set(sys.argv[1:])

    total = 0
    success = 0
    failed = []

    for skill_name, cli_name, skill_dir in skills:
        if filter_names and skill_name not in filter_names:
            continue

        total += 1
        print(f"[{total}] {skill_name} (cli: {cli_name})")

        # Step 1: Install
        print(f"  Installing {cli_name}...")
        if not install_package(cli_name):
            print(f"  FAILED to install {cli_name}")
            failed.append((skill_name, "install failed"))
            continue

        # Step 2: Get commands
        print(f"  Getting commands...")
        commands = get_commands_json(cli_name)
        if not commands:
            print(f"  FAILED to get commands for {cli_name}")
            failed.append((skill_name, "no commands"))
            continue

        # Step 3: Rebuild SKILL.md
        print(f"  Writing {len(commands)} commands to SKILL.md")
        rebuild_skill_md(skill_dir, cli_name, commands)
        success += 1

    print(f"\nDone: {success}/{total} succeeded")
    if failed:
        print(f"Failed ({len(failed)}):")
        for name, reason in failed:
            print(f"  - {name}: {reason}")


if __name__ == "__main__":
    main()
