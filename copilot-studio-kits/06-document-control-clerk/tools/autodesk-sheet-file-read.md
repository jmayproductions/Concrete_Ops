# Tool contract — Autodesk sheets and files read

Read the sheet set and the Docs files in one Autodesk Construction Cloud project. Do not publish, upload, delete, or mark a revision current.

Two collections. Do not mix their project ids.

| Collection | What it is | Project id |
|---|---|---|
| Build Sheets | Published sheets and version sets | UUID **without** the `b.` prefix |
| Docs files | Files and folders in Autodesk Docs | Data Management id **with** the `b.` prefix |

Official references: Forma Build Sheets API v1 (`GET /construction/sheets/v1/projects/{projectId}/sheets`, `GET .../version-sets`) and Data Management API v1 (`GET /data/v1/projects/{project_id}/folders/{folder_id}/contents`). A sheet in Build is not a Docs item. Do not call the Data Management versions endpoint to explain a Build sheet.

## Auth

Same 3-legged user token as the other kit 01 reads. Scopes `data:read` and `account:read`. No `data:write`.

The Sheets API also accepts a 2-legged token. Do not use one. It can see projects the signed-in user cannot.

Do not guess a project id, a folder id, or a version-set id.

## Allowed calls — sheets

| Call | Purpose |
|---|---|
| `GET /construction/sheets/v1/projects/{projectId}/version-sets?limit=20` | Version sets. Cite name and issuance date when present |
| `GET /construction/sheets/v1/projects/{projectId}/sheets?currentOnly=true&limit=20` | Sheets Autodesk marks current. Add `filter[versionSetId]` only when a returned version set matches the user's issuance |
| `GET /construction/sheets/v1/projects/{projectId}/sheets?limit=20` | One page when the user asks for sheets that are not marked current |

`limit` stays at or below 20. Follow the next page only when the user asks.

If the user names a sheet number, cite a row on that page whose number matches. If the page does not contain it, say so. Do not walk the whole set.

## Allowed calls — files

| Call | Purpose |
|---|---|
| `GET /data/v1/projects/b.{projectId}/folders/{folderId}/contents?page[limit]=20` | One known folder |
| `GET /data/v1/projects/b.{projectId}/folders/{folderId}/search?filter[displayName]={name}&page[limit]=20` | Find a file by the name the user gave, inside a known folder and its subfolders |
| `GET /data/v1/projects/b.{projectId}/items/{itemId}/versions?page[limit]=20` | Versions of an item the contents or search call already returned |

The tip version in a folder response is the latest stored file. It is not the revision to build from unless a version set, drawing log, or transmittal says so.

## Fields the agent may cite

Sheets: number, title, version-set name, issuance date, and whether this call used `currentOnly=true`.

Files: display name, version number or label the payload returns, last modified time, folder path when present.

Leave a blank field blank. Do not invent a revision letter from the file name.

## Refusals

- No upload, storage, signed URL, publish, patch, delete, or restore.
- `403` or `404`: the signed-in user cannot see that sheet or file.
- A later letter, a higher version number, or a newer modified time does not make a revision current.
- `currentOnly=true` may be quoted as Autodesk's mark for that collection. It is not an engineering stamp and it does not approve the work.
- If two version sets or two files both claim the same sheet, report both. Do not pick.
