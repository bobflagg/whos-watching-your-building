# Phase 2 — Core Data Ingestion: Validation

Phase 2 is complete and ready to merge when all of the following are true.

---

## 1. SODA pagination works

- Running the pipeline with `LOOKBACK_MONTHS=6` fetches **more than 500,000** 311 HPD complaints, confirming the row-cap is no longer a ceiling
- No duplicate complaint records (deduped by `complaint_id` before load)

## 2. BBL derivation is correct for registrations

- Every row in the loaded registrations dataset has a non-null `bbl`
- The derived BBL format matches the format used in 311 complaints and violations: exactly 10 characters, numeric, no whitespace
- At least one BBL from registrations can be found in both complaints and violations (confirming the join key is compatible)

## 3. Neo4j graph is populated

- `MATCH (b:Building) RETURN count(b)` returns a count > 0
- `MATCH (c:Complaint) RETURN count(c)` returns a count roughly equal to the number of normalized complaint rows
- `MATCH (v:Violation) RETURN count(v)` returns a count roughly equal to the number of normalized violation rows
- `MATCH (r:Registration) RETURN count(r)` returns a count roughly equal to the number of registration rows
- `MATCH ()-[r:FILED_AGAINST]->() RETURN count(r)` > 0
- `MATCH ()-[r:REGISTERED_TO]->() RETURN count(r)` > 0
- Uniqueness constraints exist on `Building.bbl`, `Complaint.complaint_id`, `Violation.violation_id`, `Registration.registration_id`

## 4. Pipeline is idempotent

- Running the pipeline a second time does not create duplicate nodes or relationships (MERGE semantics verified by re-running and confirming node counts are unchanged)

## 5. Validation notebook passes visual inspection

The `notebooks/phase2_validation.py` marimo notebook runs end-to-end without errors and shows:

- BBL null/drop rate ≤ 0.5% for complaints and violations (consistent with Phase 1 findings)
- BBL null/drop rate = 0% for registrations (all rows have derived BBL)
- At least 50% of complaint BBLs and violation BBLs have a matching registration (confirming ownership data is joinable)
- Neo4j node and relationship counts match pipeline summary output

## 6. Code quality

- `src/ingest/normalize.py` and `src/graph/loader.py` exist and are importable
- No hardcoded credentials; all connection details come from environment variables
- Pipeline runs cleanly via `uv run python -m src.pipeline`
