# Tool contract — Autodesk RFI read

Read RFIs in one Autodesk Construction Cloud project. Do not create, answer, or submit them.

Official reference: Forma Build RFIs API v3, general availability. Base path `/construction/rfis/v3/projects/{projectId}`.

Do not call the deprecated BIM 360 path `/bim360/rfis/v2/`.

## Auth

Same 3-legged user token as the issue contract. Scopes `data:read` and `account:read`. No `data:write`.

Project id has no `b.` prefix. Do not guess it.

## Allowed calls

| Call | Purpose |
|---|---|
| `POST /construction/rfis/v3/projects/{projectId}/search:rfis` | List or search. Body is `{}` for a short list, or a filter built only from the user's number, title, or status |
| `GET /construction/rfis/v3/projects/{projectId}/rfis/{rfiId}` | One RFI the search already returned |

The search call is a POST because Autodesk defined search that way. The body must not create an RFI. Do not call `POST /rfis` or `PATCH /rfis/{id}`.

Ask for at most 20 RFIs. Do not page the whole project log unless the user asks for the next page.

## Fields the agent may cite

Cite a field only when it is in the JSON: identifier, title, status, question, official response text, assignees (ball in court), due date.

If the official response is missing, say so. An open RFI is not the design.

An official response on a closed or answered RFI may be cited as the current answer for that question. It still does not approve a submittal, a cost, or a schedule change.

## Refusals

- No create, no response, no comment, no attachment upload.
- `403` or `404`: the signed-in user cannot see that RFI.
- Do not invent an RFI number, a due date, or a design-team answer.
