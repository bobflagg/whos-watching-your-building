# Phase 4 — Graph Loading: Plan

## Task Group 1 — Fix loader bugs

Files to edit: `src/graph/loader.py`

1.1 Rename Registration node label to `Registration` in `load_registrations()`  
1.2 Rename relationship `REGISTERED_TO` to `OWNED_BY`, correct direction to `(Registration)-[:OWNED_BY]->(Building)`  
1.3 Flip violation relationship: replace `(Violation)-[:FILED_AGAINST]->(Building)` with `(Building)-[:HAS_VIOLATION]->(Violation)`  
1.4 Fix violation field name: replace `row.violationtype` with `row.novtype`  
1.5 Remove nonexistent fields from violation `SET` clause: `lifecyclestage`, `lastmodifieddate`, `ownerfirstname`, `ownerlastname`, `ownertype`  
1.6 Update `ensure_constraints()` to use `Registration` label (was `Registration`)

---

## Task Group 2 — Apply DDL

2.1 Run the constraints and indexes from `specs/2026-04-27-graph-schema-design/constraints_and_indexes.cypher` against the local Neo4j instance (idempotent — safe to re-run)

---

## Task Group 3 — Run the pipeline

3.1 Run `uv run python -m src.pipeline` against the local Neo4j instance with current env vars  
3.2 Monitor stdout for batch counts and any errors; capture output for the validation notebook  
3.3 If a constraint violation or field error surfaces, fix and re-run (wipe graph first with `MATCH (n) DETACH DELETE n` if needed for a clean retry)

---

## Task Group 4 — Write validation notebook

4.1 Create `notebooks/phase4_validation.py` as a marimo notebook  
4.2 Notebook should cover:
  - Node counts by label: Building, Complaint, Violation, Registration, Agency, Neighborhood, Inspection
  - Relationship counts by type: FILED_AGAINST, HAS_VIOLATION, OWNED_BY, LOCATED_IN, HANDLED_BY, INSPECTED_BY
  - BBL join coverage: % of Complaints with a connected Building node
  - BBL join coverage: % of Violations with a connected Building node
  - % of Buildings with at least one Registration (OWNED_BY)
  - Sample traversal: given a BBL, show its Complaints, Violations, and Registration
  - Constraint verification: confirm all 7 uniqueness constraints are present

---

## Task Group 5 — Merge

5.1 Confirm all validation checks pass  
5.2 Commit, open PR to main, merge
