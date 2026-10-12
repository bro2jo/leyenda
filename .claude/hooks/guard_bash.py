#!/usr/bin/env python3
"""PreToolUse guard for Bash: the two git rules of CLAUDE.md, enforced rather than asked for.

- `git commit` runs only when `darrow.py check` and `saga.py check` pass (exit 2 blocks the call and tells Claude why).
  `python3 engine/darrow.py ship -m "..."` is the normal way to commit: it runs every check and builds the site first.
- `git push` never forces (--force, -f, --force-with-lease, a +refspec).
Anything else passes untouched. Commands are tokenized (quotes respected), so a commit message that mentions
"git commit" is not mistaken for one.
"""
import json
import os
import shlex
import subprocess
import sys

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SEPARATORS = {"&&", "||", ";", "|", "&", "\n"}


def segments(command):
    lex = shlex.shlex(command, posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    seg = []
    try:
        for tok in lex:
            if tok in SEPARATORS or set(tok) <= set("&|;"):
                if seg:
                    yield seg
                seg = []
            else:
                seg.append(tok)
    except ValueError:  # unbalanced quotes: let the shell report it
        return
    if seg:
        yield seg


def git_subcommand(seg):
    """('commit', args) for `git commit ...` (env assignments and git's own -C/-c options skipped), else (None, [])."""
    i = 0
    while i < len(seg) and "=" in seg[i] and not seg[i].startswith("-"):
        i += 1
    if i >= len(seg) or os.path.basename(seg[i]) != "git":
        return None, []
    i += 1
    while i < len(seg) and seg[i].startswith("-"):
        i += 2 if seg[i] in ("-C", "-c") else 1
    return (seg[i], seg[i + 1:]) if i < len(seg) else (None, [])


def block(msg):
    print(msg, file=sys.stderr)
    sys.exit(2)


def main():
    try:
        command = json.load(sys.stdin).get("tool_input", {}).get("command", "")
    except (ValueError, AttributeError):
        return
    for seg in segments(command):
        sub, args = git_subcommand(seg)
        if sub == "push" and any(a in ("--force", "-f", "--force-with-lease") or a.startswith("--force")
                                 or (a.startswith("+") and len(a) > 1) for a in args):
            block("Blocked: never force-push (CLAUDE.md). If the push was rejected: git pull --rebase origin main, "
                  "then push again, or use python3 engine/darrow.py ship -m \"...\".")
        if sub == "commit":
            for check in (["engine/darrow.py", "check"], ["engine/saga.py", "check"]):
                r = subprocess.run([sys.executable] + check, cwd=ROOT, capture_output=True, text=True)
                out = (r.stdout + r.stderr).strip()
                failed = r.returncode != 0 or (check[0] == "engine/darrow.py" and out != "all logs look clean")
                if failed:
                    block(f"Blocked: `python3 {' '.join(check)}` fails, so nothing is committed:\n{out}\n"
                          "Fix it, then commit with python3 engine/darrow.py ship -m \"...\" (it also syncs and builds).")


if __name__ == "__main__":
    main()
