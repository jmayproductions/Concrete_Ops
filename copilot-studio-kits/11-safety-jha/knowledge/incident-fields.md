# Incident note fields

Source of the field list: StructureOps `safety_incident_service.py`. The service sets `osha_recordable` from severity. **This agent does not.** Leave recordability UNKNOWN.

| Field | Fill when |
|---|---|
| Incident type | User said injury, near miss, property damage, environmental, or safety violation. Else blank. |
| Severity words | Copy the user’s words. Do not map them to fatality, days away, restricted duty, medical treatment, or first aid unless the user used those words. |
| Description | User’s account. Do not smooth it into a cause. |
| Location | User stated it. |
| When | User stated date and time. Else blank. Do not use “today” as a date. |
| Reported by | User’s name only if they gave it. |
| Injured person | Only if the user typed the name for this draft. |
| Body part | Only if stated: head, eyes, neck, back, shoulder, arm, hand, finger, leg, knee, foot, ankle, or multiple. |
| Witnesses | Names the user listed. |
| Immediate action | What the user said was done. |
| Photos | Only if the user attached them. |
| Recordable | UNKNOWN |
| Days away | blank |
| Restricted days | blank |
| Root cause | blank until a cited investigation states one |
| Status | DRAFT |

Do not create INC- or CA- numbers. A corrective-action line may be drafted only from an action the user stated, with status open and verification blank.
