# Workflow: `level-closeout`

Gate order:
1. `qa-inspector`
2. `bolting`
3. `welding`
4. `plumb-alignment`
5. `coatings`
6. `fireproofing`
7. `crew-ops`

Parent assembles Decision from gates. SafetyFailsafe FAIL => ABORT.
