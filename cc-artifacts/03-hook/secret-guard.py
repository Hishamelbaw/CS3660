#!/usr/bin/env python3
"""
PreToolUse hook: secret-guard

Fires before any Bash tool call. If the command contains `git add` or
`git commit`, scans the files about to be staged (for `git add`) or
already staged (for `git commit`, via `git diff --cached`) for:
  1. A literal `.env` file being staged (not `.env.example`/`.env.sample`).
  2. Secret-shaped literals: API key prefixes, Bearer tokens, AWS access
     keys, or long literals assigned to key/secret/token/password-named
     variables.

If either is found, the hook blocks the tool call (exit code 2) and
prints a reason to stderr, which Claude Code surfaces back to Claude so
it can explain the block and suggest a fix instead of silently retrying.
Clean commands are allowed to proceed untouched (exit code 0).
"""
import json
import os
import re
import subprocess
import sys

SECRET_PATTERNS = [
    (re.compile(r"sk-ant-[A-Za-z0-9\-_]{20,}"), "Anthropic API key"),
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "OpenAI-style API key"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key ID"),
    (re.compile(r"Bearer\s+[A-Za-z0-9\-_\.]{20,}"), "Bearer token"),
    (
        re.compile(
            r"(?i)(api_?key|secret|token|password)\s*[:=]\s*['\"][A-Za-z0-9+/=_\-]{16,}['\"]"
        ),
        "credential-shaped literal",
    ),
]


def redact(match_text: str) -> str:
    if len(match_text) <= 10:
        return "*" * len(match_text)
    return f"{match_text[:4]}...{match_text[-4:]}"


def scan_text(text: str, label: str, findings: list):
    for pattern, name in SECRET_PATTERNS:
        for m in pattern.finditer(text):
            findings.append(f"{label}: possible {name} ({redact(m.group(0))})")


def get_git_root(cwd: str):
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=cwd, capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    except Exception:
        return None


def files_targeted_by_add(command: str, cwd: str) -> list:
    parts = command.split()
    try:
        idx = parts.index("add")
    except ValueError:
        return []
    args = [p for p in parts[idx + 1:] if not p.startswith("-")]
    if not args or "." in args or "-A" in parts or "--all" in parts:
        try:
            out = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=cwd, capture_output=True, text=True, check=True,
            )
            files = []
            for line in out.stdout.splitlines():
                path = line[3:].strip()
                if path:
                    files.append(path)
            return files
        except Exception:
            return []
    return args


def main():
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except Exception:
        sys.exit(0)

    if payload.get("tool_name") != "Bash":
        sys.exit(0)

    command = (payload.get("tool_input") or {}).get("command", "")
    if not command or ("git add" not in command and "git commit" not in command):
        sys.exit(0)

    cwd = payload.get("cwd") or os.getcwd()
    git_root = get_git_root(cwd) or cwd

    findings = []

    if "git add" in command:
        for rel_path in files_targeted_by_add(command, git_root):
            abspath = os.path.join(git_root, rel_path)
            basename = os.path.basename(rel_path)
            if basename == ".env":
                findings.append(f"{rel_path}: staging a real .env file is blocked")
                continue
            if os.path.isfile(abspath):
                try:
                    with open(abspath, "r", errors="ignore") as f:
                        content = f.read()
                    scan_text(content, rel_path, findings)
                except Exception:
                    pass

    if "git commit" in command:
        try:
            out = subprocess.run(
                ["git", "diff", "--cached"],
                cwd=git_root, capture_output=True, text=True, check=True,
            )
            scan_text(out.stdout, "staged diff", findings)
        except Exception:
            pass
        try:
            out = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                cwd=git_root, capture_output=True, text=True, check=True,
            )
            for rel_path in out.stdout.splitlines():
                if os.path.basename(rel_path) == ".env":
                    findings.append(f"{rel_path}: a real .env file is staged for commit")
        except Exception:
            pass

    if findings:
        reason = (
            "secret-guard PreToolUse hook blocked this command:\n"
            + "\n".join(f"  - {f}" for f in findings)
            + "\n\nRemove the secret / unstage the file (e.g. `git restore --staged <file>`) "
              "before retrying."
        )
        print(reason, file=sys.stderr)
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
