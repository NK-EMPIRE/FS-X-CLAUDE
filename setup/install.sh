#!/usr/bin/env bash
# FS-X-VFX one-shot installer (macOS / Linux / Git Bash). Adds the marketplace and installs every plugin.
# Usage:  bash setup/install.sh
set -e
REPO="NK-EMPIRE/FS-X-VFX"; MARKET="fs-x-vfx"; PLUGINS=("vfx-intro")
command -v claude >/dev/null || { echo "Claude Code CLI not found: https://claude.com/claude-code"; exit 1; }
command -v git >/dev/null || { echo "Git not found. Install Git and sign in to GitHub first."; exit 1; }
GIT_TERMINAL_PROMPT=0 git ls-remote "https://github.com/$REPO.git" >/dev/null 2>&1 || { echo "No access to the private repo: ask NK-EMPIRE to add your GitHub account, then sign in to Git."; exit 1; }
if claude plugin marketplace list 2>&1 | grep -q "$MARKET"; then claude plugin marketplace update "$MARKET"; else claude plugin marketplace add "$REPO"; fi
for p in "${PLUGINS[@]}"; do claude plugin install "$p@$MARKET"; done
echo; echo "Done. Restart Claude Code, then run /vfx-setup."
