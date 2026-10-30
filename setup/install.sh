#!/usr/bin/env bash
# FS-X-CLAUDE installer (macOS / Linux / Git Bash). All plugins, or only the names you pass:
#   bash setup/install.sh            bash setup/install.sh cinematic-sound vfx-intro
set -e
REPO="NK-EMPIRE/FS-X-CLAUDE"; MARKET="fs-x-claude"; HERE="$(cd "$(dirname "$0")" && pwd)"
command -v claude >/dev/null || { echo "Install Claude Code first: https://claude.com/claude-code"; exit 1; }
command -v git >/dev/null || { echo "Install Git and sign in to GitHub first."; exit 1; }
GIT_TERMINAL_PROMPT=0 git ls-remote "https://github.com/$REPO.git" >/dev/null 2>&1 || { echo "No access to $REPO: ask NK-EMPIRE for access."; exit 1; }
if claude plugin marketplace list 2>&1 | grep -q "$MARKET"; then claude plugin marketplace update "$MARKET"; else claude plugin marketplace add "$REPO"; fi
if [ $# -gt 0 ]; then PLUGINS=("$@"); else mapfile -t PLUGINS < <(python3 -c "import json;[print(p['name']) for p in json.load(open('$HERE/../.claude-plugin/marketplace.json'))['plugins']]" 2>/dev/null || python -c "import json;[print(p['name']) for p in json.load(open('$HERE/../.claude-plugin/marketplace.json'))['plugins']]"); fi
for p in "${PLUGINS[@]}"; do claude plugin install "$p@$MARKET"; done
echo "Installed: ${PLUGINS[*]}. Restart Claude Code."
