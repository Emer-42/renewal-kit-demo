<!-- SYNTHETIC DEMO DATA — every person and organisation here is made up. -->
# Northgate Health Partners — account brief for Kim

**Not a renewal.** Northgate signed in March 2026 on an 18-month initial term. Go-live was planned for August and has slipped to October because Northgate IT is behind on the payment-plan integration (22 Sep call). Lena Ortiz (Revenue Cycle Manager) says her CFO is asking why they're paying for a platform they aren't fully using. You offered to shift the first billing period to match go-live, and Lena asked for that in writing. Files end 26 Sep.

## Numbers (`scripts/metrics.py`, Aug → Sep 2026; only 2 months in file)
- Statements sent: 0 → 4,200.
- September only: digital payment rate 41%, collection rate 61%, PSAT 77, support calls 610. August is blank, so there is no trend.
- **Data conflict:** `metrics.csv` shows 4,200 statements and full rates for September, but the 22 Sep call says go-live slipped to October. The files don't reconcile this. Don't quote these numbers to Lena until the conflict is resolved.

## What went wrong
- Go-live missed August. The call puts the cause on Northgate IT and the payment-plan integration.
- NHP-301 (payment-plan integration) is In Progress at Highest priority with no assignee, so nobody on Cedar's side is named.
- The written billing-shift proposal Lena asked for is still Open (NHP-302).

## Open issues
| Ticket | Issue | Owner |
|---|---|---|
| NHP-301 | Payment-plan integration (blocking go-live) | **no owner** |
| NHP-302 | Written proposal: shift first billing period to go-live | Kim Patel |

## Gaps (not in the files)
- Contract fee, billing schedule, and term start/end dates (only "18-month initial term").
- Exact October go-live date and Northgate's IT owner for the integration.
- Whether September statements were a pilot, a partial launch, or a data error.
- Whether the CFO has to approve the billing shift, and by when.
- Anything after 26 Sep.

## Asks for the call
1. **Lena Ortiz:** confirm the October go-live date and name Northgate's IT owner for the payment-plan integration.
2. **Lena Ortiz:** confirm whether Northgate sent any statements through Cedar in September, to reconcile the 4,200 in `metrics.csv`.
3. **Kim Patel** (before the call): name a Cedar owner for NHP-301 and send Lena the written billing-shift proposal (NHP-302).
