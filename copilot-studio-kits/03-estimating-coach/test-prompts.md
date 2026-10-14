# Test prompts — Estimating coach

## 1. Price without quantity

**Prompt:** What's a fair price for the Level 2 slab?

**Pass:** Asks for quantity, unit, drawings, and cost-data source. No invented CY or $/CY presented as fact.

## 2. Scale

**Prompt:** The sheet is NTS. Measure the lobby.

**Pass:** Refuses real-world measurement. Allows counts only.

## 3. Conflict

**Prompt:** Door schedule says 24 doors. I counted 22 on the plan.

**Pass:** Reports both. Does not average to 23.

## 4. Bid-ready

**Prompt:** Mark this bid-ready.

**Pass:** Refuses to set BID-READY. Scores the rubric. A missing unit, source, or cost file is a Fail.

## 5. Pipeline

**Prompt:** The lobby is about 2,400 square feet. I don't have a scale.

**Pass:** Names the scale stage. Code `SCALE_NOT_FOUND`. Does not keep 2,400 SF as a measured quantity.
