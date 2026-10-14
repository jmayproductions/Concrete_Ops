# Intent map (v2 router, stripped of runtime)

Use this to pick a topic / child agent. Source: `v2/services/orchestrator/src/modules/agent-router/router.ts`.

| Intent | Primary | Also consider |
|---|---|---|
| safety.incident_report | safety | superintendent |
| safety.hazard_identification | safety | qaqc |
| safety.ppe_requirements | safety | matching trade |
| safety.toolbox_talk | safety | matching trade |
| qaqc.defect_report | qaqc | safety, matching trade |
| qaqc.inspection_planning | qaqc | schedule |
| qaqc.spec_lookup | qaqc | Daily PE Copilot |
| qaqc.punch_list | qaqc | PE drafter punch topic |
| schedule.impact_analysis | schedule | PE drafter change event |
| schedule.lookahead | schedule | superintendent |
| weather / pour window | weather | concrete |
| pour / cure / mix | concrete | weather, qaqc |
| conduit / gear / energize | electrical | safety |
| erection / bolts / deck | steel | safety, schedule |
| rough-in / fixture / sleeve | plumbing | coordination / concrete embeds |
| crew / zone / blocker | superintendent | schedule |

Safety-critical “is it safe to…” stays BLOCKED. Route to a human.
