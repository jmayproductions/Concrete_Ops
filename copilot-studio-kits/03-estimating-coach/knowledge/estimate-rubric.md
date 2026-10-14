# Estimate quality rubric

Source: `estimation/docs/intelligence/rubrics.md`. Use this when the user asks for a review, a score, or bid readiness.

## Quantity and cost

| Criterion | Pass | Needs work | Fail |
|---|---|---|---|
| Units | Every quantity has a unit | A unit is ambiguous | A quantity has no unit |
| Method | Each line is counted, measured, calculated, scheduled, assumed, or allowance | A method was inferred and labeled | No method |
| Source | Each line cites a sheet, spec, schedule, assumption, or allowance | Some lines are uncited | No sources |
| Scale | Scale is confirmed against a known dimension | Scale is assumed | No scale, or NTS used for real units |
| Cost source | Each priced line has source, date, and location | A priced line is missing one of those | No cost source, or a price was invented |
| Markups | Each markup shows rate and basis | A markup is implied | A markup is hidden |
| Assumptions | Written down | Some are only in prose | No assumptions log |
| Exclusions | Written down | Partial | No exclusions log |
| Warnings | Shown, including `SCALE_NOT_FOUND`, `COST_UNIT_MISMATCH`, `COST_NO_SOURCE` | A warning was dropped | No warnings on a file that should have them |
| Review status | `review_required` and `bid_ready` are set | One flag is missing | No review status |

## Score

- **Pass:** every row passes.
- **Partial:** 1–3 rows are Needs work, and none fail.
- **Fail:** any row fails, or 4 or more rows are Needs work.

A Fail or Partial score stays **not bid-ready**. Only a person can set bid-ready after the source documents, scale, quantities, cost data, assumptions, exclusions, alternates, allowances, risks, and totals have been reviewed.

## Report sections

Also check: project name, date, revision, and basis; quantity summary; cost summary that reconciles; assumptions; exclusions; risks; review status. A missing section is a Fail for that section.
