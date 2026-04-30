# Phase 5 — DOB Safety Violations: Validation

Phase 5 is complete and ready to merge when all of the following checks pass in `notebooks/phase5_validation.py`.

---

## 1. Schema correctness

- `DOBViolation` uniqueness constraint on `violation_number` is present in Neo4j
- No `DOBViolation` node exists without a `violation_number` property

---

## 2. Node and relationship counts (non-zero)

| Label / Type | Direction | Min expected |
|---|---|---|
| `DOBViolation` | — | > 0 |
| `HAS_DOB_VIOLATION` | `(Building)→(DOBViolation)` | > 0 |

---

## 3. BBL match rate

- ≥ 50% of `DOBViolation` nodes have an inbound `HAS_DOB_VIOLATION` relationship from a Building node

```cypher
MATCH (d:DOBViolation)
OPTIONAL MATCH (b:Building)-[:HAS_DOB_VIOLATION]->(d)
RETURN
  count(d) AS total,
  count(b) AS linked,
  round(100.0 * count(b) / count(d), 1) AS match_pct
```

> 50% is a floor, not a target. DOB NOW is a newer system and may not have BBLs on all historical records.

---

## 4. Cross-dataset coverage

At least one Building node exists with both an HPD violation and a DOB violation:

```cypher
MATCH (b:Building)-[:HAS_VIOLATION]->(:Violation)
MATCH (b)-[:HAS_DOB_VIOLATION]->(:DOBViolation)
RETURN count(DISTINCT b) AS buildings_with_both
```

Result must be > 0.

---

## 5. Sample traversal

At least one successful query of the form below returns a Building with DOB violations:

```cypher
MATCH (b:Building)-[:HAS_DOB_VIOLATION]->(d:DOBViolation)
RETURN b.bbl, d.violation_number, d.device_type, d.violation_status, d.violation_issue_date
LIMIT 5
```

---

## 6. Pipeline smoke test

- `src/pipeline.py` runs to completion without an unhandled exception
- The DOB fetch step returns > 0 rows
- The DOB BBL normalization drop count is logged and < 100% of fetched rows
- `load_dob_safety_violations()` reports > 0 nodes and > 0 relationships written
