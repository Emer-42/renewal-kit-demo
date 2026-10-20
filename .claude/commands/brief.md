---
description: Renewal brief for one account
argument-hint: [account]
allowed-tools: Bash(git log *)
disable-model-invocation: true
---
Recent changes to the account files:
!`git log --oneline -3 -- accounts/`

Write the renewal brief for $ARGUMENTS,
following the renewal-brief skill.
