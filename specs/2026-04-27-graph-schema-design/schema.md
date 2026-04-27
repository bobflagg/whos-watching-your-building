# Graph Schema Reference

Canonical schema for *Who's Watching Your Building?* — the target for Phase 4 loading.

---

## Node Types

### `Building`

The central hub node. One node per unique 10-digit BBL across all three source datasets.

| Property | Neo4j type | Source field | Source dataset | Nullable |
|---|---|---|---|---|
| `bbl` ★ | String | `bbl` (normalized) / derived from `boroid+block+lot` | All three | No |
| `borough` | String | `boro` | Registrations / Violations | Yes |
| `house_number` | String | `housenumber` | Registrations / Violations | Yes |
| `street_name` | String | `streetname` | Registrations / Violations | Yes |
| `zip` | String | `zip` | Registrations / Violations | Yes |
| `community_board` | String | `communityboard` | Registrations / Violations | Yes |
| `bin` | String | `bin` | Registrations / Violations | Yes |
| `block` | String | `block` | Registrations | Yes |
| `lot` | String | `lot` | Registrations | Yes |
| `ntacode` | String | `nta` | Violations | Yes |

★ Identity key — used in all MERGE statements.

**BBL construction:**
- Complaints / Violations: `normalize_bbl(bbl)` — strip, remove non-digits, zero-pad to 10 chars, reject if not 10 digits
- Registrations: `derive_bbl(df)` — `boroid.zfill(1) + block.zfill(5) + lot.zfill(4)`

---

### `Complaint`

One node per HPD complaint from the 311 Service Requests dataset.

| Property | Neo4j type | Source field | Nullable |
|---|---|---|---|
| `complaint_id` ★ | String | `unique_key` | No |
| `created_date` | String | `created_date` | No |
| `closed_date` | String | `closed_date` | Yes |
| `complaint_type` | String | `complaint_type` | Yes |
| `descriptor` | String | `descriptor` | Yes |
| `status` | String | `status` | Yes |
| `resolution_description` | String | `resolution_description` | Yes |
| `resolution_action_updated_date` | String | `resolution_action_updated_date` | Yes |
| `borough` | String | `borough` | Yes |
| `incident_address` | String | `incident_address` | Yes |
| `community_board` | String | `community_board` | Yes |
| `latitude` | Float | `latitude` | Yes |
| `longitude` | Float | `longitude` | Yes |
| `bbl` | String | `bbl` (normalized) | Yes |

**Dropped source fields:** `agency`, `agency_name` (captured via `HANDLED_BY` relationship), `location_type`, `address_type`, `street_name`, `city`, `incident_zip`, `x_coordinate_state_plane`, `y_coordinate_state_plane`, `open_data_channel_type`, `park_facility_name`, `park_borough`, `location`, `cross_street_1`, `cross_street_2`, `intersection_street_1`, `intersection_street_2`, `landmark`, `council_district`, `police_precinct`, `descriptor_2`.

---

### `Violation`

One node per HPD violation record.

| Property | Neo4j type | Source field | Nullable |
|---|---|---|---|
| `violation_id` ★ | String | `violationid` | No |
| `class` | String | `class` | Yes |
| `type` | String | `novtype` | Yes |
| `status` | String | `violationstatus` | Yes |
| `description` | String | `novdescription` | Yes |
| `order_number` | String | `ordernumber` | Yes |
| `nov_id` | String | `novid` | Yes |
| `nov_issued_date` | String | `novissueddate` | Yes |
| `current_status` | String | `currentstatus` | Yes |
| `current_status_date` | String | `currentstatusdate` | Yes |
| `rent_impairing` | String | `rentimpairing` | Yes |
| `apartment` | String | `apartment` | Yes |
| `story` | String | `story` | Yes |
| `certify_by_date` | String | `newcertifybydate` | Yes |
| `correct_by_date` | String | `newcorrectbydate` | Yes |
| `bbl` | String | `bbl` (normalized) | Yes |

> **Phase 4 loader fix required:** The existing loader (line 105) references `row.violationtype`, which does not exist in the SODA dataset. Replace with `row.novtype`.

**Dropped source fields:** `buildingid`, `registrationid`, `boroid`, `boro`, `housenumber`, `lowhousenumber`, `highhousenumber`, `streetname`, `streetcode`, `zip`, `block`, `lot`, `latitude`, `longitude`, `communityboard`, `councildistrict`, `censustract`, `bin`, `nta` (NTA is attached to Building), `inspectiondate`, `approveddate`, `certifieddate`, `originalcertifybydate`, `originalcorrectbydate` (inspection-event fields belong to `Inspection` node).

---

### `Landlord`

One node per HPD registration record. Name-based deduplication is deferred; each `registrationid` is a distinct node.

| Property | Neo4j type | Source field | Nullable |
|---|---|---|---|
| `registration_id` ★ | String | `registrationid` | No |
| `building_id` | String | `buildingid` | Yes |
| `last_registration_date` | String | `lastregistrationdate` | Yes |
| `registration_end_date` | String | `registrationenddate` | Yes |
| `bbl` | String | derived via `derive_bbl()` | Yes |

> **Note:** The fields `lifecyclestage`, `lastmodifieddate`, `ownerfirstname`, `ownerlastname`, and `ownertype` referenced in the existing loader (lines 137–141) do **not** exist in the `tesw-yqqr` SODA dataset as currently fetched. Remove them from the loader. Owner contact data may be available via a related HPD dataset (out of scope for Phase 3).

> **Phase 4 loader fix required:** Node label is currently `Registration` — rename to `Landlord`. Relationship is currently `REGISTERED_TO` — rename to `OWNED_BY`. Remove the 5 nonexistent fields from the Cypher SET clause.

---

### `Agency`

One node per agency code. Derived from 311 complaint records (currently only HPD).

| Property | Neo4j type | Source field | Nullable |
|---|---|---|---|
| `agency_code` ★ | String | `agency` | No |
| `agency_name` | String | `agency_name` | Yes |

---

### `Inspection`

One node per violation inspection event. Derived from the HPD Violations dataset; currently 1:1 with Violation. Modeled as a separate node to accommodate future DOB inspection data (Phase 5).

| Property | Neo4j type | Source field | Nullable |
|---|---|---|---|
| `inspection_id` ★ | String | `violationid` (same as violation, 1:1) | No |
| `inspection_date` | String | `inspectiondate` | Yes |
| `approved_date` | String | `approveddate` | Yes |
| `certified_date` | String | `certifieddate` | Yes |
| `original_certify_by_date` | String | `originalcertifybydate` | Yes |
| `original_correct_by_date` | String | `originalcorrectbydate` | Yes |

---

### `Neighborhood`

One node per NTA (Neighborhood Tabulation Area) code. Derived from the `nta` field in the Violations dataset.

| Property | Neo4j type | Source field | Nullable |
|---|---|---|---|
| `ntacode` ★ | String | `nta` | No |
| `borough` | String | `boro` | Yes |

---

## Relationship Types

All relationships carry no properties. All temporal and status data lives on nodes.

| Relationship | Start → End | Cardinality | Identity keys used |
|---|---|---|---|
| `FILED_AGAINST` | `Complaint → Building` | Many-to-one | `complaint_id` → `bbl` |
| `HAS_VIOLATION` | `Building → Violation` | One-to-many | `bbl` → `violation_id` |
| `OWNED_BY` | `Building → Landlord` | Many-to-one (per registration) | `bbl` → `registration_id` |
| `LOCATED_IN` | `Building → Neighborhood` | Many-to-one | `bbl` → `ntacode` |
| `HANDLED_BY` | `Complaint → Agency` | Many-to-one | `complaint_id` → `agency_code` |
| `INSPECTED_BY` | `Violation → Inspection` | One-to-one | `violation_id` → `inspection_id` |

> **Phase 4 loader fix required:** The existing loader writes `(Violation)-[FILED_AGAINST]->(Building)`. Rename to `HAS_VIOLATION` and reverse to `(Building)-[HAS_VIOLATION]->(Violation)`.

**Null handling for relationships:** Complaints and violations with a null or malformed BBL after normalization do not get a `FILED_AGAINST` / `HAS_VIOLATION` relationship. The complaint/violation node is still created; the relationship is skipped. (~0.3% of complaints, ~0.1% of violations are affected.)

---

## Constraints and Indexes

See `constraints_and_indexes.cypher` for the full DDL.

**Uniqueness constraints (one per node type):**

| Node | Constraint property |
|---|---|
| `Building` | `bbl` |
| `Complaint` | `complaint_id` |
| `Violation` | `violation_id` |
| `Landlord` | `registration_id` |
| `Agency` | `agency_code` |
| `Inspection` | `inspection_id` |
| `Neighborhood` | `ntacode` |

**Additional indexes (high-cardinality query fields):**

| Node | Property | Rationale |
|---|---|---|
| `Complaint` | `status` | Filter open vs. closed complaints |
| `Complaint` | `complaint_type` | Filter by complaint category |
| `Complaint` | `created_date` | Time-range queries |
| `Violation` | `status` | Filter open vs. closed violations |
| `Violation` | `class` | Filter by HPD violation class (A/B/C) |
| `Violation` | `current_status` | Filter by current enforcement status |
| `Landlord` | `registration_id` | Already covered by uniqueness constraint |
| `Building` | `zip` | Geographic filtering |
| `Building` | `community_board` | Geographic filtering |
