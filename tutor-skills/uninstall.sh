#!/bin/bash
set -e

SKILLS=("tutor-setup" "tutor")

for skill in "${SKILLS[@]}"; do
  SKILL_DIR="$HOME/.claude/skills/$skill"

  if [ -d "$SKILL_DIR" ]; then
    rm -rf "$SKILL_DIR"
    echo "Removed $skill from $SKILL_DIR"
  else
    echo "$skill not found at $SKILL_DIR (skipping)"
  fi
done
