# Phase 4 — Graph Loading: Validation

Phase 4 is complete and ready to merge when all of the following checks pass in `notebooks/phase4_validation.py`.

---

## 1. Schema correctness

- All 7 uniqueness constraints are present (one per node label: Building, Complaint, Violation, Registration, Agency, Neighborhood, Inspection)
- No node with label `Registration` exists in the graph (renamed to `Registration`)
- No relationship of type `REGISTERED_TO` exists (renamed to `OWNED_BY`)
- No relationship of type `FILED_AGAINST` originates from a `Violation` node (direction was flipped)

---

## 2. Node counts (non-zero)

Each label must have at least one node:

| Label | Min expected |
|---|---|
| Building | > 0 |
| Complaint | > 0 |
| Violation | > 0 |
| Registration | > 0 |
| Agency | > 0 |
| Neighborhood | > 0 |
| Inspection | > 0 |

---

## 3. Relationship counts (non-zero)

Each relationship type must have at least one instance:

| Type | Direction | Min expected |
|---|---|---|
| FILED_AGAINST | (Complaint)→(Building) | > 0 |
| HAS_VIOLATION | (Building)→(Violation) | > 0 |
| OWNED_BY | (Registration)→(Building) | > 0 |
| LOCATED_IN | (Building)→(Neighborhood) | > 0 |
| HANDLED_BY | (Complaint)→(Agency) | > 0 |
| INSPECTED_BY | (Violation)→(Inspection) | > 0 |

---

## 4. BBL join coverage

- ≥ 80% of Complaint nodes have a `FILED_AGAINST` relationship to a Building node
- ≥ 80% of Violation nodes have an inbound `HAS_VIOLATION` relationship from a Building node

(Complaints or violations with unparseable BBLs are expected to be unlinked; 80% is a floor, not a target.)

---

## 5. Sample traversal

At least one successful round-trip traversal of the form:

```cypher
MATCH (b:Building {bbl: $bbl})
OPTIONAL MATCH (c:Complaint)-[:FILED_AGAINST]->(b)
OPTIONAL MATCH (b)-[:HAS_VIOLATION]->(v:Violation)
OPTIONAL MATCH (l:Registration)-[:OWNED_BY]->(b)
RETURN b, collect(c)[..3] AS complaints, collect(v)[..3] AS violations, collect(l)[..1] AS landlords
```

Returns a Building with at least one related Complaint or Violation.

---

## 6. Pipeline smoke test

- `src/pipeline.py` runs to completion without an unhandled exception
- No batch produces 0 rows written when the SODA fetch returned > 0 rows
