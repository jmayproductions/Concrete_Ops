# Transmittal fields

Source: `create_transmittal` and `acknowledge_transmittal` in `document_control_service.py`.

- transmittal_number
- from_party
- to_party
- subject
- purpose
- documents: id or number, revision, title
- notes
- transmitted_date
- received_date
- received_by

Purpose examples the service allows: For Review, For Approval, For Construction, plus whatever the project form uses.

A transmittal draft does not change document status to approved.
