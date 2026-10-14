# Workflow — Read, then answer

1. User asks one PE question.
2. Agent classifies the lane.
3. If the question needs a project file, call SharePoint library read on the one PE site.
4. If the question names an Autodesk issue, call issue read.
5. If the question names an RFI, call RFI read.
6. Cite the returned fields in the answer contract.
7. If the call is empty, 403, or the tool is not connected: **Insufficient evidence**. Ask for the file. Do not guess.
8. Do not write back to SharePoint or Autodesk.
