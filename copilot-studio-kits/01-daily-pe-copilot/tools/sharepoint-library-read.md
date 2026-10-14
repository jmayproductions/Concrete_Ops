# Tool contract — SharePoint library read

Read one project PE site. This is the first tool for kit 01.

## Copilot Studio setup

1. Add the SharePoint knowledge source.
2. Point it at one site the firm names for this pilot. Example shape: `https://{tenant}.sharepoint.com/sites/{pe-site}`.
3. Leave every other site off.
4. The connector runs as the signed-in user. The agent sees only files that user can already open.

Do not use an app-only token. An app-only token can read sites the user cannot.

## Allowed calls

Microsoft Graph, delegated, read:

| Call | Purpose |
|---|---|
| `GET /sites/{hostname}:/sites/{site-path}` | Resolve the one site |
| `GET /sites/{site-id}/drive/root/search(q='{query}')` | Find a file in that site's library |
| `GET /sites/{site-id}/lists/{list-id}/items?$expand=fields` | Read a named log list on that site, when the list exists |

Search query comes from the user's words: spec section, sheet number, RFI number, or file name. Do not search the tenant.

## Fields the agent may cite

File: name, web URL, parent path, last modified time.

List item: only columns the list returns. Typical PE columns are number, title, status, spec section, due date, ball in court. If a column is absent, leave it blank.

## Refusals

- No create, update, delete, share, or permission change.
- No second site "to be helpful."
- Empty search is **Insufficient evidence**. Do not fill the gap with general knowledge and call it the project spec.
- A file the user cannot open is not a source. Say the signed-in user cannot open it.
