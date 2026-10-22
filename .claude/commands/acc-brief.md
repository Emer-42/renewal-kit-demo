---
description: Renewal brief for one account
argument-hint: [account]
allowed-tools: Bash(git log *)
disable-model-invocation: true
---
Recent changes to the account files:
!`git log --oneline -3 -- accounts/ 2>/dev/null || true`

Write the renewal brief for $ARGUMENTS,
following the acc-renewal-brief skill.
