# Phase 6 — ACRIS Ownership Ingestion: Plan

## Task Group 1 — Exploration

1.1 Pull samples of ACRIS Real Property Master (`7isb-wh4c`), Legals (`8h5j-fqxa`), and Parties (`636b-3b5g`) via SODA; inspect schemas, field names, and data types  
1.2 Identify which `doc_type` values correspond to deed transfers; document the full list  
1.3 Construct BBL from borough/block/lot fields; spot-check a handful against Building nodes already in the graph  
1.4 Assess party name variation and normalization needs (punctuation, suffixes like LLC vs L.L.C., case)  
1.5 Identify a known multi-building landlord (by LLC name or owner name) present in the ACRIS data to use as a validation anchor  
1.6 Document findings in a `exploration-notes.md` in this directory

## Task Group 2 — ACRIS Ingestion Script

2.1 Create `src/ingest/acris.py`  
2.2 Implement `fetch_acris_deed_parties(bbls=None)` — pulls Master + Legals + Parties, joined on `document_id`, filtered to deed doc types and party types 1/2; constructs BBL from Legals borough/block/lot  
2.3 Implement `normalize_party_name(name: str) -> str` — strips punctuation, collapses whitespace, uppercases, handles common suffix variants (LLC, L.L.C., INC, etc.)  
2.4 Implement `infer_entity_type(name: str) -> str` — returns INDIVIDUAL, LLC, CORPORATION, TRUST, or OTHER based on suffix patterns  
2.5 If the dataset is large, implement BBL-constrained pull: only fetch records for BBLs already present in the graph  
2.6 Write unit tests for `normalize_party_name` and `infer_entity_type`

## Task Group 3 — Graph Loading

3.1 Create `src/graph/load_acris.py`  
3.2 Implement `load_owners(records)` — `MERGE` Owner nodes by normalized name, set `entity_type` property  
3.3 Implement `load_ownership_relationships(records)` — `MERGE` `OWNS` and `SOLD` relationships with document metadata as properties  
3.4 Add a `Building` constraint/index on `bbl` if not already present (it should be from Phase 4)  
3.5 Add a `Owner` constraint on `name` (normalized) for uniqueness  
3.6 Run the full load; log counts of nodes and relationships created vs merged

## Task Group 4 — Validation

4.1 Run Cypher to confirm Owner nodes exist and are linked to Buildings  
4.2 Execute the known-landlord validation query (from Task Group 1.5) — traverse from a known LLC to all Buildings it appears on  
4.3 Check for Buildings with no Owner link; compute coverage percentage  
4.4 Spot-check 3–5 individual BBLs in ACRIS web UI to confirm data accuracy  
4.5 Document results in `validation-results.md` in this directory
