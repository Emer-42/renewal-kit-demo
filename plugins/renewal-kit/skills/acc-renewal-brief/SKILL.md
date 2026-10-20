---
name: acc-renewal-brief
description: Write the renewal brief briefs/<account>.md for one account in accounts/ (lakeshore-health, mercy-valley, northgate-partners) from its call notes, Jira export, prior-renewal notes and scripts/metrics.py. Use when someone asks for a renewal brief, an account brief or pre-call notes for one of these accounts. Do not use for pricing, for accounts outside accounts/, or to edit source data.
owner: Emerson Hernández
team: Client Analytics
---
<!-- SYNTHETIC DEMO DATA — every person and organisation here is made up. -->

# Renewal brief

Write `briefs/<account>.md` for Jordan, the client manager, who reads it for five minutes before the renewal call. `<account>` is the folder name under `accounts/`.

## Steps

1. Read every file in `accounts/<account>/`: `last-renewal-notes.md`, `jira-tickets.csv`, every `call-*.txt`, and `slack-account-channel.txt` if present. Commitments live in the calls, status and ownership in Jira, terms in the notes.
2. Get the numbers only from the script. Run it exactly like this and quote what it prints:

   ```
   python3 scripts/metrics.py <account>
   ```

   It prints the last 4 months (`--months N` widens the window), the first → last change, and the low/high so mid-window dips stay visible. Never compute or estimate a figure yourself. If the script fails, stop and report the error instead of writing a brief.
3. Write the brief under the six headings below, in this order, verbatim.
4. Re-read it against the rules before saving.

## Sections

Use exactly these six `##` headings, in this order:

```
## At a glance
## Numbers
## What went wrong
## Open issues
## Risks
## Gaps
```

- **At a glance**: renewal date and term, who changed on the client side, what is at stake. The data snapshot ends 26 Sep 2026; after that is unknown, not quiet.
- **Numbers**: cite the script and the window (for example `scripts/metrics.py`, Jun → Sep 2026). For digital payment rate, collection rate and PSAT state the latest month's value from the script output, and the first → last change. Call out dips the endpoints hide.
- **What went wrong**: facts tied to Jira keys.
- **Open issues**: a table with columns Ticket, Issue, Owner. Every row has an owner from Jira or says **no owner** in bold.
- **Risks**: three risks for the renewal, each ending with the ask for the call: a named person and a concrete commitment.
- **Gaps**: what the files do not say. List it; do not guess.

## Rules

- Under 400 words. One page.
- Start the file with the line `<!-- SYNTHETIC DEMO DATA — every person and organisation here is made up. -->`.
- No pricing: the files hold no fee, list price or per-statement rate, and the brief suggests none. Put pricing under Gaps.
- Only what is in the files. No options, no recommendations beyond the asks.
- Northgate Partners is a new client, not a renewal; say so in At a glance and flag the known September metrics conflict.
- Never edit anything under `accounts/`. It is source data.
