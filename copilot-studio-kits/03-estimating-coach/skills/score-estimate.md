# Skill — Score the estimate

Instruction-level.

When the user asks for a review or bid readiness, score `knowledge/estimate-rubric.md`.

1. Walk each criterion. Mark Pass, Needs work, or Fail. Say which line or section caused it.
2. Apply the score rule. Any Fail, or four Needs-work rows, is Fail.
3. Name the pipeline stage from `knowledge/parsing-pipeline.md` when a quantity has no trustworthy source.
4. Put CSI from `knowledge/csi-divisions.md` on each line, or `UNMAPPED`.
5. Leave `bid_ready` false. Say review_required.

Do not fill missing quantities or prices in order to improve the score.
