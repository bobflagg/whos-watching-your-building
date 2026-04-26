# Development Roadmap

**Phase 0 — Foundation** ✓
Dev environment, Neo4j Desktop setup, API keys, `.env` structure

**Phase 1 — Data Exploration**
Pull a configurable recent sample of the three core datasets (311 Service Requests `erm2-nwe9` filtered to `agency='HPD'`, Violations `wvxf-dwi5`, Registrations `tesw-yqqr`) via SODA; default window is last 6 months (controlled by a `LOOKBACK_MONTHS` env var so it can be extended without code changes); explore schemas, understand BBL coverage and join logic

**Phase 2 — Core Data Ingestion**
Ingest and normalize the three core datasets, implement BBL resolution logic, validate joins across all three

**Phase 3 — Graph Schema Design**
Define and document node types, relationship types, and cardinalities before building:
- `(Complaint) -[FILED_AGAINST]-> (Building/BBL)`
- `(Building) -[HAS_VIOLATION]-> (Violation)`
- `(Building) -[OWNED_BY]-> (Landlord)`
- `(Building) -[LOCATED_IN]-> (Neighborhood/NTA)`
- `(Complaint) -[HANDLED_BY]-> (Agency)`
- `(Violation) -[INSPECTED_BY]-> (Inspection)`

**Phase 4 — Graph Loading**
Load nodes and relationships into Neo4j, validate with sample Cypher queries

**Phase 5 — Enrichment Data Ingestion**
Pull DOB Violations (`3h2n-5cm9`), integrate into the existing graph

**Phase 6 — Embeddings**
Identify text fields to embed, generate embeddings with `sentence-transformers`, attach to nodes

**Phase 7 — Vector Index**
Build Neo4j built-in vector index, test similarity queries

**Phase 8 — Neo4j MCP Server Integration**
Set up Neo4j's MCP server, connect Claude to the graph via MCP, validate basic graph queries

**Phase 9 — Query Router**
Classify incoming queries as graph traversal, vector search, web search, or hybrid

**Phase 10 — Cypher Generator**
LLM-assisted natural language → Cypher translation

**Phase 11 — Tavily Integration**
Add Tavily as a LangChain tool, test web search retrieval, make it available to the agent alongside graph and vector retrieval

**Phase 12 — DeepAgents**
Multi-step reasoning across graph, vector, and web search using LangChain DeepAgents

**Phase 13 — Answer Synthesis**
Claude integration to synthesize multi-source context into coherent answers

**Phase 14 — Streamlit UI**
Basic conversational interface wired to the agent

**Phase 15 — Polish & Demo**
Showcase queries, graph visualization, documentation
