# Submittal and document statuses

Source: `backend/services/document_control_service.py`.

Use these words only when a stamp, log, or transmittal uses them. Do not upgrade a status.

| Status | Meaning in a draft |
|---|---|
| draft | Not issued |
| submitted | Sent, not returned |
| under_review | In review |
| approved | Stamp or log says approved, with no open notes |
| approved_as_noted | Approved only with the written notes. Quote the notes. |
| revise_resubmit | Returned for revision. Not a rejection essay. |
| superseded | An older revision. Do not treat it as current. |
| current | The revision the log or transmittal marks current |

If the log says Approved and the stamp says Approved as Noted, that is an approval-status conflict. Report both. Do not drop the notes.

This review is still not an engineering approval. Keep the do-not-approve sentence on every submittal note.
