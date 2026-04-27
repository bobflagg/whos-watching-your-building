// ============================================================
// Who's Watching Your Building? — Graph Schema DDL
// Phase 3: Graph Schema Design
// Run against Neo4j Desktop (local dev) before Phase 4 loading.
// All statements are idempotent (IF NOT EXISTS).
// ============================================================

// ------------------------------------------------------------
// UNIQUENESS CONSTRAINTS (one per node type, on identity key)
// ------------------------------------------------------------

CREATE CONSTRAINT building_bbl_unique IF NOT EXISTS
  FOR (n:Building) REQUIRE n.bbl IS UNIQUE;

CREATE CONSTRAINT complaint_id_unique IF NOT EXISTS
  FOR (n:Complaint) REQUIRE n.complaint_id IS UNIQUE;

CREATE CONSTRAINT violation_id_unique IF NOT EXISTS
  FOR (n:Violation) REQUIRE n.violation_id IS UNIQUE;

CREATE CONSTRAINT landlord_registration_id_unique IF NOT EXISTS
  FOR (n:Landlord) REQUIRE n.registration_id IS UNIQUE;

CREATE CONSTRAINT agency_code_unique IF NOT EXISTS
  FOR (n:Agency) REQUIRE n.agency_code IS UNIQUE;

CREATE CONSTRAINT inspection_id_unique IF NOT EXISTS
  FOR (n:Inspection) REQUIRE n.inspection_id IS UNIQUE;

CREATE CONSTRAINT neighborhood_ntacode_unique IF NOT EXISTS
  FOR (n:Neighborhood) REQUIRE n.ntacode IS UNIQUE;


// ------------------------------------------------------------
// ADDITIONAL INDEXES (high-cardinality query fields)
// ------------------------------------------------------------

CREATE INDEX complaint_status IF NOT EXISTS
  FOR (n:Complaint) ON (n.status);

CREATE INDEX complaint_type IF NOT EXISTS
  FOR (n:Complaint) ON (n.complaint_type);

CREATE INDEX complaint_created_date IF NOT EXISTS
  FOR (n:Complaint) ON (n.created_date);

CREATE INDEX violation_status IF NOT EXISTS
  FOR (n:Violation) ON (n.status);

CREATE INDEX violation_class IF NOT EXISTS
  FOR (n:Violation) ON (n.class);

CREATE INDEX violation_current_status IF NOT EXISTS
  FOR (n:Violation) ON (n.current_status);

CREATE INDEX building_zip IF NOT EXISTS
  FOR (n:Building) ON (n.zip);

CREATE INDEX building_community_board IF NOT EXISTS
  FOR (n:Building) ON (n.community_board);
