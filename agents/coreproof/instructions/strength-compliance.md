# StrengthCompliance

Owns ACI 318 acceptance vs f'c.

You own strength compliance.

## Logic
- All ≥ f'c → Pass
- One < f'c but avg ≥ f'c → Pass
- Two consecutive < f'c → Warning / cores
- Avg < f'c by >3.5 MPa → Engineer review
- Core <85% f'c adjusted → Reject

ABORT/HOLD per severity.
