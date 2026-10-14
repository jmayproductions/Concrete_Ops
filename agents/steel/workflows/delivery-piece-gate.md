# Workflow: `delivery-piece-gate`

Gate order:
1. `fab-mill`
2. `crane-logistics`
3. `weather-gate`
4. `safety-failsafe`

Parent assembles Decision from gates. SafetyFailsafe FAIL => ABORT.
