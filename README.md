<!-- SYNTHETIC DEMO DATA — every account, person and number in this repo is made up. -->
# Renewal kit · Advanced Claude Code exercises (Cedar, Session 6)

This repo is the renewal kit from Session 2 plus the pieces Session 6 adds: a skill, a read-only reviewer agent, a slash command, a hook, a brief checker and a render script. You can follow every live exercise from the session on your own machine. Nothing here is real client data.

## Before you start

- Claude Code CLI (`claude --version`), `git`, `gh` logged in (`gh auth status`), `jq` (`brew install jq`; the hook refuses to run without it), Python 3.11+.
- Work in your own copy, not the shared repo. Create one from the template under your own account, with every checkpoint branch, and clone it:

  ```bash
  gh repo create renewal-kit-demo --template Emer-42/renewal-kit-demo --include-all-branches --private --clone
  ```

  Your copy has no link to the shared repo, so the branches you push and the pull requests Claude opens stay in your copy. Don't fork: in a fork, `gh pr create` targets the parent repo by default.

- Start Claude Code from the repo root: `cd renewal-kit-demo && claude`. Use Sonnet and Auto mode for the exercises; that is what the session used.

## Save points

Each exercise starts from a checkpoint branch. To reset your copy (this throws away local changes):

```bash
git fetch origin && git checkout -B main origin/ckpt/0 && git clean -fd
```

| Checkpoint | What it holds | Start of |
|---|---|---|
| `ckpt/0` | the kit, `.claude/` additions, `scripts/check_briefs.py` | Exercises A and C |
| `ckpt/1` | the acc-renewal-brief skill copied into `plugins/renewal-kit/` (PR #1 merged) | Exercise D |
| `ckpt/2` | `eh/lock-layout` updated from `ckpt/1`, with `scripts/render_brief.py` | Exercise D, render step |
| `ckpt/3` | hook and render script inside the plugin (PR #2 merged), `briefs/` empty | Exercise E |

For Exercise D you also need the branch `eh/lock-layout` as it was before the update: `git checkout -B eh/lock-layout origin/ckpt/lock-layout`.

## What is in the repo

| Path | What it is |
|---|---|
| `CLAUDE.md` | the rules: audience, length, numbers from the script only, no pricing |
| `accounts/<slug>/` | source data per account: calls, Jira export, metrics, prior-renewal notes. Read-only by hook |
| `briefs/` | where briefs go |
| `scripts/metrics.py` | the only source of numbers for a brief |
| `scripts/check_briefs.py` | checks every brief's headings and numbers, writes `briefs/check-report.md` |
| `.claude/skills/acc-renewal-brief/SKILL.md` | the brief skill: six fixed headings |
| `.claude/agents/skill-reviewer.md` | read-only Sonnet helper that reviews a skill change |
| `.claude/commands/acc-brief.md` | `/acc-brief <account>`: user-invoked only |
| `.claude/settings.json`, `.claude/hooks/guard-accounts.sh` | PreToolUse hook: nothing writes under `accounts/` |

## The exercises

Paste each prompt as written. After each one, look at what Claude did, not only what it said.

### A · Branch to draft PR

Start: `ckpt/0`, on `main`.

```
Make a branch eh/renewal-brief-plugin. Copy our acc-renewal-brief skill into plugin layout under plugins/renewal-kit/ and keep the project skill. Header with name, owner and a one-line description. Commit, push, and open a draft pull request: what changed, why, and how to test it.
```

Done when: the branch exists, `plugins/renewal-kit/skills/acc-renewal-brief/SKILL.md` exists, `.claude/skills/acc-renewal-brief/SKILL.md` is still there, and `gh` printed a draft PR URL. Notice you typed no git command.

### B · Review, revise, merge

Start: the PR from A, still open.

```
@agent-skill-reviewer review the SKILL.md changed on this branch. One line per finding: file, problem, fix.
```

The helper can read but not write. Expect it to flag a missing `team` field and a description that does not say when not to use the skill. Then add a comment on the PR in GitHub (`gh pr comment <n> --body "Add team, and say when not to use this."`) and run:

```
Address the review comments on this pull request. Commit and push on the same branch.
```

Done when: a new commit appears on the same PR. Mark it ready and merge it. Merge is a release: everyone who uses the plugin gets the change.

### C · The hook fires

Start: `ckpt/0`, fresh session.

```
Fix the typo in Lakeshore's latest call notes.
```

Done when: the edit is refused with `accounts/ is source data. Write to briefs/ instead.` and Claude does not go around it with `sed`, a redirect or Python. The hook watches `Edit`, `Write` and `Bash`, in every permission mode. Try to break it: ask Claude to find another way, and read `.claude/hooks/guard-accounts.sh` to see why it holds.

### D · Same content, same file

Start: `ckpt/1` on `main`, `eh/lock-layout` from `origin/ckpt/lock-layout`. Fresh session.

```
Update my branch eh/lock-layout from main and tell me what changed.
```

Done when: `main` is merged in with no conflicts and Claude lists what arrived (the plugin folder). Then:

```
Render briefs/lakeshore-health from content/lakeshore-health.json twice, then compare the two files with shasum.
```

Done when: two identical hashes. The model decides what goes in `content/lakeshore-health.json`; the script fixes the headings, the order, the numbers table and the file. Then:

```
Add the hook and the render script to the renewal-kit plugin, commit, push and open a pull request.
```

Done when: the PR contains `plugins/renewal-kit/hooks/hooks.json` (using `${CLAUDE_PLUGIN_ROOT}`), the hook script, `render_brief.py` and the template inside the plugin.

### E · Three accounts, three helpers, one check

Start: `ckpt/3` (`briefs/` is empty). Fresh session. Do not read ahead in the account files; the point is what the check finds.

```
Brief all three accounts in parallel, one sub-agent per account on Sonnet, each using the acc-renewal-brief skill and writing briefs/<account>.md. Return only the path and three risks.
```

Done when: three briefs exist (`ls -la briefs/`) and you have nine one-line risks. Then:

```
Run scripts/check_briefs.py, fix what it flags, run it again.
```

Done when: the first run fails on one brief, Claude fixes the brief (never the source data; the hook stops that), and the second run prints `✓ 3 of 3 briefs pass`. Open `briefs/check-report.md`: that is the written record of what was checked.

### Optional · Commands

In a session: `/acc-brief mercy-valley`. In a plain shell from the repo root: `claude -p "/acc-brief northgate-partners"`. Look at `.claude/commands/acc-brief.md`: the `!` line runs before Claude sees the prompt, `$ARGUMENTS` is what you typed, and `disable-model-invocation` means only you can start it.

## If something goes wrong

- Reset to the exercise's checkpoint (table above) and start a fresh session.
- Close any PR you opened: `gh pr close <n> --delete-branch`.
- The hook needs `jq`; without it every edit is blocked on purpose.
- Keep the `SYNTHETIC DEMO DATA` banner on any file you add.

### If `/acc-brief` does something unexpected

Run `/skills` and check which `acc-brief` and `acc-renewal-brief` resolve to. A personal skill (`~/.claude/skills/`) with the same name overrides the repo's. Rename yours or ours.
