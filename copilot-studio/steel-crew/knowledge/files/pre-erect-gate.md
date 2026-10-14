# Workflow: `pre-erect-gate`

Gate order:
1. `fab-mill`
2. `survey-anchors`
3. `crane-logistics`
4. `temp-bracing`
5. `crew-ops`
6. `weather-gate`
7. `safety-failsafe`
8. `qa-inspector`

Parent assembles Decision from gates. SafetyFailsafe FAIL => ABORT.
