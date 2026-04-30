# Phase 6 — ACRIS Ownership Ingestion: Requirements

## Objective

Pull NYC ACRIS Deed Transfer records and link them to existing Building nodes in Neo4j, enabling ownership chain traversal across LLCs, shell companies, and related entities.

## Source Datasets

Three ACRIS datasets joined on `document_id`:

| Dataset | ID | Used for |
|---|---|---|
| Real Property Master | `7isb-wh4c` | `doc_type` filter, document dates and amounts |
| Real Property Legals | `8h5j-fqxa` | BBL construction (`borough`, `block`, `lot`) |
| Real Property Parties | `636b-3b5g` | Buyer/seller party names (`party_type`, `name`) |

Filter to deed-type documents (any `doc_type` containing `DEED`).

## Graph Model Decision

**New `Owner` node** per unique party name, connected to `Building` via a relationship.

```
(Owner) -[:OWNS]-> (Building)
(Owner) -[:SOLD]-> (Building)
```

- `Owner` node properties: `name` (normalized), `entity_type` (INDIVIDUAL / LLC / CORPORATION / TRUST / etc.)
- Relationship properties on `OWNS` / `SOLD`: `document_id`, `recorded_datetime`, `document_date`, `party_type` (BUYER / SELLER)
- Normalization: strip punctuation, uppercase, collapse whitespace on party names before deduplication
- Each unique normalized name = one `Owner` node; multiple buildings link to the same node

## BBL Join Strategy

ACRIS Master records carry `lot`, `block`, and `borough` as separate fields. Construct BBL as:
```
BBL = LPAD(borough, 1) + LPAD(block, 5) + LPAD(lot, 4)
```
Match to `Building.bbl` (same format established in prior phases).

## Scope Constraints

- Filter to `party_type IN ('1', '2')` (buyer = 1, seller = 2) from the parties dataset
- Filter documents to deed categories only (exclude mortgages, liens, etc.)
- Apply the same `LOOKBACK_MONTHS` env var window used in prior phases for consistency, but note ACRIS goes back decades — consider fetching all records for buildings already in the graph (BBL-constrained pull) rather than a time-window pull
- Deduplicate `Owner` nodes by normalized name using `MERGE` in Cypher

## Out of Scope

- Mortgage and lien records (future enrichment)
- UCC filings
- Corporate registry cross-referencing (future phase)
- Beneficial ownership resolution (manual research layer, not automated here)
