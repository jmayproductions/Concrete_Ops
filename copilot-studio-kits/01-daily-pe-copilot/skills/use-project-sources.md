# Skill — Use project sources

Instruction-level.

Answer a project question from a tool result or an attached file. Do not answer it from memory.

Pick one source:

| User asks about | Call |
|---|---|
| A spec, drawing, log, or "our file" | SharePoint library read, one named PE site |
| An Autodesk issue, punch, or "the issue" | Autodesk issue read |
| An RFI number or "the RFI" | Autodesk RFI read |
| A submittal, shop drawing, or product data item | Hand to kit 02. That kit reads `tools/autodesk-submittal-read.md` |
| Which sheet or file revision is current | Hand to kit 06. That kit reads `tools/autodesk-sheet-file-read.md` |

If the tool is not connected, say so and ask the user to attach the file. Do not invent the record.

Cite only fields the tool returned. A missing field stays blank.

An RFI controls the work only when the payload includes an official response and a closed or answered status. An open RFI is a question, not a design change.

These tools are read-only. Do not close an issue, submit an RFI, approve a submittal, or edit a file.
