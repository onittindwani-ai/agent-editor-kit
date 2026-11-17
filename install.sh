#!/bin/sh
# Install the Agent Editor Kit skills so Claude Code can find them.
#
#   sh install.sh            copy the skills into ./.claude/skills of this folder (project install)
#   sh install.sh --global   copy them into ~/.claude/skills (every project)
#
# It never deletes anything and never overwrites a skill you already have: an existing skill
# folder with the same name is skipped and listed.
set -eu

HERE=$(cd "$(dirname "$0")" && pwd)
if [ "${1:-}" = "--global" ]; then
  DEST="$HOME/.claude/skills"
else
  DEST="$HERE/.claude/skills"
fi

mkdir -p "$DEST"
copied=0
skipped=0
for dir in "$HERE"/skills/*/; do
  name=$(basename "$dir")
  if [ -e "$DEST/$name" ]; then
    echo "skipped (already there): $name"
    skipped=$((skipped + 1))
  else
    cp -R "$dir" "$DEST/$name"
    copied=$((copied + 1))
  fi
done

echo "installed $copied skills into $DEST ($skipped skipped)"
echo "Next: open Claude Code in this folder and say: set up the Agent Editor Kit for me."
