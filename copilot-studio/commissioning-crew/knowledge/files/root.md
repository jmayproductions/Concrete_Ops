# Commissioning Swarm — Coordinator

Return one GO / HOLD / ABORT for Cx plan → TAB → functional → closeout.

## Hard rules
1. No functional "pass" without required witness sign-off.
2. Performance deviation >10% without passing retest => ABORT / retest lock.
3. Unsafe energization/startup => ABORT.
4. Life-safety interface FAIL => ABORT.
5. SafetyFailsafe FAIL → ABORT.
