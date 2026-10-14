# Safety flags

Emit the matching flag in Risks when the condition is true.

| Flag | When | Effect |
|---|---|---|
| NO_RELEVANT_EVIDENCE | No usable source | BLOCKED |
| ONLY_SUPERSEDED_EVIDENCE | All sources superseded | Cap LOW |
| CONFLICTING_EVIDENCE | Authoritative sources disagree | BLOCKED + Potential RFI |
| MISSING_SOURCE_CITATION | HIGH/MEDIUM answer has no citation | Downgrade |
| UNSUPPORTED_QUANTITY | Number not in a source | Downgrade |
| UNSUPPORTED_DATE | Date not in a source | Warn |
| UNSUPPORTED_APPROVAL | Claims approved/rejected without source | BLOCKED |
| UNSUPPORTED_COST_IMPACT | Dollar or cost claim without source | BLOCKED |
| UNSUPPORTED_SCHEDULE_IMPACT | Delay/duration claim without source | Cap LOW |
| ENGINEERING_JUDGMENT_REQUIRED | Structural or design adequacy | BLOCKED |
| LEGAL_OR_CODE_AUTHORITY_REQUIRED | Legal or code compliance claim | BLOCKED |
| FIELD_VERIFICATION_REQUIRED | Depends on unverified field condition | Cap MEDIUM |
| RFI_RECOMMENDED | Gap or conflict | Flag next action |
| GENERIC_KNOWLEDGE_ONLY | Only general practice | Cap LOW and label it |
| OCR_UNCERTAINTY | Source looks like bad OCR | Cap MEDIUM |

An answer is ready for a human to act on only when confidence is HIGH or MEDIUM and no BLOCKING or HIGH flag is present. Most answers stay drafts.
