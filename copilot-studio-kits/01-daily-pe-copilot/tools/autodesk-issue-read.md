# Tool contract — Autodesk issue read

Read issues in one Autodesk Construction Cloud project. Do not create or close them.

Official reference: Autodesk Platform Services, Construction Issues API v1. `GET /construction/issues/v1/projects/{projectId}/issues`.

The vendored bulk uploader under `utils/aps-hubs-bulk-files-manager-main` moves files. It is not this tool.

## Auth

3-legged OAuth, authorization code, as the signed-in user.

Scopes: `data:read` and `account:read`. Do not request `data:write`.

Do not use a 2-legged service account for this pilot. That token can see hubs the user cannot.

## Project id

Take the project id from the Data Management API. Issues calls use that id **without** the `b.` prefix.

Do not guess a project id. If the user did not name the project and no default project is configured for this agent, ask.

Send `Authorization: Bearer` and `Accept: application/json`. Send `x-ads-region` only when the firm's hub region is already known. Do not default it.

## Allowed calls

| Call | Purpose |
|---|---|
| `GET /construction/issues/v1/projects/{projectId}/issues?filter[search]={text}&limit=20` | Find issues by the user's words or number |
| `GET /construction/issues/v1/projects/{projectId}/issues/{issueId}` | One issue the list already returned |

`limit` stays at or below 20. Follow `offset` only when the user asks for the next page.

## Fields the agent may cite

Cite a field only when it is in the JSON: the human-readable number, title, description, status, due date, assignee, location. Quote the description. Do not rewrite it into a cause.

## Refusals

- No `POST` or `PATCH`. "Close this issue" is a refusal. The next action is the user closing it in Autodesk.
- `403` or `404`: the signed-in user cannot see that issue. Do not retry with another token.
- Do not treat an issue status as design approval, a code ruling, or a cost.
