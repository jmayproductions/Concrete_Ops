# Skill — Detect conflicts

Instruction-level. Append to Daily PE Copilot instructions.

Conflicts are reported. They are never silently resolved. When two sources disagree and both sit near the same authority (within 15 points, or both at 70+), set confidence to BLOCKED and lead with **Potential RFI**.

## Types

| Type | What you saw | Severity | Next action |
|---|---|---|---|
| Revision | Same sheet, two revisions, different requirement | HIGH | Use the confirmed current revision. Flag the gap. |
| Drawing vs spec | Drawing and spec disagree | HIGH | Draft RFI. Do not pick a winner. |
| RFI vs drawing | An RFI response and a drawing disagree | MEDIUM | Check whether the RFI is the approved response for that item. |
| Submittal vs spec | Product in the package differs from the spec | HIGH | Spec controls unless a stamp explicitly approves the deviation. |
| Meeting vs contract | Minutes say the owner approved a change; no change document | MEDIUM | Ask the PM. Minutes do not create a change. |
| Quantity | Two counts for the same scope | MEDIUM | Report both. Do not average. |
| Date | Two logs give two due dates | LOW | Reconcile the logs. |
| Approval status | Log says Approved; stamp says Approved as Noted | MEDIUM | Read the notes. Do not drop the conditions. |
| Field vs design | Field note differs from the drawing or spec | HIGH | Draft RFI. Needs field verification if the note is thin. |

## How to report one

- conflict_type
- source A: title, type, authority, short excerpt
- source B: same
- what disagrees, in one sentence
- severity
- recommended action: VERIFY, DRAFT_RFI, CHECK_SPEC, ASK_PM, or UPDATE_LOG

## Exceptions

- An approved RFI response that clarifies one item controls that item. Note it as a revision, not a conflict.
- An approved submittal deviation is not a conflict when the stamp says the deviation is accepted.
- If one source is clearly higher authority (more than 15 points) and current, prefer it and say why. Still show the lower source.
- Two sections of the same document that disagree are still a conflict.
