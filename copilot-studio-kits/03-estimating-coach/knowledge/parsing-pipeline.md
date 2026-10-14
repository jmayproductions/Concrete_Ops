# Parsing pipeline card

Source: `estimation/docs/intelligence/blueprint_parsing_pipeline.md`. This is the measurement chain. You do not run it. You name the stage that failed and you refuse to invent the missing number.

```text
PDF → render (default 300 DPI) → cleanup → OCR
  → dimension parse → scale → pixels to real units
  → link dimension to a line → count symbols
  → close room polygons → takeoff rollup → price
```

| Stage | Stop when |
|---|---|
| OCR | Text was overwritten, or confidence is too low to read a dimension |
| Dimension | Feet, inches, or a fraction did not parse |
| Scale | No scale, two scales, or the sheet is NTS. Code: `SCALE_NOT_FOUND` |
| Pixels to real units | Scale is not verified. Do not emit feet, SF, or CY |
| Link | A dimension is not tied to a line. Leave it unmatched |
| Symbols | A count has no method and no confidence |
| Area | The polygon is open, unlabeled, or it is furniture or a detail symbol |
| Rollup | The line has no unit, no method, or no source |
| Price | Unit clash: `COST_UNIT_MISMATCH`. No price file: `COST_NO_SOURCE` |

A takeoff line that survives rollup has: description, CSI or `UNMAPPED`, quantity, unit, method (`counted`, `measured`, `calculated`, `scheduled`, `assumed`, `allowance`), source refs, confidence, review status, warnings.

Direct cost is material + labor + equipment + subcontract. Tax, overhead and profit, contingency, escalation, and allowances are separate lines with a stated rate. You do not compute a new price in chat.
