# Agent-usable construction data (found inventory)

This index lists **construction agent data already available** for Copilot Studio swarms: failure RAG corpora, Copilot authoring kits, field SOPs/guides, and the PE build sheet. Windows paths like `S:\Swinerton\Manuals` / `S:\Swinerton\KBs` are the on-disk originals; Google Drive holds working copies of the RAG JSON and kits.

## A. Copilot Studio authoring kits (this folder)

12 agents + shared law. Paste into Copilot Studio → publish → **Download .zip** → admin upload.

| Kit | Swarm role | Core workflows |
|---|---|---|
| 01 Daily PE Copilot | Parent / router | `ask-one-pe-task`, `read-then-answer` |
| 02 PE document drafter | Child / sibling | `draft-then-review` (RFI, submittal, NCR, …) |
| 03 Estimating coach | Separate agent | `estimate-review-pass` |
| 04 Concrete field QA | Field child | `pre-pour-gate` |
| 05 Trade/role shells | Child agents | `multi-agent-handoff` |
| 06 Document-control clerk | Sibling of 01 | `revision-intake` |
| 07 AHJ permit tracker | Sibling of 01 | `failed-inspection` |
| 08 Closeout pack | Sibling of 02 | `turnover-gap-list` |
| 09 Procurement / long-lead | Sibling of 01 | `release-gate` |
| 10 Tilt-up field QA | Sibling of 04 | `panel-gate` |
| 11 Safety / JHA | Sibling of 05 | `jha-before-task` |
| 12 Field failure cards | Symptom router | `symptom-to-card` |

Shared law (`_shared/`): ironclad law, answer contract, evidence tiers, confidence rules, safety flags, Studio mapping.

**Build → zip → download (established path):** see [INSTALL.md](INSTALL.md) and [SWARM.md](SWARM.md).

Drive source zip: [copilot-studio-kits.zip](https://drive.google.com/file/d/1mLBB67CuRSp492GJxJy2vBXlu9S3VEPB/view)

## B. Field-failure RAG corpora (primary agent knowledge)

Master manifest: `construction_rag_master_manifest_v1.json`  
Drive: https://drive.google.com/file/d/1aNdNvo95t4tIGtsYg2VPEM8RNIDo9oSK/view

| | |
|---|---|
| Modules | **33** |
| Issue records | **2,209** |
| Declared sources | **1,523** |
| Archive name | `construction_rag_complete_bundle_v1.zip` (referenced by manifest; not found as a single Drive file in this pass) |
| On-disk home | `S:\Swinerton\KBs` (JSON issue files). Kit 12 markdown cards are the Studio upload surface; leave full JSON in KBs / Drive. |

### Modules (filename → records)

| File | Records | Use for agents |
|---|---:|---|
| `backsight_prism_tripod_failures_rag_v1.json` | 64 | Layout / survey |
| `below_grade_waterproofing_vapor_waterstop_failures_rag_v1.json` | 64 | Envelope / below-grade (no kit-12 card yet) |
| `bim_to_field_ar_mr_layout_failures_rag_v1.json` | 64 | BIM-to-field / AR |
| `bim_vdc_model_coordination_clash_constructability_failures_rag_v1.json` | 64 | VDC / clash |
| `cad_bim_coordinate_transform_failures_rag_v1.json` | 64 | Coordinates / datum |
| `cmu_masonry_layout_grout_bracing_failures_rag_v1.json` | 64 | Masonry |
| `concrete_geometry_tolerance_asbuilt_failures_rag_v1.json` | 64 | Concrete as-built |
| `concrete_placement_curing_testing_failures_rag_v1.json` | 64 | Placement / cure |
| `concrete_pour_placement_curing_testing_failures_rag_v1.json` | 64 | Pre-pour → acceptance |
| `concrete_scanning_slab_penetration_failures_rag_v1.json` | 64 | Scanning / coring |
| `controller_communications_sync_storage_failures_rag_v1.json` | 64 | Controller / sync |
| `drone_uas_construction_mapping_progress_failures_rag_v1.json` | 64 | Drone / UAS |
| `elevation_delta_measurement_issues_rag_v1.json` | 68 | Elevations |
| `exterior_envelope_fenestration_waterproofing_failures_rag_v1.json` | 64 | Envelope / fenestration |
| `formwork_shoring_reshoring_failures_rag_v1.json` | 64 | Formwork / shores |
| `interior_framing_drywall_ceiling_failures_rag_v1.json` | 64 | Framing / drywall |
| `layout_pole_prism_failures_rag_v1.json` | 64 | Pole / prism |
| `layout_qaqc_asbuilt_verification_failures_rag_v1.json` | 64 | Layout QA/QC |
| `mep_sleeve_embed_penetration_coordination_failures_rag_v1.json` | 64 | MEP embeds |
| `occupied_total_station_setup_failures_rag_v1.json` | 64 | Occupied setup |
| `post_tensioning_failures_rag_v1.json` | 64 | PT |
| `precast_tiltup_erection_connection_failures_rag_v1.json` | 64 | Precast / tilt-up |
| `reality_capture_pointcloud_scantobim_failures_rag_v1.json` | 64 | Scan-to-BIM |
| `reinforcing_steel_dowel_coupler_failures_rag_v1.json` | 64 | Rebar |
| `resection_geometry_issues_rag_v1.json` | 64 | Resection |
| `robotic_tracking_search_lock_failures_rag_v1.json` | 64 | Robotic lock |
| `roofing_drainage_flashing_failures_rag_v1.json` | 64 | Roofing |
| `site_control_setup_failures_rag_v1.json` | 87 | Site control |
| `stakeout_software_delta_interpretation_failures_rag_v1.json` | 64 | Stakeout deltas |
| `structural_steel_erection_connection_failures_rag_v1.json` | 64 | Structural steel |
| `total_station_calibration_environment_failures_rag_v1.json` | 64 | Calibration / EDM |
| `total_station_layout_problems_rag_v1.json` | 134 | Total-station layout |
| `underground_utility_locating_gpr_potholing_failures_rag_v1.json` | 64 | Utility locate / GPR |

**Ingestion rules (from manifest):** one issue object = preferred retrieval chunk; key with `dataset_id` + `issue_id`; forum/incident sources are recognition evidence, not approval authority; verify SHA-256 before production ingest.

Most modules also exist as Google Drive JSON (search Drive for `*_failures_rag_v1.json`). Kit 12 markdown cards already point at these filenames.

## C. Field / VDC SOP & training docs (Drive) — agent knowledge uploads

| Doc | Drive |
|---|---|
| COPILOT AGENT BUILD SHEET | https://docs.google.com/document/d/1it_GT9VDMU1F3vvJMz-q5gg7ZBtrZKjhDPnSCHhv9Kg/edit |
| AUTHORITATIVE FIELD TRAINING GUIDE | https://docs.google.com/document/d/1pePkHbvPuvi46OA53y6sSG6w7JEDi9J-gfAoDqY8Y44/edit |
| HP SITEPRINT ROBOT FIELD LAYOUT SOP | https://docs.google.com/document/d/1Im1ySGA2WSYVzbPADEYg8yl0nokLjgOPC70EVHv2sAM/edit |
| PERFECT FIELD LAYOUT WITH A TOTAL STATION | https://docs.google.com/document/d/1q8VAqlcC_sbeH73E1q7KhTHVMfsCCeHAjWBsOoFRe5c/edit |
| GUIDE 1 — AutoCAD (field→VDC) | https://docs.google.com/document/d/14gRHthZz8mDIYZg9eUAPMpE_raJrrOk3_5kpaG0TaPY/edit |
| GUIDE 2 — Revit | https://docs.google.com/document/d/1M8OpGtItYtqLuaKe7p57J4h5mdhcLcoK-tcnDW-CWBU/edit |
| GUIDE 3 — Navisworks | https://docs.google.com/document/d/1enoOvn9HIdWKnwb2NeAc0OV6o2Eo1812OLsVt3ZYpSw/edit |
| GUIDE 4 — Forma / Docs | https://docs.google.com/document/d/1wIWU0eg2OqCbDDZn-_REkZxCsuupvSlYEJmpMs4T3Ok/edit |
| GUIDE 5 — Forma Build / Build | https://docs.google.com/document/d/19Y5g9RUzr1zQT35VxrEqNSkfgDo-RqfM6pDGEvAjdlg/edit |
| GUIDE 6 — Forma Design Collaboration | https://docs.google.com/document/d/1uk5ZaP0-Oj4Zqx4A8_MfpgiKvVv0f-ySJu31_UlaNjc/edit |
| Superintendent + VDC Master Glossary (PDF) | https://drive.google.com/file/d/1sTth8Ik7mPKbv446pv51z_x3bHmYn9H0/view |
| Superintendent’s Whole-Building Component Glossary (PDF) | https://drive.google.com/file/d/1nVQC1YVOPnCOSYpwOxDoR32ECY8EZh8k/view |
| Superintendent VDC Glossary (PDF) | https://drive.google.com/file/d/1TDBrneOz7nwkbDhsDHJl9BhqX5EexLuT/view |
| `tiltup.pdf` | https://drive.google.com/file/d/1fwfKA4dcB7LojlKQo5QjMsF3Hc7JPvCW/view |
| `construction.md` (large construction knowledge dump) | https://drive.google.com/file/d/1B-dkbKg04aQGVPxKAw992VIxyrQtvGjo/view |

PDFs of several guides also exist beside the Docs (same titles).

## D. What to feed which swarm agent

| Swarm node | Prefer |
|---|---|
| 01 Daily PE | `_shared/*`, PE lanes, SharePoint job library |
| 02 Drafter | RFI/submittal/NCR rules in kit 02 knowledge |
| 04 / 10 Field QA | Kit checklists + concrete/tilt RAG modules |
| 12 Failure cards | Kit 12 markdown cards; RAG JSON for retrieval backends |
| 05 Trade shells | Intent map + handoff skill |
| Layout / VDC specialist (future child) | SitePrint SOP, total-station guides, layout RAG modules |
| Estimating (03) | Estimating doctrine knowledge only — no client price DBs |

## E. Not agent data (skip for swarm knowledge)

Demo fixtures, generated sample daily reports, live client cost databases, OSHA-filing tools, anything that would invent approvals, pour releases, or code rulings.
