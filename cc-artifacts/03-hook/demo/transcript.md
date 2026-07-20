# Demonstration transcript

A real run of the `secret-guard` PreToolUse hook against the
[job-pack](https://github.com/Hishamelbaw/job-pack) repo, showing it
both block a bad command and let a clean one through.

## Setup

- Copied `secret-guard.py` to `.claude/hooks/secret-guard.py` in
  job-pack.
- Registered it in job-pack's `.claude/settings.json` as a
  `PreToolUse` hook matched on `Bash` (the same registration shown in
  [`../settings.json`](../settings.json)).
- Created `scratch_secret_test.py` containing:

  ```python
  ANTHROPIC_API_KEY = "sk-ant-faketestkey1234567890abcdef"
  ```

## Test 1 — blocked

Command: `git add scratch_secret_test.py`, with the fake secret
present.

```
PreToolUse:Bash hook error: [python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/secret-guard.py"]: secret-guard PreToolUse hook blocked this command:
  - scratch_secret_test.py: possible Anthropic API key (sk-a...cdef)
  - scratch_secret_test.py: possible credential-shaped literal (API_...def")

Remove the secret / unstage the file (e.g. `git restore --staged <file>`) before retrying.
```

A follow-up `git status` confirmed nothing was staged — the file
stayed untracked. The hook fired on the `PreToolUse` event *before* the
`Bash` tool call ran, exited 2, and the `git add` never executed at
all: the secret never reached the index, let alone a commit.

## Test 2 — passed

Setup change: `scratch_secret_test.py` deleted, a blank line appended
to `README.md` instead — a clean change with nothing secret-shaped in
it.

Command: `git add README.md`

```
warning: in the working copy of 'README.md', LF will be replaced by CRLF the next time Git touches it
```

(only Git's routine CRLF warning — no hook block)

`git status` immediately after:

```
On branch main
Your branch is up to date with 'origin/main'
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
      modified:   README.md
Untracked files:
  (use "git add <file>..." to include in what will be committed)
      .claude/
```

The command proceeded normally: the hook still ran on the
`PreToolUse` event, found nothing matching either check, and exited 0,
so `git add` executed exactly as if the hook weren't installed.
Everything was left unstaged/uncommitted afterward per the test
instructions.

## Takeaway

Same hook, same event, two outcomes driven entirely by exit code: a
planted fake Anthropic key in a file about to be staged was caught and
the `git add` never ran (exit 2, Test 1); a genuinely clean `git add`
passed straight through (exit 0, Test 2). This is the behavior the
whole artifact exists for — the block happens *before* the tool call,
not after a secret is already in the index or a commit.
