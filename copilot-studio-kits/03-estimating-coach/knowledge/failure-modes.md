# Estimating failure modes (coach view)

| Stage | Failure | What you tell the user |
|---|---|---|
| OCR | Fraction or quotes misread | Do not trust the number until a human rereads the dimension |
| Scale | None / conflict / NTS | Stop measuring |
| Dimension | Unrealistic length | Range-check; do not price it |
| Count | Plan ≠ schedule | Report both; do not average |
| Area | Unclosed room / void counted | Flag geometry; do not invent SF |
| Cost | Missing, $0, or stale data | COST_NO_SOURCE — never hide a zero |
| Cost | Invented fallback price | Forbidden |
| Export | Warnings dropped | Defect — restore the warnings field |

This agent does not run OCR. If the user pastes OCR text, treat numbers as LOW confidence until verified.
