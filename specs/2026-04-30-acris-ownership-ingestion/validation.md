# Phase 6 — ACRIS Ownership Ingestion: Validation

## Success Criteria

All of the following must pass before this branch is merged.

---

### 1. Owner Nodes Exist in the Graph

```cypher
MATCH (o:Owner) RETURN count(o) AS owner_count
```
- Expected: > 0 (non-trivial count proportional to Buildings in graph)

```cypher
MATCH (o:Owner) WHERE o.entity_type = 'LLC' RETURN count(o) AS llc_count
```
- Expected: LLC entities are present and classified correctly

---

### 2. Ownership Relationships Are Wired to Buildings

```cypher
MATCH (o:Owner)-[r:OWNS|SOLD]->(b:Building) RETURN count(r) AS rel_count
```
- Expected: Multiple relationships; each relationship has `document_id` and `recorded_datetime` set

```cypher
MATCH (o:Owner)-[:OWNS|SOLD]->(b:Building)
RETURN o.name, count(b) AS building_count
ORDER BY building_count DESC
LIMIT 10
```
- Expected: Top owners link to multiple buildings; LLC names appear in the list

---

### 3. Known Problem Landlord Test

During exploration (Task 1.5), identify a specific LLC or individual known to own multiple buildings in NYC (e.g., a landlord flagged in HPD data or press coverage). Then:

```cypher
MATCH (o:Owner {name: '<NORMALIZED_NAME>'})-[:OWNS]->(b:Building)
RETURN b.bbl, b.address
```
- Expected: Returns multiple Buildings matching the known portfolio

```cypher
MATCH (o:Owner)-[:OWNS]->(b:Building)-[:HAS_VIOLATION]->(v:Violation)
WHERE o.name = '<NORMALIZED_NAME>'
RETURN b.bbl, count(v) AS violation_count
ORDER BY violation_count DESC
```
- Expected: Cross-graph traversal works — violations reachable from an Owner through a Building

---

### 4. BBL Coverage

```cypher
MATCH (b:Building)
OPTIONAL MATCH (o:Owner)-[:OWNS]->(b)
WITH b, count(o) AS owner_links
RETURN
  count(b) AS total_buildings,
  sum(CASE WHEN owner_links > 0 THEN 1 ELSE 0 END) AS buildings_with_owners,
  round(100.0 * sum(CASE WHEN owner_links > 0 THEN 1 ELSE 0 END) / count(b), 1) AS pct_covered
```
- Expected: > 50% of Buildings have at least one Owner link (ACRIS doesn't cover all properties equally; document the actual number)

---

### 5. No Duplicate Owner Nodes

```cypher
MATCH (o:Owner)
WITH o.name AS name, count(*) AS cnt
WHERE cnt > 1
RETURN name, cnt
LIMIT 10
```
- Expected: Empty result (uniqueness constraint on normalized name enforces this)

---

## Definition of Done

- All 5 checks above pass or have documented explanations for gaps
- `validation-results.md` created with actual query output and counts
- `src/ingest/acris.py` and `src/graph/load_acris.py` exist with tests passing
- `specs/roadmap.md` updated to mark Phase 6 ✓
