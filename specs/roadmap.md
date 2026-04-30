# Development Roadmap

**Phase 0 — Foundation** ✓
Dev environment, Neo4j Desktop setup, API keys, `.env` structure

**Phase 1 — Data Exploration** ✓
Pull a configurable recent sample of the three core datasets (311 Service Requests `erm2-nwe9` filtered to `agency='HPD'`, Violations `wvxf-dwi5`, Registrations `tesw-yqqr`) via SODA; default window is last 6 months (controlled by a `LOOKBACK_MONTHS` env var so it can be extended without code changes); explore schemas, understand BBL coverage and join logic

**Phase 2 — Core Data Ingestion** ✓
Ingest and normalize the three core datasets, implement BBL resolution logic, validate joins across all three

**Phase 3 — Graph Schema Design** ✓
Define and document node types, relationship types, and cardinalities before building:
- `(Complaint) -[FILED_AGAINST]-> (Building/BBL)`
- `(Building) -[HAS_VIOLATION]-> (Violation)`
- `(Building) -[OWNED_BY]-> (Landlord)`
- `(Building) -[LOCATED_IN]-> (Neighborhood/NTA)`
- `(Complaint) -[HANDLED_BY]-> (Agency)`
- `(Violation) -[INSPECTED_BY]-> (Inspection)`

**Phase 4 — Graph Loading** ✓
Load nodes and relationships into Neo4j, validate with sample Cypher queries

**Phase 5 — Enrichment Data Ingestion** ✓
Pull DOB Safety Violations (`855j-jady`), integrate into the existing graph

**Phase 6 — ACRIS Ownership Ingestion** ✓
Pull ACRIS Deed Transfers (`636b-3b5g`); extract party names (buyers, sellers, LLC and corporate entities) and link them to Building nodes via BBL; enable ownership chain traversal across shell companies and related entities

**Phase 7 — Embeddings**
Identify text fields to embed, generate embeddings with `sentence-transformers`, attach to nodes

**Phase 8 — Vector Index**
Build Neo4j built-in vector index, test similarity queries

**Phase 9 — Neo4j MCP Server Integration**
Set up Neo4j's MCP server, connect Claude to the graph via MCP, validate basic graph queries

**Phase 10 — Query Router**
Classify incoming queries as graph traversal, vector search, web search, or hybrid

**Phase 11 — Cypher Generator**
LLM-assisted natural language → Cypher translation

**Phase 12 — Tavily Integration**
Add Tavily as a LangChain tool, test web search retrieval, make it available to the agent alongside graph and vector retrieval

**Phase 13 — DeepAgents**
Multi-step reasoning across graph, vector, and web search using LangChain DeepAgents

**Phase 14 — Answer Synthesis**
Claude integration to synthesize multi-source context into coherent answers

**Phase 15 — Streamlit UI**
Basic conversational interface wired to the agent

**Phase 16 — Polish & Demo**
Showcase queries, graph visualization, documentation
