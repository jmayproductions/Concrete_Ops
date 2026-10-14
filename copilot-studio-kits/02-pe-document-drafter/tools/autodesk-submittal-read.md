# Tool contract — Autodesk submittal read

Read submittal items in one Autodesk Construction Cloud project. Do not create, submit, or review them.

Official reference: Construction Submittals API v2. `GET /construction/submittals/v2/projects/{projectId}/items` and `GET /construction/submittals/v2/projects/{projectId}/items/{itemId}`.

Creating an item is `POST .../items` and requires `data:write`. This contract does not call it.

## Auth

Same 3-legged user token as the kit 01 issue and RFI reads. Scopes `data:read` and `account:read`. No `data:write`.

Project id comes from the Data Management API with the `b.` prefix removed. Do not guess it.

## Allowed calls

| Call | Purpose |
|---|---|
| `GET /construction/submittals/v2/projects/{projectId}/items?limit=20` | Short list. Add a filter only from the user's number, title, spec section, or package |
| `GET /construction/submittals/v2/projects/{projectId}/items/{itemId}` | One item the list already returned |
| `GET /construction/submittals/v2/projects/{projectId}/responses/{responseId}` | The review response, only when that item payload includes the response id |

`limit` stays at or below 20. Follow the next page only when the user asks.

Attachment names may be cited when the item payload includes them. Do not download attachment bytes. The spec and the shop drawing still have to be opened by the user or returned by the SharePoint read.

## Fields the agent may cite

Cite a field only when it is in the JSON: identifier, title, revision, spec section, status text, due date, submitter, manager, response text.

If the payload has a status id and no status words, report the id. Do not translate a number into approved, approved as noted, or rejected.

If the payload's own words say approved or approved as noted, quote those words and quote any notes. Then still print the do-not-approve sentence from `skills/draft-not-approve.md`. Quoting the log is not this agent approving the package.

A missing response means the review has not come back. Status stays DRAFT or BLOCKED. Do not tell procurement the item is clear to buy.

## Refusals

- No create, no submit, no response, no comment, no attachment upload.
- `403` or `404`: the signed-in user cannot see that item.
- Do not invent a submittal number, a spec section, a revision, or a stamp.
