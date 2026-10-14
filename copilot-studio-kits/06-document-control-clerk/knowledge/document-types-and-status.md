# Document types and status

Source: `backend/services/document_control_service.py`.

## Types

drawing, specification, submittal, shop_drawing, rfi_response, change_order, meeting_minutes, transmittal, test_report, o_and_m_manual, warranty, as_built.

## Status

draft, submitted, under_review, approved, approved_as_noted, revise_resubmit, superseded, current, archived.

Use a status only when a log, stamp, or transmittal uses it.

`approved_as_noted` keeps the notes. Dropping the notes is an error.

Meeting minutes and daily reports do not create contract requirements.
