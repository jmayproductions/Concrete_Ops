# Procurement status

Source: `ProcurementStatus` and `DeliveryCondition` in `procurement_tracking_service.py`.

requisition → rfq_issued → quotes_received → vendor_selected → po_issued → in_fabrication → ready_to_ship → in_transit → delivered → inspected → accepted or rejected.

Move a draft forward only when a log, PO, or ticket supports the new word. Do not skip to accepted.
