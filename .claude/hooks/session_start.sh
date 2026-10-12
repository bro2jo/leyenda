#!/bin/bash
# SessionStart (startup, resume): CLAUDE.md's "Every session" routine, done before the first message.
# Pulls main when the working tree is clean, syncs the engine, prints the day and the story digest.
# Never fails the session: anything that goes wrong is printed for Claude to handle.
set -uo pipefail
cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/../..}" || exit 0
cat >/dev/null  # the hook's JSON input is not needed

echo "## Session start (.claude/hooks/session_start.sh)"
if [ -n "$(git status --porcelain)" ]; then
  echo "- pull skipped: uncommitted changes in the working tree; commit them (or stash), then git pull --rebase origin main"
elif out=$(timeout 60 git pull -q --rebase origin main 2>&1); then
  echo "- pulled main: $(git log --oneline -1)"
else
  git rebase --abort >/dev/null 2>&1
  echo "- pull failed, nothing changed; run git pull --rebase origin main yourself. Git said: $(echo "$out" | head -3)"
fi

echo; echo "### python3 engine/darrow.py sync"
python3 engine/darrow.py sync 2>&1 | tail -20
echo; echo "### python3 engine/darrow.py today"
python3 engine/darrow.py today 2>&1 | head -25
echo; echo "### python3 engine/saga.py now"
python3 engine/saga.py now 2>&1 | head -40
exit 0
