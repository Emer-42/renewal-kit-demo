# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Not a code project. `renewal-kit/` is a folder of **synthetic** customer-account material (call transcripts, an internal Slack log, Jira exports, monthly metrics, prior-renewal notes) used to prepare renewal briefs for Cedar's account team. There is no build, lint, or test tooling and no README. It is not a git repository, though a `.gitignore` exists (ignores `.DS_Store`, `__pycache__/`, `compare/`; the last two don't exist yet and their purpose isn't documented).

Every file starts with a `SYNTHETIC DEMO DATA` banner (HTML comment in `.md`, first line in `.txt`; the CSVs have none). Keep it on any new prose or transcript file. The data snapshot ends 26 Sep 2026 (latest Jira `updated`), so anything after that is unknown, not "nothing happened".

## Layout

```
accounts/<slug>/
  last-renewal-notes.md      # baseline terms, champion, risks from the previous renewal or signing
  metrics.csv
  jira-tickets.csv
  call-MM-DD-<topic>.txt     # one transcript per call, all 2026
  slack-account-channel.txt  # marked internal; Lakeshore only
```

| Account (Jira prefix) | Stage | Cedar owner | Key date |
|---|---|---|---|
| lakeshore-health (LKH) | Renewal, at risk | Jordan Lee | Renews 31 Oct 2026 |
| mercy-valley (MVM) | Renewal + expansion | Kim Patel | Renews 30 Nov 2026 |
| northgate-partners (NHP) | **New client, not a renewal** (signed Mar 2026, 18-month term) | Kim Patel | Go-live slipped Aug → Oct 2026 |

Northgate's `last-renewal-notes.md` is really its signing notes. Other Cedar staff: Sam Ortiz (Client Analyst), Riley Chen (Reporting Ops). Lena Ortiz (Northgate) and Sam Ortiz (Cedar) are different people.

## Data formats

- `metrics.csv`: `month,statements_sent,digital_payment_rate,collection_rate,psat,support_calls`. Rates are fractions (`0.64` = 64%). The window differs per account (Lakeshore Mar–Sep, Mercy Valley Jul–Sep, Northgate Aug–Sep). Blank cells mean not applicable yet, not zero.
- `jira-tickets.csv`: `key,summary,status,priority,assignee,updated,labels`. Labels are `;`-separated. An empty `assignee` means unowned. Statuses seen: Open, In Progress, In Review, Done, Won't Do.
- Transcripts: header block (call, date, attendees grouped by org), then `[mm:ss] Speaker: text`. Lakeshore calls end with Jordan's `Recap:` line listing commitments; the other accounts' calls don't.

## How the files fit together

Commitments and customer asks live in call transcripts, status and ownership in Jira, numbers in `metrics.csv`, and contract terms in `last-renewal-notes.md`. A brief joins them, so a task usually means reading several of these and reconciling. They can disagree (e.g. Riley committed on 3 Sep to an automated count check by 20 Sep, but LKH-112 is still Open and unassigned).

The brief format is defined by the `renewal-brief` skill (`.claude/skills/renewal-brief/SKILL.md`): exactly six `##` headings, in this order, verbatim:

1. `## At a glance`: renewal date and term, who changed, what's at stake.
2. `## Numbers`: window and source stated, latest month's value and first → last change for each rate, and mid-period dips that the endpoints hide are called out.
3. `## What went wrong`: facts tied to ticket keys.
4. `## Open issues`: table (ticket / issue / owner), with unowned items in bold.
5. `## Risks`: three risks, each ending with the ask for the call: a named person and a concrete commitment.
6. `## Gaps`: unknowns are listed rather than guessed.

`scripts/check_briefs.py` checks every `briefs/*.md` for the six headings and for rate/PSAT figures that match `metrics.csv`, and writes `briefs/check-report.md`.

The files contain no contract fee, list price, or per-statement pricing. Don't invent any; list them under Gaps.

## Brief rules

- **Audience and length:** Jordan, the client manager, reading for 5 minutes before the renewal call. One page, under 400 words.
- **Location:** save as `briefs/<account>.md`, using the account folder name as `<account>`.
- **Sources:** only what's in the files. No pricing models and no suggested options.
- **Numbers:** compute them from `metrics.csv`; never estimate. If something isn't in the files, list it under Gaps.
- **Numbers source:** brief numbers come from `python3 scripts/metrics.py` (last 4 months per account, first → last change, low/high to expose dips; `--months N` widens the window). Cite the script and window in the brief.
- **Open issues:** every one needs an owner, or **no owner** in bold.
- **Headings:** the six from the skill, verbatim and in order. `## Risks` ends with 3 asks for the call, each with a name.
- **Check:** run `python3 scripts/check_briefs.py` after writing or changing a brief.
- **Data:** synthetic only.

## Known data inconsistency

Northgate's `metrics.csv` has 4,200 statements and full rates for 2026-09, but the 22 Sep call says go-live slipped to October. The files don't reconcile this, so flag it instead of explaining it away.
