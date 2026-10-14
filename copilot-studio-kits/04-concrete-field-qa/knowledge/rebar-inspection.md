# Checklist — Rebar inspection

Source: `modules/field_ops/qaqc_engine.py` template `rebar_inspection`. Priority and cited standard are templates.

| Item | Category | Priority | Standard |
|---|---|---|---|
| Rebar size matches drawings | rebar | critical | ACI |
| Spacing within tolerance | rebar | critical | ACI |
| Lap splices meet code | rebar | critical | ACI |
| Chairs and supports adequate | rebar | high | — |
| Rust and contamination check | rebar | medium | — |
| Epoxy coating intact (if specified) | rebar | medium | — |

Project drawing and spec govern size, spacing, lap, and cover. If those files are not attached, mark size/spacing/lap **Unknown** and do not pass them.
